"""Tests for magnetizer/validate.py — validate_project(), validate_content(), validate_config()"""

import pytest
from magnetizer.validate import validate_config, validate_content, validate_project


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_project(tmp_path, missing=None):
    """Create a minimal valid project structure, optionally omitting one item."""
    dirs = ["content", "dist", "templates", "resources"]
    for d in dirs:
        if d != missing:
            (tmp_path / d).mkdir()
    if missing != "config.yaml":
        (tmp_path / "config.yaml").write_text("site_title: Test\n")
    if missing != "templates/index.html" and "templates" not in (missing or ""):
        (tmp_path / "templates" / "index.html").write_text("<html>MAGNETIZER_TITLE MAGNETIZER_CONTENT</html>")
    return tmp_path


def make_content(tmp_path, files):
    """Write files into a content/ directory and return its path."""
    content = tmp_path / "content"
    content.mkdir(exist_ok=True)
    for name, body in files.items():
        (content / name).write_bytes(body if isinstance(body, bytes) else body.encode())
    return content


MINIMAL_MD = b"---\ndate: 2026-01-01\n---\n"
MINIMAL_IMG = b"\xff\xd8\xff"


# ---------------------------------------------------------------------------
# validate_project — required items present
# ---------------------------------------------------------------------------

class TestValidateProject:

    def test_passes_when_all_present(self, tmp_path):
        validate_project(make_project(tmp_path))  # should not raise

    def test_fails_when_content_missing(self, tmp_path):
        with pytest.raises(SystemExit):
            validate_project(make_project(tmp_path, missing="content"))

    def test_fails_when_dist_missing(self, tmp_path):
        with pytest.raises(SystemExit):
            validate_project(make_project(tmp_path, missing="dist"))

    def test_fails_when_templates_missing(self, tmp_path):
        with pytest.raises(SystemExit):
            validate_project(make_project(tmp_path, missing="templates"))

    def test_fails_when_resources_missing(self, tmp_path):
        with pytest.raises(SystemExit):
            validate_project(make_project(tmp_path, missing="resources"))

    def test_fails_when_config_yaml_missing(self, tmp_path):
        with pytest.raises(SystemExit):
            validate_project(make_project(tmp_path, missing="config.yaml"))

    def test_error_message_names_missing_item(self, tmp_path, capsys):
        with pytest.raises(SystemExit):
            validate_project(make_project(tmp_path, missing="dist"))
        assert "dist" in capsys.readouterr().err

    def test_config_must_be_a_file_not_directory(self, tmp_path):
        make_project(tmp_path)
        (tmp_path / "config.yaml").unlink()
        (tmp_path / "config.yaml").mkdir()
        with pytest.raises(SystemExit):
            validate_project(tmp_path)

    def test_fails_when_templates_index_html_missing(self, tmp_path):
        make_project(tmp_path, missing="templates/index.html")
        with pytest.raises(SystemExit):
            validate_project(tmp_path)

    def test_error_message_mentions_template_file(self, tmp_path, capsys):
        make_project(tmp_path, missing="templates/index.html")
        with pytest.raises(SystemExit):
            validate_project(tmp_path)
        assert "index.html" in capsys.readouterr().err

    def test_passes_when_templates_index_html_present(self, tmp_path):
        make_project(tmp_path)
        validate_project(tmp_path)  # should not raise


# ---------------------------------------------------------------------------
# validate_content — valid content
# ---------------------------------------------------------------------------

class TestValidateContentValid:

    def test_passes_with_single_md_file(self, tmp_path):
        content = make_content(tmp_path, {"1.md": MINIMAL_MD})
        validate_content(content)  # should not raise

    def test_passes_with_md_and_image(self, tmp_path):
        content = make_content(tmp_path, {
            "1.md": MINIMAL_MD,
            "1-image-01.jpg": MINIMAL_IMG,
        })
        validate_content(content)

    def test_passes_with_multiple_posts_and_images(self, tmp_path):
        content = make_content(tmp_path, {
            "1.md": MINIMAL_MD,
            "1-image-01.jpg": MINIMAL_IMG,
            "1-image-02.png": MINIMAL_IMG,
            "2.md": MINIMAL_MD,
            "3.md": MINIMAL_MD,
            "3-image-01.jpeg": MINIMAL_IMG,
        })
        validate_content(content)

    def test_passes_with_jpeg_extension(self, tmp_path):
        content = make_content(tmp_path, {
            "1.md": MINIMAL_MD,
            "1-image-01.jpeg": MINIMAL_IMG,
        })
        validate_content(content)

    def test_passes_with_png_extension(self, tmp_path):
        content = make_content(tmp_path, {
            "1.md": MINIMAL_MD,
            "1-image-01.png": MINIMAL_IMG,
        })
        validate_content(content)

    def test_passes_with_high_post_ids(self, tmp_path):
        content = make_content(tmp_path, {"999.md": MINIMAL_MD})
        validate_content(content)


# ---------------------------------------------------------------------------
# validate_content — no markdown files
# ---------------------------------------------------------------------------

class TestValidateContentNoMarkdown:

    def test_fails_when_content_is_empty(self, tmp_path):
        content = tmp_path / "content"
        content.mkdir()
        with pytest.raises(SystemExit):
            validate_content(content)

    def test_error_message_for_empty_content(self, tmp_path, capsys):
        content = tmp_path / "content"
        content.mkdir()
        with pytest.raises(SystemExit):
            validate_content(content)
        assert "content" in capsys.readouterr().err.lower()


