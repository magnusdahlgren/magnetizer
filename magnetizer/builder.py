import re
import shutil
import time
from datetime import datetime as _datetime
from pathlib import Path

from magnetizer.config import load_config
from magnetizer.content import parse_post
from magnetizer.image import resize_image
from magnetizer.manifest import get_changed_post_ids, load_manifest, save_manifest
from magnetizer.render import (
    canonical_url,
    category_page_url,
    index_page_url,
    render_archive_page_content,
    render_category_page_content,
    render_index_page_content,
    render_page_title,
    render_post_page_content,
    render_template,
)
from magnetizer.feed import render_feed
from magnetizer.sitemap import render_sitemap, render_robots_txt
from magnetizer.validate import validate_config, validate_content, validate_project

_FLUSH_PRESERVE = {'.git', 'CNAME', '.nojekyll'}


def _lastmod(paths):
    mtimes = [p.stat().st_mtime for p in paths if p.exists()]
    if not mtimes:
        return None
    return _datetime.fromtimestamp(max(mtimes)).strftime('%Y-%m-%d')


def _post_ids_in_content(content_dir):
    ids = set()
    for f in content_dir.iterdir():
        m = re.match(r'^(\d+)', f.name)
        if m:
            ids.add(int(m.group(1)))
    return ids


def _image_filenames_for_post(content_dir, post_id):
    pattern = re.compile(rf'^{post_id}-image-\d{{2}}\.(jpg|jpeg|png)$')
    return sorted(
        f.name for f in content_dir.iterdir() if pattern.match(f.name)
    )


def _load_post(content_dir, post_id, micro_post_max_length=180):
    md_path = content_dir / f"{post_id}.md"
    md_text = md_path.read_text()
    images = _image_filenames_for_post(content_dir, post_id)
    return parse_post(md_text, post_id, images, micro_post_max_length)


def _delete_post_files(dist_dir, post_id):
    for f in list(dist_dir.iterdir()):
        if re.match(rf'^{post_id}[-.]', f.name):
            f.unlink()


def _build_post(post, dist_dir, content_dir, config):
    _delete_post_files(dist_dir, post.id)

    for image in post.images:
        stem, _, ext = image.filename.rpartition('.')
        resized_name = f"{stem}-resized.{ext}"
        resize_image(
            content_dir / image.filename,
            dist_dir / resized_name,
            max_dimension=config["image_max_dimension"],
            quality=config["image_quality"],
        )


def _neighbor_post_ids(post_id, all_post_ids_sorted_desc):
    if post_id in all_post_ids_sorted_desc:
        pos = all_post_ids_sorted_desc.index(post_id)
        neighbors = []
        if pos > 0:
            neighbors.append(all_post_ids_sorted_desc[pos - 1])
        if pos + 1 < len(all_post_ids_sorted_desc):
            neighbors.append(all_post_ids_sorted_desc[pos + 1])
        return neighbors
    else:
        # Deleted post: find neighbors by value in the remaining list
        newer = next((p for p in all_post_ids_sorted_desc if p > post_id), None)
        older = next((p for p in reversed(all_post_ids_sorted_desc) if p < post_id), None)
        return [p for p in [newer, older] if p is not None]


def _post_index_page_url(post_id, all_post_ids_sorted_desc, posts_per_page):
    pos = all_post_ids_sorted_desc.index(post_id)
    page = pos // posts_per_page + 1
    return index_page_url(page)


def _warn_if_missing_category(post, categories):
    if categories and not post.category:
        print(f"Warning: Post {post.id} is missing a category")


def _warn_if_invalid_category(post, categories):
    if categories and post.category and post.category not in categories:
        print(f"Warning: Post {post.id} has unknown category: '{post.category}'")


def _warn_if_missing_alt_texts(post):
    if post.images and any(not img.alt for img in post.images):
        print(f"Warning: Post {post.id} is missing one or more alt texts")


def _warn_if_missing_title(post):
    has_text = bool(post.body_html and post.body_html.strip())
    is_photo_only = bool(post.images) and not has_text
    if not post.is_micro and not is_photo_only and (has_text or post.images) and not post.title:
        print(f"Warning: Post {post.id} is missing a title")


