"""Tests for magnetizer/builder.py — build orchestration"""

import json
import shutil
from pathlib import Path

import pytest
from PIL import Image as PILImage

from magnetizer.builder import build


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

TEMPLATE = (
    "<!DOCTYPE html><html><head><title>MAGNETIZER_TITLE</title></head>"
    "<body>MAGNETIZER_CONTENT</body></html>"
)
CONFIG = "site_title: Test Blog\nsite_url: https://example.github.io\nposts_per_page: 2\n"
MINIMAL_MD = "---\ndate: 2026-05-24\n---\n\nHello world\n"
TITLED_MD = "---\ndate: 2026-05-24\ntitle: My Post\n---\n\n# My Post\n\nContent here.\n"


def make_jpg(path, width=800, height=600):
    img = PILImage.new("RGB", (width, height), color=(100, 150, 200))
    img.save(path, "JPEG")


def make_project(tmp_path, posts=None, config=CONFIG):
    """Build a minimal valid project tree and return the project root."""
    (tmp_path / "content").mkdir()
    (tmp_path / "dist").mkdir()
    (tmp_path / "templates").mkdir()
    (tmp_path / "resources").mkdir()
    (tmp_path / "resources" / "style.css").write_text("body {}")
    (tmp_path / "templates" / "index.html").write_text(TEMPLATE)
    (tmp_path / "config.yaml").write_text(config)

    if posts:
        for post_id, md_text in posts.items():
            (tmp_path / "content" / f"{post_id}.md").write_text(md_text)

    return tmp_path


# ---------------------------------------------------------------------------
# Basic post generation
# ---------------------------------------------------------------------------

