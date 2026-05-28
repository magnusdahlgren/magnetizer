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
        assert post.images == ["1-image-01.jpg"]

    def test_multiple_images_in_correct_order(self):
        post = parse_post(make_md(), 1, ["1-image-01.jpg", "1-image-02.png"])
        assert post.images == ["1-image-01.jpg", "1-image-02.png"]

    def test_images_sorted_by_image_number(self):
        post = parse_post(make_md(), 1, ["1-image-03.jpg", "1-image-01.png", "1-image-02.jpg"])
        assert post.images == ["1-image-01.png", "1-image-02.jpg", "1-image-03.jpg"]

    def test_images_provided_out_of_order_are_sorted(self):
        post = parse_post(make_md(), 1, ["1-image-02.jpg", "1-image-01.jpg"])
        assert post.images[0] == "1-image-01.jpg"
        assert post.images[1] == "1-image-02.jpg"
