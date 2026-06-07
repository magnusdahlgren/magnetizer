"""CLI integration tests for build.py"""

import subprocess
import sys
from pathlib import Path

import pytest
from PIL import Image as PILImage

from conftest import MINIMAL_MD, make_project

BUILD_SCRIPT = Path(__file__).parent.parent / "build.py"


def run_build(args, cwd):
    return subprocess.run(
        [sys.executable, str(BUILD_SCRIPT)] + args,
        cwd=str(cwd),
        capture_output=True,
        text=True,
    )


# ---------------------------------------------------------------------------
# Help
# ---------------------------------------------------------------------------

class TestHelp:

    def test_help_exits_zero(self, tmp_path):
        assert run_build(["--help"], cwd=tmp_path).returncode == 0

    def test_help_output_mentions_build(self, tmp_path):
        result = run_build(["--help"], cwd=tmp_path)
        assert "build.py" in result.stdout or "usage" in result.stdout.lower()


# ---------------------------------------------------------------------------
# Validation errors surfaced through CLI
# ---------------------------------------------------------------------------

class TestCLIValidation:

    def test_exits_nonzero_when_content_missing(self, tmp_path):
        (tmp_path / "dist").mkdir()
        (tmp_path / "templates").mkdir()
        (tmp_path / "resources").mkdir()
        (tmp_path / "config.yaml").write_text("site_url: https://example.github.io\n")
        result = run_build([], cwd=tmp_path)
        assert result.returncode != 0

    def test_error_mentions_missing_directory(self, tmp_path):
        (tmp_path / "dist").mkdir()
        (tmp_path / "templates").mkdir()
        (tmp_path / "resources").mkdir()
        (tmp_path / "config.yaml").write_text("site_url: https://example.github.io\n")
        result = run_build([], cwd=tmp_path)
        assert "content" in result.stderr.lower()

    def test_exits_nonzero_when_content_has_no_md_files(self, tmp_path):
        make_project(tmp_path)  # content/ is empty
        result = run_build([], cwd=tmp_path)
        assert result.returncode != 0

    def test_filename_with_flush_is_rejected(self, tmp_path):
        make_project(tmp_path, posts={1: MINIMAL_MD})
        result = run_build(["1.md", "--flush"], cwd=tmp_path)
        assert result.returncode != 0

    def test_filename_with_resources_is_rejected(self, tmp_path):
        make_project(tmp_path, posts={1: MINIMAL_MD})
        result = run_build(["1.md", "--resources"], cwd=tmp_path)
        assert result.returncode != 0

    def test_filename_with_push_is_rejected(self, tmp_path):
        make_project(tmp_path, posts={1: MINIMAL_MD})
        result = run_build(["1.md", "--push"], cwd=tmp_path)
        assert result.returncode != 0


# ---------------------------------------------------------------------------
# Basic build
# ---------------------------------------------------------------------------