class TestBasicBuild:

    def test_post_html_file_created(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        build(p)
        assert (p / "dist" / "1.html").exists()

    def test_post_html_contains_post_body(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        build(p)
        assert "Hello world" in (p / "dist" / "1.html").read_text()

    def test_post_html_uses_template(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        build(p)
        html = (p / "dist" / "1.html").read_text()
        assert "<html>" in html
        assert "MAGNETIZER_CONTENT" not in html
        assert "MAGNETIZER_TITLE" not in html

    def test_post_html_title_is_site_title_when_no_post_title(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        build(p)
        assert "Test Blog" in (p / "dist" / "1.html").read_text()

    def test_post_html_title_is_post_title_dash_site_title(self, tmp_path):
        p = make_project(tmp_path, posts={1: TITLED_MD})
        build(p)
        assert "My Post - Test Blog" in (p / "dist" / "1.html").read_text()

    def test_multiple_posts_each_get_html_file(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD, 2: MINIMAL_MD})
        build(p)
        assert (p / "dist" / "1.html").exists()
        assert (p / "dist" / "2.html").exists()

    def test_manifest_written_after_build(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        build(p)
        assert (p / "manifest.json").exists()

    def test_manifest_contains_content_files(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        build(p)
        data = json.loads((p / "manifest.json").read_text())
        assert "1.md" in data


# ---------------------------------------------------------------------------
# Image processing
# ---------------------------------------------------------------------------

class TestImageProcessing:

    def test_resized_image_created_in_dist(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        make_jpg(p / "content" / "1-image-01.jpg", 2400, 1800)
        build(p)
        assert (p / "dist" / "1-image-01-resized.jpg").exists()

    def test_resized_image_long_edge_within_max(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD}, config="site_url: https://example.github.io\nimage_max_dimension: 1200\nposts_per_page: 12\n")
        make_jpg(p / "content" / "1-image-01.jpg", 2400, 1800)
        build(p)
        img = PILImage.open(p / "dist" / "1-image-01-resized.jpg")
        assert max(img.size) <= 1200

    def test_multiple_resized_images_all_created(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        make_jpg(p / "content" / "1-image-01.jpg")
        make_jpg(p / "content" / "1-image-02.jpg")
        build(p)
        assert (p / "dist" / "1-image-01-resized.jpg").exists()
        assert (p / "dist" / "1-image-02-resized.jpg").exists()

    def test_post_html_references_resized_image(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        make_jpg(p / "content" / "1-image-01.jpg")
        build(p)
        html = (p / "dist" / "1.html").read_text()
        assert "1-image-01-resized.jpg" in html


# ---------------------------------------------------------------------------
# Index pages
# ---------------------------------------------------------------------------

class TestIndexPages:

    def test_index_html_created(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        build(p)
        assert (p / "dist" / "index.html").exists()

    def test_index_html_contains_post(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        build(p)
        assert "Hello world" in (p / "dist" / "index.html").read_text()

    def test_index_page_title_is_site_title(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        build(p)
        html = (p / "dist" / "index.html").read_text()
        assert "<title>Test Blog</title>" in html

    def test_multiple_pages_created_when_posts_exceed_per_page(self, tmp_path):
        # posts_per_page=2 in CONFIG, so 3 posts → 2 index pages
        posts = {i: MINIMAL_MD for i in range(1, 4)}
        p = make_project(tmp_path, posts=posts)
        build(p)
        assert (p / "dist" / "index.html").exists()
        assert (p / "dist" / "index-2.html").exists()

    def test_second_index_page_title_includes_page_number(self, tmp_path):
        posts = {i: MINIMAL_MD for i in range(1, 4)}
        p = make_project(tmp_path, posts=posts)
        build(p)
        html = (p / "dist" / "index-2.html").read_text()
        assert "Test Blog - Page 2" in html

    def test_posts_in_reverse_chronological_order_on_index(self, tmp_path):
        # Higher post-id = newer, should appear first
        p = make_project(tmp_path, posts={1: MINIMAL_MD, 2: MINIMAL_MD, 3: MINIMAL_MD})
        build(p)
        html = (p / "dist" / "index.html").read_text()
        pos3 = html.index('id="post-3"')
        pos2 = html.index('id="post-2"')
        assert pos3 < pos2

    def test_post_page_back_link_points_to_correct_index_page(self, tmp_path):
        # posts_per_page=2: post 1 is on index-2.html, posts 2+3 on index.html
        posts = {i: MINIMAL_MD for i in range(1, 4)}
        p = make_project(tmp_path, posts=posts)
        build(p)
        html = (p / "dist" / "1.html").read_text()
        assert 'href="index-2.html#post-1"' in html

    def test_post_on_first_index_page_has_correct_back_link(self, tmp_path):
        posts = {i: MINIMAL_MD for i in range(1, 4)}
        p = make_project(tmp_path, posts=posts)
        build(p)
        html = (p / "dist" / "3.html").read_text()
        assert 'href="index.html#post-3"' in html


# ---------------------------------------------------------------------------
# Resources
# ---------------------------------------------------------------------------

class TestResources:

    def test_resources_copied_on_first_build(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        build(p)
        assert (p / "dist" / "resources" / "style.css").exists()

    def test_resources_not_copied_if_already_present(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        (p / "dist" / "resources").mkdir()
        sentinel = p / "dist" / "resources" / "existing.css"
        sentinel.write_text("existing")
        build(p)
        assert sentinel.exists()  # not overwritten

    def test_resources_replaced_with_resources_flag(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        (p / "dist" / "resources").mkdir()
        sentinel = p / "dist" / "resources" / "old.css"
        sentinel.write_text("old")
        build(p, resources=True)
        assert not sentinel.exists()
        assert (p / "dist" / "resources" / "style.css").exists()


# ---------------------------------------------------------------------------
# --flush
# ---------------------------------------------------------------------------

class TestFlush:

    def test_flush_clears_dist(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        stale = p / "dist" / "stale.html"
        stale.write_text("<html>old</html>")
        build(p, flush=True)
        assert not stale.exists()

    def test_flush_rebuilds_all_posts(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD, 2: MINIMAL_MD})
        build(p, flush=True)
        assert (p / "dist" / "1.html").exists()
        assert (p / "dist" / "2.html").exists()

    def test_flush_deletes_manifest_before_build(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        old_manifest = p / "manifest.json"
        old_manifest.write_text(json.dumps({"old.md": {"mtime": 0.0}}))
        build(p, flush=True)
        data = json.loads(old_manifest.read_text())
        assert "old.md" not in data

    def test_flush_copies_resources(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        build(p, flush=True)
        assert (p / "dist" / "resources" / "style.css").exists()

    def test_flush_preserves_git_directory(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        git_dir = p / "dist" / ".git"
        git_dir.mkdir()
        (git_dir / "config").write_text("[core]")
        build(p, flush=True)
        assert git_dir.exists()

    def test_flush_preserves_cname(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        cname = p / "dist" / "CNAME"
        cname.write_text("example.com")
        build(p, flush=True)
        assert cname.exists()

    def test_flush_preserves_nojekyll(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        nojekyll = p / "dist" / ".nojekyll"
        nojekyll.write_text("")
        build(p, flush=True)
        assert nojekyll.exists()


# ---------------------------------------------------------------------------
# Incremental build
# ---------------------------------------------------------------------------

class TestIncrementalBuild:

    def test_unchanged_post_html_not_regenerated(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD, 2: MINIMAL_MD})
        build(p)
        mtime_before = (p / "dist" / "1.html").stat().st_mtime

        # Touch only post 2
        import time; time.sleep(0.01)
        (p / "content" / "2.md").write_text(MINIMAL_MD)

        build(p)
        assert (p / "dist" / "1.html").stat().st_mtime == mtime_before

    def test_changed_post_html_is_regenerated(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD, 2: MINIMAL_MD})
        build(p)
        mtime_before = (p / "dist" / "2.html").stat().st_mtime

        import time; time.sleep(0.01)
        (p / "content" / "2.md").write_text("---\ndate: 2026-05-24\n---\n\nUpdated!\n")

        build(p)
        assert (p / "dist" / "2.html").stat().st_mtime > mtime_before

    def test_manifest_updated_after_incremental_build(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        build(p)

        import time; time.sleep(0.01)
        (p / "content" / "1.md").write_text("---\ndate: 2026-05-24\n---\n\nUpdated!\n")
        new_mtime = (p / "content" / "1.md").stat().st_mtime

        build(p)
        data = json.loads((p / "manifest.json").read_text())
        assert data["1.md"]["mtime"] == new_mtime


# ---------------------------------------------------------------------------
# Single-file (preview) build
# ---------------------------------------------------------------------------

class TestSingleFileBuild:

    def test_single_file_produces_its_html(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD, 2: MINIMAL_MD})
        build(p, filename="1.md")
        assert (p / "dist" / "1.html").exists()

    def test_single_file_does_not_build_other_posts(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD, 2: MINIMAL_MD})
        build(p, filename="1.md")
        assert not (p / "dist" / "2.html").exists()

    def test_single_file_does_not_create_index_pages(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        build(p, filename="1.md")
        assert not (p / "dist" / "index.html").exists()

    def test_single_file_does_not_write_manifest(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        build(p, filename="1.md")
        assert not (p / "manifest.json").exists()


# ---------------------------------------------------------------------------
# Build outcome
# ---------------------------------------------------------------------------

class TestBuildOutcome:

    def test_fresh_build_returns_created_count(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD, 2: MINIMAL_MD})
        result = build(p)
        assert result["created"] == 2

    def test_fresh_build_returns_zero_updated(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        result = build(p)
        assert result["updated"] == 0

    def test_fresh_build_returns_zero_deleted(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        result = build(p)
        assert result["deleted"] == 0

    def test_incremental_build_returns_updated_count(self, tmp_path):
        import time
        p = make_project(tmp_path, posts={1: MINIMAL_MD, 2: MINIMAL_MD})
        build(p)
        time.sleep(0.01)
        (p / "content" / "1.md").write_text("---\ndate: 2026-05-24\n---\n\nUpdated!\n")
        result = build(p)
        assert result["updated"] == 1

    def test_incremental_build_returns_zero_created_for_existing(self, tmp_path):
        import time
        p = make_project(tmp_path, posts={1: MINIMAL_MD, 2: MINIMAL_MD})
        build(p)
        time.sleep(0.01)
        (p / "content" / "1.md").write_text("---\ndate: 2026-05-24\n---\n\nUpdated!\n")
        result = build(p)
        assert result["created"] == 0

    def test_deleted_post_returns_deleted_count(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD, 2: MINIMAL_MD})
        build(p)
        (p / "content" / "1.md").unlink()
        result = build(p)
        assert result["deleted"] == 1

    def test_no_changes_returns_zero_for_all(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        build(p)
        result = build(p)
        assert result["created"] == 0
        assert result["updated"] == 0
        assert result["deleted"] == 0


# ---------------------------------------------------------------------------
# Feed generation
# ---------------------------------------------------------------------------

class TestFeed:

    def test_feed_xml_created_on_full_build(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        build(p)
        assert (p / "dist" / "feed.xml").exists()

    def test_feed_xml_not_created_on_single_file_build(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        build(p, filename="1.md")
        assert not (p / "dist" / "feed.xml").exists()

    def test_feed_xml_recreated_on_flush(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        build(p)
        (p / "dist" / "feed.xml").write_text("old content")
        build(p, flush=True)
        assert "old content" not in (p / "dist" / "feed.xml").read_text()


# ---------------------------------------------------------------------------
# Post navigation
# ---------------------------------------------------------------------------

class TestPostNavigation:

    def test_post_has_link_to_newer_post(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD, 2: MINIMAL_MD})
        build(p)
        assert "2.html" in (p / "dist" / "1.html").read_text()

    def test_post_has_link_to_older_post(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD, 2: MINIMAL_MD})
        build(p)
        assert "1.html" in (p / "dist" / "2.html").read_text()

    def test_newest_post_has_no_newer_link(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD, 2: MINIMAL_MD})
        build(p)
        assert "Newer post" not in (p / "dist" / "2.html").read_text()

    def test_oldest_post_has_no_older_link(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD, 2: MINIMAL_MD})
        build(p)
        assert "Older post" not in (p / "dist" / "1.html").read_text()

    def test_only_post_has_no_post_navigation(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        build(p)
        html = (p / "dist" / "1.html").read_text()
        assert "Newer post" not in html
        assert "Older post" not in html


# ---------------------------------------------------------------------------
# About page
# ---------------------------------------------------------------------------

ABOUT_MD = "---\ndate: 2026-05-24\ntitle: About\n---\n\nThis is the about page.\n"

class TestAboutPage:

    def test_about_html_created_when_about_md_exists(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        (p / "content" / "about.md").write_text(ABOUT_MD)
        build(p)
        assert (p / "dist" / "about.html").exists()

    def test_about_html_not_created_when_about_md_absent(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        build(p)
        assert not (p / "dist" / "about.html").exists()

    def test_about_html_contains_body_content(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        (p / "content" / "about.md").write_text(ABOUT_MD)
        build(p)
        assert "about page" in (p / "dist" / "about.html").read_text()

    def test_about_html_uses_template(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        (p / "content" / "about.md").write_text(ABOUT_MD)
        build(p)
        assert "<html>" in (p / "dist" / "about.html").read_text()

    def test_about_html_title_includes_post_title_and_site_title(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        (p / "content" / "about.md").write_text(ABOUT_MD)
        build(p)
        assert "About - Test Blog" in (p / "dist" / "about.html").read_text()

    def test_about_not_in_index(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        (p / "content" / "about.md").write_text(ABOUT_MD)
        build(p)
        assert "about.html" not in (p / "dist" / "index.html").read_text()

    def test_about_not_in_post_navigation(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD, 2: MINIMAL_MD})
        (p / "content" / "about.md").write_text(ABOUT_MD)
        build(p)
        assert "about.html" not in (p / "dist" / "1.html").read_text()
        assert "about.html" not in (p / "dist" / "2.html").read_text()

    def test_about_back_link_points_to_index(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        (p / "content" / "about.md").write_text(ABOUT_MD)
        build(p)
        assert 'href="index.html"' in (p / "dist" / "about.html").read_text()

    def test_about_back_link_has_no_anchor(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        (p / "content" / "about.md").write_text(ABOUT_MD)
        build(p)
        assert 'href="index.html#' not in (p / "dist" / "about.html").read_text()

    def test_single_file_build_about(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        (p / "content" / "about.md").write_text(ABOUT_MD)
        build(p, filename="about.md")
        assert (p / "dist" / "about.html").exists()

    def test_about_html_created_without_date(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        (p / "content" / "about.md").write_text("---\ntitle: About\n---\n\nNo date here.\n")
        build(p)
        assert (p / "dist" / "about.html").exists()

    def test_about_without_date_has_no_footer(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        (p / "content" / "about.md").write_text("---\ntitle: About\n---\n\nNo date here.\n")
        build(p)
        assert "<footer>" not in (p / "dist" / "about.html").read_text()

    def test_about_image_resized_and_copied(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        (p / "content" / "about.md").write_text(ABOUT_MD)
        make_jpg(p / "content" / "about-image-01.jpg")
        build(p)
        assert (p / "dist" / "about-image-01-resized.jpg").exists()


# ---------------------------------------------------------------------------
# Build ID placeholder
# ---------------------------------------------------------------------------

BUILD_ID_TEMPLATE = (
    "<!DOCTYPE html><html><head>"
    "<link rel=\"stylesheet\" href=\"style.css?v=MAGNETIZER_BUILD_ID\">"
    "<title>MAGNETIZER_TITLE</title></head>"
    "<body>MAGNETIZER_CONTENT</body></html>"
)


class TestBuildId:

    def test_build_id_placeholder_is_replaced(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        (p / "templates" / "index.html").write_text(BUILD_ID_TEMPLATE)
        build(p)
        assert "MAGNETIZER_BUILD_ID" not in (p / "dist" / "1.html").read_text()

    def test_build_id_is_numeric(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        (p / "templates" / "index.html").write_text(BUILD_ID_TEMPLATE)
        build(p)
        html = (p / "dist" / "1.html").read_text()
        import re
        m = re.search(r'style\.css\?v=(\S+)"', html)
        assert m and m.group(1).isdigit()

    def test_build_id_same_across_all_pages(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD, 2: MINIMAL_MD})
        (p / "templates" / "index.html").write_text(BUILD_ID_TEMPLATE)
        build(p)
        import re
        def get_build_id(path):
            m = re.search(r'style\.css\?v=(\d+)', path.read_text())
            return m.group(1) if m else None
        assert get_build_id(p / "dist" / "1.html") == get_build_id(p / "dist" / "index.html")


# ---------------------------------------------------------------------------
# Archive page
# ---------------------------------------------------------------------------

class TestArchivePage:

    def test_archive_html_created_after_build_with_changes(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        build(p)
        assert (p / "dist" / "archive.html").exists()

    def test_archive_html_not_created_on_single_file_build(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        build(p, filename="1.md")
        assert not (p / "dist" / "archive.html").exists()

    def test_archive_html_not_created_when_no_changes(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        build(p)
        (p / "dist" / "archive.html").unlink()
        build(p)  # no changes — archive should not be recreated
        assert not (p / "dist" / "archive.html").exists()

    def test_archive_contains_post_link(self, tmp_path):
        p = make_project(tmp_path, posts={1: TITLED_MD})
        build(p)
        assert "1.html" in (p / "dist" / "archive.html").read_text()

    def test_archive_title_includes_site_title(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        build(p)
        assert "Archive" in (p / "dist" / "archive.html").read_text()
