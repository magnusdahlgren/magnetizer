"""Tests for magnetizer/content.py — Post dataclass and parse_post()"""

import pytest
from magnetizer.content import Post, parse_post


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_md(date="2026-05-24", title=None, body=""):
    """Build a minimal markdown string with frontmatter."""
    lines = ["---", f"date: {date}"]
    if title:
        lines.append(f"title: {title}")
    lines.append("---")
    if body:
        lines.append("")
        lines.append(body)
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Post dataclass
# ---------------------------------------------------------------------------

class TestPostDataclass:

    def test_post_is_a_dataclass(self):
        post = parse_post(make_md(), 1, [])
        assert isinstance(post, Post)

    def test_post_id(self):
        post = parse_post(make_md(), 7, [])
        assert post.id == 7

    def test_post_url(self):
        post = parse_post(make_md(), 7, [])
        assert post.url == "7.html"


# ---------------------------------------------------------------------------
# Frontmatter parsing
# ---------------------------------------------------------------------------

class TestFrontmatterParsing:

    def test_date_extracted(self):
        post = parse_post(make_md(date="2026-05-24"), 1, [])
        assert post.date == "2026-05-24"

    def test_title_extracted_when_present(self):
        post = parse_post(make_md(title="My Great Post"), 1, [])
        assert post.title == "My Great Post"

    def test_title_is_none_when_absent(self):
        post = parse_post(make_md(), 1, [])
        assert post.title is None

    def test_title_with_colon_preserved(self):
        post = parse_post(make_md(title="Hello: World"), 1, [])
        assert post.title == "Hello: World"


# ---------------------------------------------------------------------------
# UK date formatting
# ---------------------------------------------------------------------------

class TestDateUK:

    def test_date_uk_format(self):
        post = parse_post(make_md(date="2026-05-24"), 1, [])
        assert post.date_uk == "24 May 2026"

    def test_date_uk_no_leading_zero_on_day(self):
        post = parse_post(make_md(date="2026-05-04"), 1, [])
        assert post.date_uk == "4 May 2026"

    def test_date_uk_january(self):
        post = parse_post(make_md(date="2026-01-01"), 1, [])
        assert post.date_uk == "1 January 2026"

    def test_date_uk_december(self):
        post = parse_post(make_md(date="2026-12-31"), 1, [])
        assert post.date_uk == "31 December 2026"


# ---------------------------------------------------------------------------
# Markdown body → HTML
# ---------------------------------------------------------------------------

class TestBodyHtml:

    def test_empty_body_produces_empty_string(self):
        post = parse_post(make_md(), 1, [])
        assert post.body_html == ""

    def test_paragraph_converted_to_html(self):
        post = parse_post(make_md(body="Hello world"), 1, [])
        assert "<p>Hello world</p>" in post.body_html

    def test_bold_converted_to_strong(self):
        post = parse_post(make_md(body="Hello **world**"), 1, [])
        assert "<strong>world</strong>" in post.body_html

    def test_heading_converted(self):
        post = parse_post(make_md(body="## Section"), 1, [])
        assert "<h2>Section</h2>" in post.body_html

    def test_link_converted(self):
        post = parse_post(make_md(body="[click](http://example.com)"), 1, [])
        assert 'href="http://example.com"' in post.body_html

    def test_multiple_paragraphs(self):
        post = parse_post(make_md(body="First\n\nSecond"), 1, [])
        assert post.body_html.count("<p>") == 2

    def test_frontmatter_not_included_in_body(self):
        post = parse_post(make_md(date="2026-05-24", title="My Title"), 1, [])
        assert "2026-05-24" not in post.body_html
        assert "My Title" not in post.body_html


# ---------------------------------------------------------------------------
# Images
# ---------------------------------------------------------------------------

class TestImages:

    def test_images_empty_when_none_provided(self):
        post = parse_post(make_md(), 1, [])
        assert post.images == []

    def test_single_image_included(self):
        post = parse_post(make_md(), 1, ["1-image-01.jpg"])
        assert post.images[0].filename == "1-image-01.jpg"

    def test_multiple_images_in_correct_order(self):
        post = parse_post(make_md(), 1, ["1-image-01.jpg", "1-image-02.png"])
        assert [img.filename for img in post.images] == ["1-image-01.jpg", "1-image-02.png"]

    def test_images_sorted_by_image_number(self):
        post = parse_post(make_md(), 1, ["1-image-03.jpg", "1-image-01.png", "1-image-02.jpg"])
        assert [img.filename for img in post.images] == ["1-image-01.png", "1-image-02.jpg", "1-image-03.jpg"]

    def test_images_provided_out_of_order_are_sorted(self):
        post = parse_post(make_md(), 1, ["1-image-02.jpg", "1-image-01.jpg"])
        assert post.images[0].filename == "1-image-01.jpg"
        assert post.images[1].filename == "1-image-02.jpg"


# ---------------------------------------------------------------------------
# Read more marker
# ---------------------------------------------------------------------------