# ---------------------------------------------------------------------------
# validate_content — invalid .md filenames
# ---------------------------------------------------------------------------

class TestValidateContentMdFilenames:

    def test_fails_for_non_integer_md_name(self, tmp_path):
        content = make_content(tmp_path, {"foo.md": MINIMAL_MD})
        with pytest.raises(SystemExit):
            validate_content(content)

    def test_fails_for_zero_padded_post_id(self, tmp_path):
        content = make_content(tmp_path, {"01.md": MINIMAL_MD})
        with pytest.raises(SystemExit):
            validate_content(content)

    def test_error_message_names_invalid_file(self, tmp_path, capsys):
        content = make_content(tmp_path, {"foo.md": MINIMAL_MD})
        with pytest.raises(SystemExit):
            validate_content(content)
        assert "foo.md" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# validate_content — invalid image filenames
# ---------------------------------------------------------------------------

class TestValidateContentImageFilenames:

    def test_fails_for_image_with_single_digit_number(self, tmp_path):
        content = make_content(tmp_path, {
            "1.md": MINIMAL_MD,
            "1-image-1.jpg": MINIMAL_IMG,
        })
        with pytest.raises(SystemExit):
            validate_content(content)

    def test_fails_for_image_with_unsupported_extension(self, tmp_path):
        content = make_content(tmp_path, {
            "1.md": MINIMAL_MD,
            "1-image-01.gif": MINIMAL_IMG,
        })
        with pytest.raises(SystemExit):
            validate_content(content)

    def test_fails_for_image_with_zero_padded_post_id(self, tmp_path):
        content = make_content(tmp_path, {
            "1.md": MINIMAL_MD,
            "01-image-01.jpg": MINIMAL_IMG,
        })
        with pytest.raises(SystemExit):
            validate_content(content)

    def test_error_message_names_invalid_image_file(self, tmp_path, capsys):
        content = make_content(tmp_path, {
            "1.md": MINIMAL_MD,
            "1-image-01.gif": MINIMAL_IMG,
        })
        with pytest.raises(SystemExit):
            validate_content(content)
        assert "1-image-01.gif" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# validate_content — orphan images
# ---------------------------------------------------------------------------

class TestValidateContentOrphanImages:

    def test_fails_when_image_has_no_matching_md(self, tmp_path):
        content = make_content(tmp_path, {
            "1.md": MINIMAL_MD,
            "2-image-01.jpg": MINIMAL_IMG,  # no 2.md
        })
        with pytest.raises(SystemExit):
            validate_content(content)

    def test_error_message_mentions_orphan(self, tmp_path, capsys):
        content = make_content(tmp_path, {
            "1.md": MINIMAL_MD,
            "2-image-01.jpg": MINIMAL_IMG,
        })
        with pytest.raises(SystemExit):
            validate_content(content)
        assert "2-image-01.jpg" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# validate_content — unrecognised files
# ---------------------------------------------------------------------------

class TestValidateContentUnrecognisedFiles:

    def test_fails_for_txt_file(self, tmp_path):
        content = make_content(tmp_path, {
            "1.md": MINIMAL_MD,
            "notes.txt": b"hello",
        })
        with pytest.raises(SystemExit):
            validate_content(content)

    def test_fails_for_html_file(self, tmp_path):
        content = make_content(tmp_path, {
            "1.md": MINIMAL_MD,
            "1.html": b"<html></html>",
        })
        with pytest.raises(SystemExit):
            validate_content(content)

    def test_error_message_names_unrecognised_file(self, tmp_path, capsys):
        content = make_content(tmp_path, {
            "1.md": MINIMAL_MD,
            "notes.txt": b"hello",
        })
        with pytest.raises(SystemExit):
            validate_content(content)
        assert "notes.txt" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# validate_content — about page
# ---------------------------------------------------------------------------

class TestValidateContentAboutPage:

    def test_passes_with_about_md(self, tmp_path):
        content = make_content(tmp_path, {"1.md": MINIMAL_MD, "about.md": MINIMAL_MD})
        validate_content(content)  # should not raise

    def test_passes_with_about_md_and_image(self, tmp_path):
        content = make_content(tmp_path, {
            "1.md": MINIMAL_MD,
            "about.md": MINIMAL_MD,
            "about-image-01.jpg": MINIMAL_IMG,
        })
        validate_content(content)  # should not raise

    def test_about_image_without_about_md_fails(self, tmp_path):
        content = make_content(tmp_path, {
            "1.md": MINIMAL_MD,
            "about-image-01.jpg": MINIMAL_IMG,
        })
        with pytest.raises(SystemExit):
            validate_content(content)

    def test_about_md_alone_without_posts_fails(self, tmp_path):
        content = make_content(tmp_path, {"about.md": MINIMAL_MD})
        with pytest.raises(SystemExit):
            validate_content(content)


# ---------------------------------------------------------------------------
# validate_config — site_url required
# ---------------------------------------------------------------------------

class TestValidateConfig:

    def test_passes_with_site_url_set(self):
        validate_config({"site_url": "https://example.github.io"})  # should not raise

    def test_fails_when_site_url_missing(self):
        with pytest.raises(SystemExit):
            validate_config({})

    def test_fails_when_site_url_is_empty_string(self):
        with pytest.raises(SystemExit):
            validate_config({"site_url": ""})

    def test_error_message_mentions_site_url(self, capsys):
        with pytest.raises(SystemExit):
            validate_config({})
        assert "site_url" in capsys.readouterr().err
