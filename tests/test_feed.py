"""Tests for magnetizer/feed.py — render_feed()"""

import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element as _El

import pytest

from magnetizer.content import Image, Post
from magnetizer.feed import render_feed
from conftest import make_post


def _req(elem: _El | None) -> _El:
    assert elem is not None
    return elem

ATOM_NS = "http://www.w3.org/2005/Atom"


def el(tag):
    return f"{{{ATOM_NS}}}{tag}"


CONFIG = {
    "site_title": "My Blog",
    "site_url": "https://example.github.io",
}


def parse(posts, config=CONFIG):
    xml = render_feed(posts, config)
    return ET.fromstring(xml)


# ---------------------------------------------------------------------------
# Feed-level elements
# ---------------------------------------------------------------------------

class TestFeedStructure:

    def test_root_is_feed_with_atom_namespace(self):
        root = parse([make_post()])
        assert root.tag == el("feed")

    def test_feed_title_uses_site_title(self):
        root = parse([make_post()])
        assert _req(root.find(el("title"))).text == "My Blog"

    def test_feed_link_href_uses_site_url(self):
        root = parse([make_post()])
        links = root.findall(el("link"))
        hrefs = [l.get("href") for l in links]
        assert "https://example.github.io" in hrefs

    def test_feed_self_link_points_to_feed_xml(self):
        root = parse([make_post()])
        links = root.findall(el("link"))
        self_link = next(l for l in links if l.get("rel") == "self")
        assert self_link.get("href") == "https://example.github.io/feed.xml"

    def test_feed_id_has_trailing_slash(self):
        root = parse([make_post()])
        assert _req(root.find(el("id"))).text == "https://example.github.io/"

    def test_feed_id_trailing_slash_not_doubled(self):
        config = {**CONFIG, "site_url": "https://example.github.io/"}
        root = parse([make_post()], config=config)
        assert _req(root.find(el("id"))).text == "https://example.github.io/"

    def test_feed_updated_is_most_recent_post_date(self):
        posts = [make_post(post_id=3, date="2026-05-24"), make_post(post_id=1, date="2026-01-01")]
        root = parse(posts)
        assert _req(root.find(el("updated"))).text == "2026-05-24T00:00:03Z"

    def test_feed_updated_with_single_post(self):
        root = parse([make_post(post_id=1, date="2026-03-15")])
        assert _req(root.find(el("updated"))).text == "2026-03-15T00:00:01Z"


# ---------------------------------------------------------------------------
# Entry count and order
# ---------------------------------------------------------------------------

class TestFeedEntries:

    def test_one_entry_per_post(self):
        posts = [make_post(post_id=1), make_post(post_id=2), make_post(post_id=3)]
        root = parse(posts)
        assert len(root.findall(el("entry"))) == 3

    def test_entries_in_reverse_chronological_order(self):
        posts = [make_post(post_id=3, date="2026-05-24"), make_post(post_id=1, date="2026-01-01")]
        root = parse(posts)
        entries = root.findall(el("entry"))
        dates = [_req(e.find(el("updated"))).text for e in entries]
        assert dates == ["2026-05-24T00:00:03Z", "2026-01-01T00:00:01Z"]

    def test_entries_on_same_date_have_unique_timestamps(self):
        posts = [make_post(post_id=2, date="2026-05-24"), make_post(post_id=1, date="2026-05-24")]
        root = parse(posts)
        entries = root.findall(el("entry"))
        timestamps = [_req(e.find(el("updated"))).text for e in entries]
        assert len(set(timestamps)) == 2


# ---------------------------------------------------------------------------
# Entry-level elements
# ---------------------------------------------------------------------------

class TestEntryStructure:

    def test_entry_title_uses_post_title(self):
        root = parse([make_post(title="My Great Post")])
        entry = _req(root.find(el("entry")))
        assert _req(entry.find(el("title"))).text == "My Great Post"

    def test_entry_title_falls_back_to_uk_date_for_untitled_post(self):
        post = Post(id=1, date="2026-05-24", date_uk="24 May 2026",
                    title=None, url="1.html", body_html="", images=[])
        root = parse([post])
        entry = _req(root.find(el("entry")))
        assert _req(entry.find(el("title"))).text == "24 May 2026"

    def test_entry_link_href_is_absolute_url(self):
        root = parse([make_post(post_id=5)])
        entry = _req(root.find(el("entry")))
        assert _req(entry.find(el("link"))).get("href") == "https://example.github.io/5.html"

    def test_entry_id_is_absolute_url(self):
        root = parse([make_post(post_id=5)])
        entry = _req(root.find(el("entry")))
        assert _req(entry.find(el("id"))).text == "https://example.github.io/5.html"

    def test_entry_updated_is_rfc3339_date(self):
        root = parse([make_post(post_id=1, date="2026-03-01")])
        entry = _req(root.find(el("entry")))
        assert _req(entry.find(el("updated"))).text == "2026-03-01T00:00:01Z"

    def test_entry_content_type_is_html(self):
        root = parse([make_post()])
        entry = _req(root.find(el("entry")))
        assert _req(entry.find(el("content"))).get("type") == "html"

    def test_entry_content_contains_body_html(self):
        root = parse([make_post(body_html="<p>Hello world</p>")])
        entry = _req(root.find(el("entry")))
        assert "<p>Hello world</p>" in (_req(entry.find(el("content"))).text or "")

    def test_feed_has_author_element(self):
        root = parse([make_post()])
        assert root.find(el("author")) is not None

    def test_feed_author_name_uses_site_title(self):
        root = parse([make_post()])
        assert _req(_req(root.find(el("author"))).find(el("name"))).text == "My Blog"

    def test_entry_does_not_have_author_element(self):
        root = parse([make_post()])
        entry = _req(root.find(el("entry")))
        assert entry.find(el("author")) is None