def _adjacent_post_urls(post_id, all_post_ids_sorted_desc):
    pos = all_post_ids_sorted_desc.index(post_id)
    newer_url = f"{all_post_ids_sorted_desc[pos - 1]}.html" if pos > 0 else None
    older_url = f"{all_post_ids_sorted_desc[pos + 1]}.html" if pos + 1 < len(all_post_ids_sorted_desc) else None
    return newer_url, older_url


def _write_post_html(post, index_page_url, dist_dir, config, template, newer_url=None, older_url=None, categories=None):
    content_html = render_post_page_content(post, index_page_url, newer_url=newer_url, older_url=older_url, categories=categories)
    title = render_page_title(config["site_title"], post.title, page_num=None)
    html = render_template(template, title=title, content=content_html,
                           canonical=canonical_url(config["site_url"], f"{post.id}.html"))
    (dist_dir / f"{post.id}.html").write_text(html)


def _write_index_pages(posts_sorted_desc, dist_dir, config, template, categories=None):
    per_page = config["posts_per_page"]
    total = len(posts_sorted_desc)
    total_pages = max(1, (total + per_page - 1) // per_page)

    for page_num in range(1, total_pages + 1):
        slice_ = posts_sorted_desc[(page_num - 1) * per_page: page_num * per_page]
        content_html = render_index_page_content(slice_, page_num, total_pages, categories=categories)
        title = render_page_title(config["site_title"], None, page_num=page_num)
        filename = index_page_url(page_num)
        html = render_template(template, title=title, content=content_html,
                               canonical=canonical_url(config["site_url"], filename),
                               meta_description=config["index_meta_description"])
        (dist_dir / filename).write_text(html)


def _write_category_pages(posts_sorted_desc, dist_dir, config, template):
    categories = config["categories"]
    if not categories:
        return
    per_page = config["posts_per_page"]
    for slug, display_name in categories.items():
        category_posts = [p for p in posts_sorted_desc if p.category == slug]
        if not category_posts:
            continue
        total = len(category_posts)
        total_pages = max(1, (total + per_page - 1) // per_page)
        for page_num in range(1, total_pages + 1):
            slice_ = category_posts[(page_num - 1) * per_page: page_num * per_page]
            content_html = render_category_page_content(
                slice_, display_name, slug, page_num, total_pages, categories=categories
            )
            title = render_page_title(config["site_title"], display_name, page_num=None)
            filename = category_page_url(slug, page_num)
            html = render_template(template, title=title, content=content_html,
                                   canonical=canonical_url(config["site_url"], filename))
            (dist_dir / filename).write_text(html)


def _about_image_filenames(content_dir):
    pattern = re.compile(r'^about-image-\d{2}\.(jpg|jpeg|png)$')
    return sorted(f.name for f in content_dir.iterdir() if pattern.match(f.name))


def _build_cookies_page(content_dir, dist_dir, config, template):
    md_text = (content_dir / "cookies.md").read_text()
    post = parse_post(md_text, "cookies", [])
    content_html = render_post_page_content(post, "index.html", back_url="index.html")
    title = render_page_title(config["site_title"], post.title, page_num=None)
    html = render_template(template, title=title, content=content_html,
                           canonical=canonical_url(config["site_url"], "cookies.html"))
    (dist_dir / "cookies.html").write_text(html)


def _build_about_page(content_dir, dist_dir, config, template):
    md_text = (content_dir / "about.md").read_text()
    images = _about_image_filenames(content_dir)
    post = parse_post(md_text, "about", images)

    for image in post.images:
        stem, _, ext = image.filename.rpartition('.')
        resize_image(
            content_dir / image.filename,
            dist_dir / f"{stem}-resized.{ext}",
            max_dimension=config["image_max_dimension"],
            quality=config["image_quality"],
        )

    content_html = render_post_page_content(post, "index.html", back_url="index.html")
    title = render_page_title(config["site_title"], post.title, page_num=None)
    html = render_template(template, title=title, content=content_html,
                           canonical=canonical_url(config["site_url"], "about.html"))
    (dist_dir / "about.html").write_text(html)


def _special_page_changed(content_dir, manifest, md_name, image_pattern=None):
    relevant = {md_name}
    if image_pattern:
        pattern = re.compile(image_pattern)
        for f in content_dir.iterdir():
            if pattern.match(f.name):
                relevant.add(f.name)
        for name in manifest:
            if pattern.match(name):
                relevant.add(name)
    for name in relevant:
        f = content_dir / name
        if f.exists():
            if name not in manifest or manifest[name]["mtime"] != f.stat().st_mtime:
                return True
        elif name in manifest:
            return True
    return False


def _copy_resources(resources_dir, dist_dir, replace=False):
    dest = dist_dir / "resources"
    if replace and dest.exists():
        shutil.rmtree(dest)
    if not dest.exists():
        shutil.copytree(resources_dir, dest)
        return True
    return False


def build(cwd, filename=None, flush=False, resources=False):
    cwd = Path(cwd)
    content_dir = cwd / "content"
    dist_dir = cwd / "dist"
    manifest_path = cwd / "manifest.json"

    validate_project(cwd)
    validate_content(content_dir)

    config = load_config(cwd / "config.yaml")
    validate_config(config)
    template = (cwd / "templates" / "index.html").read_text().replace(
        'MAGNETIZER_BUILD_ID', str(int(time.time()))
    )

    if flush:
        for item in dist_dir.iterdir():
            if item.name in _FLUSH_PRESERVE:
                continue
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
        if manifest_path.exists():
            manifest_path.unlink()

    manifest = load_manifest(manifest_path)
    log = []

    about_md = content_dir / "about.md"
    cookies_md = content_dir / "cookies.md"

    post_ids_to_build: set[int] = set()

    if filename:
        stem = Path(filename).stem
        if stem == "about":
            if about_md.exists():
                _build_about_page(content_dir, dist_dir, config, template)
                log.append(("UPDATED", "about.html"))
            return {"created": 0, "updated": 0, "deleted": 0, "log": log}
        if stem == "cookies":
            if cookies_md.exists():
                _build_cookies_page(content_dir, dist_dir, config, template)
                log.append(("UPDATED", "cookies.html"))
            return {"created": 0, "updated": 0, "deleted": 0, "log": log}
        post_id = int(Path(filename).stem)
        changed_post_ids = {post_id}
        post_ids_to_build = {post_id}
    else:
        changed_post_ids = get_changed_post_ids(content_dir, manifest)

    all_post_ids_sorted_desc = sorted(_post_ids_in_content(content_dir), reverse=True)

    if not filename:
        neighbor_ids = {
            n
            for pid in changed_post_ids
            for n in _neighbor_post_ids(pid, all_post_ids_sorted_desc)
        }
        post_ids_to_build = changed_post_ids | neighbor_ids

    created = updated = deleted = 0
    posts_cache = {}

    for post_id in post_ids_to_build:
        md_path = content_dir / f"{post_id}.md"
        if not md_path.exists():
            if post_id in changed_post_ids:
                _delete_post_files(dist_dir, post_id)
                deleted += 1
                log.append(("REMOVED", f"{post_id}.html"))
            continue

        action = "UPDATED" if f"{post_id}.md" in manifest else "CREATED"
        if post_id in changed_post_ids:
            if action == "UPDATED":
                updated += 1
            else:
                created += 1

        post = _load_post(content_dir, post_id, config["micro_post_max_length"])
        posts_cache[post_id] = post
        _warn_if_missing_alt_texts(post)
        _warn_if_missing_title(post)
        _warn_if_missing_category(post, config["categories"])
        _warn_if_invalid_category(post, config["categories"])
        src_sizes = {img.filename: (content_dir / img.filename).stat().st_size for img in post.images}
        _build_post(post, dist_dir, content_dir, config)
        for image in post.images:
            stem, _, ext = image.filename.rpartition('.')
            resized_name = f"{stem}-resized.{ext}"
            dest_size = (dist_dir / resized_name).stat().st_size
            log.append(("RESIZED", resized_name, src_sizes[image.filename], dest_size))
        idx_url = _post_index_page_url(post_id, all_post_ids_sorted_desc, config["posts_per_page"])
        newer_url, older_url = _adjacent_post_urls(post_id, all_post_ids_sorted_desc)
        _write_post_html(post, idx_url, dist_dir, config, template, newer_url=newer_url, older_url=older_url, categories=config["categories"])
        log.append((action, f"{post_id}.html", post.char_count, post.is_micro))

    if about_md.exists():
        if filename or _special_page_changed(content_dir, manifest, "about.md", r'^about-image-\d{2}\.(jpg|jpeg|png)$'):
            _build_about_page(content_dir, dist_dir, config, template)
            log.append(("UPDATED", "about.html"))
    elif not filename:
        about_html = dist_dir / "about.html"
        if about_html.exists():
            about_html.unlink()
            log.append(("REMOVED", "about.html"))

    if cookies_md.exists():
        if filename or _special_page_changed(content_dir, manifest, "cookies.md"):
            _build_cookies_page(content_dir, dist_dir, config, template)
            log.append(("UPDATED", "cookies.html"))
    elif not filename:
        cookies_html = dist_dir / "cookies.html"
        if cookies_html.exists():
            cookies_html.unlink()
            log.append(("REMOVED", "cookies.html"))

    if not filename and post_ids_to_build:
        all_posts = [
            posts_cache[pid] if pid in posts_cache else _load_post(content_dir, pid, config["micro_post_max_length"])
            for pid in all_post_ids_sorted_desc
        ]
        _write_index_pages(all_posts, dist_dir, config, template, categories=config["categories"])
        per_page = config["posts_per_page"]
        total_pages = max(1, (len(all_posts) + per_page - 1) // per_page)
        for page_num in range(1, total_pages + 1):
            log.append(("UPDATED", index_page_url(page_num)))
        _write_category_pages(all_posts, dist_dir, config, template)
        (dist_dir / "feed.xml").write_text(render_feed(all_posts, config))
        log.append(("UPDATED", "feed.xml"))
        archive_html = render_template(
            template,
            title=render_page_title(config["site_title"], "Archive", page_num=None),
            content=render_archive_page_content(all_posts, categories=config["categories"]),
            canonical=canonical_url(config["site_url"], "archive.html"),
        )
        (dist_dir / "archive.html").write_text(archive_html)
        log.append(("UPDATED", "archive.html"))
        save_manifest(content_dir, manifest_path)

    if not filename and log:
        per_page = config["posts_per_page"]
        total_pages = max(1, (len(all_post_ids_sorted_desc) + per_page - 1) // per_page)
        index_lastmod = _lastmod([content_dir / f"{pid}.md" for pid in all_post_ids_sorted_desc])
        sitemap_pages = []
        for pid in all_post_ids_sorted_desc:
            post_files = [content_dir / f"{pid}.md"] + [
                f for f in content_dir.iterdir() if re.match(rf'^{pid}-image-', f.name)
            ]
            sitemap_pages.append((f"{pid}.html", _lastmod(post_files)))
        for page_num in range(1, total_pages + 1):
            sitemap_pages.append((index_page_url(page_num), index_lastmod))
        if about_md.exists():
            about_files = [content_dir / "about.md"] + [
                f for f in content_dir.iterdir() if re.match(r'^about-image-', f.name)
            ]
            sitemap_pages.append(("about.html", _lastmod(about_files)))
        sitemap_pages.append(("archive.html", index_lastmod))
        (dist_dir / "sitemap.xml").write_text(render_sitemap(sitemap_pages, config))
        log.append(("UPDATED", "sitemap.xml"))
        (dist_dir / "robots.txt").write_text(render_robots_txt(config))
        log.append(("UPDATED", "robots.txt"))

    if _copy_resources(cwd / "resources", dist_dir, replace=resources or flush):
        log.append(("COPIED", "resources/"))

    return {"created": created, "updated": updated, "deleted": deleted, "log": log}