class TestCLIBasicBuild:

    def test_exits_zero_on_success(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        assert run_build([], cwd=p).returncode == 0

    def test_post_html_created(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        run_build([], cwd=p)
        assert (p / "dist" / "1.html").exists()

    def test_index_html_created(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        run_build([], cwd=p)
        assert (p / "dist" / "index.html").exists()

    def test_resources_copied(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        run_build([], cwd=p)
        assert (p / "dist" / "resources" / "style.css").exists()

    def test_manifest_written(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        run_build([], cwd=p)
        assert (p / "manifest.json").exists()


# ---------------------------------------------------------------------------
# --flush
# ---------------------------------------------------------------------------

class TestCLIFlush:

    def test_flush_removes_stale_dist_files(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        stale = p / "dist" / "stale.html"
        stale.write_text("<html>old</html>")
        run_build(["--flush"], cwd=p)
        assert not stale.exists()

    def test_flush_rebuilds_posts(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        run_build(["--flush"], cwd=p)
        assert (p / "dist" / "1.html").exists()


# ---------------------------------------------------------------------------
# --resources
# ---------------------------------------------------------------------------

class TestCLIResources:

    def test_resources_replaces_existing(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        (p / "dist" / "resources").mkdir()
        old = p / "dist" / "resources" / "old.css"
        old.write_text("old")
        run_build(["--resources"], cwd=p)
        assert not old.exists()
        assert (p / "dist" / "resources" / "style.css").exists()


# ---------------------------------------------------------------------------
# Single filename
# ---------------------------------------------------------------------------

class TestCLISingleFile:

    def test_single_file_creates_post_html(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD, 2: MINIMAL_MD})
        run_build(["1.md"], cwd=p)
        assert (p / "dist" / "1.html").exists()

    def test_single_file_does_not_create_other_post_html(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD, 2: MINIMAL_MD})
        run_build(["1.md"], cwd=p)
        assert not (p / "dist" / "2.html").exists()

    def test_single_file_does_not_create_index(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        run_build(["1.md"], cwd=p)
        assert not (p / "dist" / "index.html").exists()

    def test_single_file_does_not_write_manifest(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        run_build(["1.md"], cwd=p)
        assert not (p / "manifest.json").exists()


# ---------------------------------------------------------------------------
# Outcome summary
# ---------------------------------------------------------------------------

class TestCLIOutcome:

    def test_outcome_printed_on_fresh_build(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        result = run_build([], cwd=p)
        assert "1 post(s) created" in result.stdout

    def test_outcome_shows_all_three_counts(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        result = run_build([], cwd=p)
        assert "post(s) created" in result.stdout
        assert "post(s) updated" in result.stdout
        assert "post(s) deleted" in result.stdout

    def test_no_changes_message_when_nothing_changed(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        run_build([], cwd=p)
        result = run_build([], cwd=p)
        assert "No changes detected." in result.stdout

    def test_no_zero_counts_when_nothing_changed(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        run_build([], cwd=p)
        result = run_build([], cwd=p)
        assert "post(s)" not in result.stdout


# ---------------------------------------------------------------------------
# --verbose
# ---------------------------------------------------------------------------

class TestCLIVerbose:

    def test_verbose_shows_created_post(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        result = run_build(["--verbose"], cwd=p)
        assert "CREATED: 1.html" in result.stdout

    def test_verbose_shows_index_page(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        result = run_build(["--verbose"], cwd=p)
        assert "UPDATED: index.html" in result.stdout

    def test_verbose_shows_feed(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        result = run_build(["--verbose"], cwd=p)
        assert "UPDATED: feed.xml" in result.stdout

    def test_verbose_shows_resources(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        result = run_build(["--verbose"], cwd=p)
        assert "COPIED: resources/" in result.stdout

    def test_no_action_lines_without_verbose(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        result = run_build([], cwd=p)
        assert "CREATED:" not in result.stdout
        assert "UPDATED:" not in result.stdout

    def test_verbose_compatible_with_single_file(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD, 2: MINIMAL_MD})
        result = run_build(["1.md", "--verbose"], cwd=p)
        assert result.returncode == 0

    def test_verbose_resized_images_are_indented(self, tmp_path):
        from PIL import Image as PILImage
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        img = PILImage.new("RGB", (800, 600))
        img.save(p / "content" / "1-image-01.jpg", "JPEG")
        result = run_build(["--verbose"], cwd=p)
        assert "  RESIZED: 1-image-01-resized.jpg" in result.stdout

    def test_verbose_resized_shows_file_sizes(self, tmp_path):
        from PIL import Image as PILImage
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        img = PILImage.new("RGB", (800, 600))
        img.save(p / "content" / "1-image-01.jpg", "JPEG")
        result = run_build(["--verbose"], cwd=p)
        resized_line = next(line for line in result.stdout.splitlines() if "RESIZED: 1-image-01-resized.jpg" in line)
        assert "→" in resized_line

    def test_verbose_blank_line_between_post_and_site_entries(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        result = run_build(["--verbose"], cwd=p)
        created_pos = result.stdout.index("CREATED: 1.html")
        index_pos = result.stdout.index("UPDATED: index.html")
        assert "\n\n" in result.stdout[created_pos:index_pos]

    def test_verbose_shows_char_count_for_post(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        result = run_build(["--verbose"], cwd=p)
        assert "characters" in result.stdout

    def test_verbose_shows_micro_label_for_micro_post(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})  # "Hello world" — micro
        result = run_build(["--verbose"], cwd=p)
        assert "(micro)" in result.stdout

    def test_verbose_no_micro_label_for_regular_post(self, tmp_path):
        regular_md = "---\ndate: 2026-05-24\ntitle: My Post\n---\n\nNot micro.\n"
        p = make_project(tmp_path, posts={1: regular_md})
        result = run_build(["--verbose"], cwd=p)
        assert "(micro)" not in result.stdout

    def test_generating_line_has_arrow_prefix(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        result = run_build([], cwd=p)
        assert "→ Generating" in result.stdout


# ---------------------------------------------------------------------------
# Generating header and no-changes message
# ---------------------------------------------------------------------------

class TestCLIHeaderAndStatus:

    def test_generating_line_includes_site_title(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        result = run_build([], cwd=p)
        assert "Generating Test" in result.stdout

    def test_generating_line_includes_dist_path(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        result = run_build([], cwd=p)
        assert str(p / "dist") in result.stdout

    def test_generating_line_appears_before_summary(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        result = run_build([], cwd=p)
        assert result.stdout.index("Generating") < result.stdout.index("post(s)")

    def test_no_changes_message_shown_on_second_build(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        run_build([], cwd=p)
        result = run_build([], cwd=p)
        assert "No changes detected." in result.stdout

    def test_summary_counts_not_shown_when_no_changes(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        run_build([], cwd=p)
        result = run_build([], cwd=p)
        assert "post(s)" not in result.stdout

    def test_summary_counts_shown_when_changes_exist(self, tmp_path):
        p = make_project(tmp_path, posts={1: MINIMAL_MD})
        result = run_build([], cwd=p)
        assert "post(s)" in result.stdout
        assert "No changes detected." not in result.stdout