class TestReadMore:

    def test_excerpt_html_is_none_when_no_more_tag(self):
        post = parse_post(make_md(body="Hello world"), 1, [])
        assert post.excerpt_html is None

    def test_excerpt_html_contains_content_before_more_tag(self):
        post = parse_post(make_md(body="Intro.\n\n<!-- more -->\n\nRest."), 1, [])
        assert "<p>Intro.</p>" in post.excerpt_html

    def test_excerpt_html_excludes_content_after_more_tag(self):
        post = parse_post(make_md(body="Intro.\n\n<!-- more -->\n\nRest."), 1, [])
        assert "Rest" not in post.excerpt_html

    def test_body_html_contains_full_content_when_more_tag_present(self):
        post = parse_post(make_md(body="Intro.\n\n<!-- more -->\n\nRest."), 1, [])
        assert "<p>Intro.</p>" in post.body_html
        assert "<p>Rest.</p>" in post.body_html

    def test_more_tag_not_present_in_excerpt_html(self):
        post = parse_post(make_md(body="Intro.\n\n<!-- more -->\n\nRest."), 1, [])
        assert "<!-- more -->" not in post.excerpt_html

    def test_more_tag_not_present_in_body_html(self):
        post = parse_post(make_md(body="Intro.\n\n<!-- more -->\n\nRest."), 1, [])
        assert "<!-- more -->" not in post.body_html

    def test_body_html_preserves_paragraph_break_when_more_tag_inline(self):
        post = parse_post(make_md(body="Intro.<!-- more -->Rest."), 1, [])
        assert "<p>Intro.</p>" in post.body_html
        assert "<p>Rest.</p>" in post.body_html


# ---------------------------------------------------------------------------
# Optional date
# ---------------------------------------------------------------------------

class TestOptionalDate:

    def test_date_is_none_when_not_in_frontmatter(self):
        post = parse_post("---\n---\n", 1, [])
        assert post.date is None

    def test_date_uk_is_none_when_not_in_frontmatter(self):
        post = parse_post("---\n---\n", 1, [])
        assert post.date_uk is None

    def test_date_set_when_present_in_frontmatter(self):
        post = parse_post(make_md(date="2026-05-24"), 1, [])
        assert post.date == "2026-05-24"


# ---------------------------------------------------------------------------
# Image dataclass and alt texts
# ---------------------------------------------------------------------------

class TestImageAltTexts:

    def test_images_are_image_objects(self):
        from magnetizer.content import Image
        post = parse_post(make_md(), 1, ["1-image-01.jpg"])
        assert isinstance(post.images[0], Image)

    def test_image_has_filename(self):
        post = parse_post(make_md(), 1, ["1-image-01.jpg"])
        assert post.images[0].filename == "1-image-01.jpg"

    def test_image_alt_from_frontmatter(self):
        md = "---\ndate: 2026-05-24\nimages:\n  - A sunny beach\n---\n"
        post = parse_post(md, 1, ["1-image-01.jpg"])
        assert post.images[0].alt == "A sunny beach"

    def test_image_alt_empty_when_no_images_key(self):
        post = parse_post(make_md(), 1, ["1-image-01.jpg"])
        assert post.images[0].alt == ""

    def test_image_alt_empty_for_extra_images_beyond_alt_list(self):
        md = "---\ndate: 2026-05-24\nimages:\n  - First alt\n---\n"
        post = parse_post(md, 1, ["1-image-01.jpg", "1-image-02.jpg"])
        assert post.images[0].alt == "First alt"
        assert post.images[1].alt == ""

    def test_multiple_alts_assigned_in_order(self):
        md = "---\ndate: 2026-05-24\nimages:\n  - First\n  - Second\n---\n"
        post = parse_post(md, 1, ["1-image-01.jpg", "1-image-02.jpg"])
        assert post.images[0].alt == "First"
        assert post.images[1].alt == "Second"

    def test_colon_in_title_preserved_alongside_images_list(self):
        md = "---\ndate: 2026-05-24\ntitle: Title: with colon\nimages:\n  - Alt text\n---\n"
        post = parse_post(md, 1, ["1-image-01.jpg"])
        assert post.title == "Title: with colon"
        assert post.images[0].alt == "Alt text"


# ---------------------------------------------------------------------------
# Frontmatter key validation
# ---------------------------------------------------------------------------

class TestFrontmatterKeyValidation:

    def test_no_warning_for_valid_keys(self, capsys):
        parse_post(make_md(date="2026-05-24", title="Hello"), 1, [])
        assert "Warning" not in capsys.readouterr().out

    def test_warning_for_unknown_key(self, capsys):
        md = "---\ndate: 2026-05-24\nfoo: bar\n---\n"
        parse_post(md, 1, [])
        assert "Warning" in capsys.readouterr().out

    def test_warning_mentions_post_id(self, capsys):
        md = "---\ndate: 2026-05-24\nfoo: bar\n---\n"
        parse_post(md, 12, [])
        assert "12" in capsys.readouterr().out

    def test_warning_mentions_unknown_key(self, capsys):
        md = "---\ndate: 2026-05-24\nfoo: bar\n---\n"
        parse_post(md, 1, [])
        assert "foo" in capsys.readouterr().out

    def test_warning_for_each_unknown_key(self, capsys):
        md = "---\ndate: 2026-05-24\nfoo: bar\nbaz: qux\n---\n"
        parse_post(md, 1, [])
        output = capsys.readouterr().out
        assert "foo" in output
        assert "baz" in output

    def test_images_key_is_allowed(self, capsys):
        md = "---\ndate: 2026-05-24\nimages:\n  - Alt text\n---\n"
        parse_post(md, 1, ["1-image-01.jpg"])
        assert "Warning" not in capsys.readouterr().out