# ---------------------------------------------------------------------------
# Entry images
# ---------------------------------------------------------------------------

class TestEntryImages:

    def test_entry_content_includes_img_tag_for_image(self):
        post = make_post(images=["1-image-01.jpg"])
        xml = render_feed([post], CONFIG)
        assert 'src="https://example.github.io/1-image-01-resized.jpg"' in xml

    def test_entry_content_uses_resized_filename(self):
        post = make_post(images=["1-image-01.jpg"])
        xml = render_feed([post], CONFIG)
        assert "1-image-01-resized.jpg" in xml
        assert '"1-image-01.jpg"' not in xml

    def test_entry_content_includes_alt_text(self):
        post = make_post(images=[Image("1-image-01.jpg", alt="A sunny beach")])
        xml = render_feed([post], CONFIG)
        assert 'alt="A sunny beach"' in xml

    def test_entry_content_images_appear_before_body_html(self):
        post = make_post(images=["1-image-01.jpg"], body_html="<p>Text here</p>")
        xml = render_feed([post], CONFIG)
        assert xml.index("1-image-01-resized.jpg") < xml.index("Text here")

    def test_entry_content_multiple_images_all_included(self):
        post = make_post(images=["1-image-01.jpg", "1-image-02.jpg"])
        xml = render_feed([post], CONFIG)
        assert "1-image-01-resized.jpg" in xml
        assert "1-image-02-resized.jpg" in xml

    def test_entry_content_special_chars_in_alt_escaped(self):
        post = make_post(images=[Image("1-image-01.jpg", alt='Say "cheese" & smile')])
        xml = render_feed([post], CONFIG)
        assert 'alt="Say &quot;cheese&quot; &amp; smile"' in xml
        ET.fromstring(xml)  # must be valid XML

    def test_entry_without_images_has_no_img_tag(self):
        post = make_post(body_html="<p>No images here</p>")
        xml = render_feed([post], CONFIG)
        assert "<img" not in xml


# ---------------------------------------------------------------------------
# XML safety
# ---------------------------------------------------------------------------

class TestFeedXmlSafety:

    def test_site_title_with_ampersand_produces_valid_xml(self):
        config = {**CONFIG, "site_title": "Photos & Notes"}
        xml = render_feed([make_post()], config)
        ET.fromstring(xml)  # would raise ParseError if invalid

    def test_post_title_with_ampersand_produces_valid_xml(self):
        xml = render_feed([make_post(title="A & B")], CONFIG)
        ET.fromstring(xml)

    def test_post_title_with_angle_bracket_produces_valid_xml(self):
        xml = render_feed([make_post(title="A > B")], CONFIG)
        ET.fromstring(xml)

    def test_site_title_special_chars_escaped_in_feed_title(self):
        config = {**CONFIG, "site_title": "Photos & Notes"}
        root = parse([make_post()], config=config)
        assert _req(root.find(el("title"))).text == "Photos & Notes"

    def test_post_title_special_chars_escaped_in_entry_title(self):
        root = parse([make_post(title="A & B")])
        entry = _req(root.find(el("entry")))
        assert _req(entry.find(el("title"))).text == "A & B"

    def test_undated_post_excluded_from_feed(self):
        dated = make_post(post_id=2, date="2026-05-24")
        undated = Post(id=1, date=None, date_uk=None, title="No date",
                       url="1.html", body_html="", images=[])
        root = parse([dated, undated])
        assert len(root.findall(el("entry"))) == 1

    def test_feed_valid_xml_when_all_posts_undated(self):
        undated = Post(id=1, date=None, date_uk=None, title=None,
                       url="1.html", body_html="", images=[])
        xml = render_feed([undated], CONFIG)
        ET.fromstring(xml)  # must not raise

    def test_feed_updated_uses_most_recent_dated_post(self):
        dated = make_post(post_id=2, date="2026-05-24")
        undated = Post(id=3, date=None, date_uk=None, title=None,
                       url="3.html", body_html="", images=[])
        root = parse([undated, dated])
        assert _req(root.find(el("updated"))).text == "2026-05-24T00:00:02Z"
