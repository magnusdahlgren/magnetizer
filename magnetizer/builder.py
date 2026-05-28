import re
import shutil
from pathlib import Path

from magnetizer.config import load_config
from magnetizer.content import parse_post
from magnetizer.image import resize_image
from magnetizer.manifest import get_changed_post_ids, load_manifest, save_manifest
from magnetizer.render import (
    index_page_url,
    render_index_page_content,
    render_page_title,
    render_post_page_content,
    render_template,
)
from magnetizer.validate import validate_content, validate_project

_FLUSH_PRESERVE = {'.git', 'CNAME', '.nojekyll'}


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


def _load_post(content_dir, post_id):
    md_path = content_dir / f"{post_id}.md"
    md_text = md_path.read_text()
    images = _image_filenames_for_post(content_dir, post_id)
    return parse_post(md_text, post_id, images)


def _delete_post_files(dist_dir, post_id):
    for f in list(dist_dir.iterdir()):
        if re.match(rf'^{post_id}[-.]', f.name):
            f.unlink()


def _build_post(post, dist_dir, content_dir, config):
    _delete_post_files(dist_dir, post.id)

    for img_name in post.images:
        stem, dot, ext = img_name.rpartition('.')
        resized_name = f"{stem}-resized.{ext}"
        resize_image(
            content_dir / img_name,
            dist_dir / resized_name,
            max_dimension=config["image_max_dimension"],
            quality=config["image_quality"],
        )

    return post


def _post_index_page_url(post_id, all_post_ids_sorted_desc, posts_per_page):
    pos = all_post_ids_sorted_desc.index(post_id)
    page = pos // posts_per_page + 1
    return index_page_url(page)


def _write_post_html(post, index_page_url, dist_dir, config, template):
    content_html = render_post_page_content(post, index_page_url)
    title = render_page_title(config["site_title"], post.title, page_num=None)
    html = render_template(template, title=title, content=content_html)
    (dist_dir / f"{post.id}.html").write_text(html)


def _write_index_pages(posts_sorted_desc, dist_dir, config, template):
    per_page = config["posts_per_page"]
    total = len(posts_sorted_desc)
    total_pages = max(1, (total + per_page - 1) // per_page)

    for page_num in range(1, total_pages + 1):
        slice_ = posts_sorted_desc[(page_num - 1) * per_page: page_num * per_page]
        content_html = render_index_page_content(slice_, page_num, total_pages)
        title = render_page_title(config["site_title"], None, page_num=page_num)
        html = render_template(template, title=title, content=content_html)
        filename = index_page_url(page_num)
        (dist_dir / filename).write_text(html)


def _copy_resources(resources_dir, dist_dir, replace=False):
    dest = dist_dir / "resources"
    if replace and dest.exists():
        shutil.rmtree(dest)
    if not dest.exists():
        shutil.copytree(resources_dir, dest)


def build(cwd, filename=None, flush=False, resources=False):
    cwd = Path(cwd)
    content_dir = cwd / "content"
    dist_dir = cwd / "dist"
    manifest_path = cwd / "manifest.json"

    validate_project(cwd)
    validate_content(content_dir)

    config = load_config(cwd / "config.yaml")
    template = (cwd / "templates" / "index.html").read_text()

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

    if filename:
        post_id = int(Path(filename).stem)
        post_ids_to_build = {post_id}
    else:
        post_ids_to_build = get_changed_post_ids(content_dir, manifest)

    all_post_ids_sorted_desc = sorted(_post_ids_in_content(content_dir), reverse=True)

    created = updated = deleted = 0

    for post_id in post_ids_to_build:
        md_path = content_dir / f"{post_id}.md"
        if not md_path.exists():
            _delete_post_files(dist_dir, post_id)
            deleted += 1
            continue

        if f"{post_id}.md" in manifest:
            updated += 1
        else:
            created += 1

        post = _load_post(content_dir, post_id)
        _build_post(post, dist_dir, content_dir, config)
        idx_url = _post_index_page_url(post_id, all_post_ids_sorted_desc, config["posts_per_page"])
        _write_post_html(post, idx_url, dist_dir, config, template)

    if not filename and post_ids_to_build:
        all_posts = [_load_post(content_dir, pid) for pid in all_post_ids_sorted_desc]
        _write_index_pages(all_posts, dist_dir, config, template)
        save_manifest(content_dir, manifest_path)

    _copy_resources(cwd / "resources", dist_dir, replace=resources or flush)

    return {"created": created, "updated": updated, "deleted": deleted}
