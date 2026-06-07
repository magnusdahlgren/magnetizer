"""Tests for magnetizer/sitemap.py — render_sitemap() and render_robots_txt()"""

import pytest
from magnetizer.sitemap import render_sitemap, render_robots_txt


CONFIG = {"site_url": "https://example.com"}
CONFIG_TRAILING_SLASH = {"site_url": "https://example.com/"}


class TestRenderSitemap:

    def test_has_xml_declaration(self):
        result = render_sitemap([], CONFIG)
        assert result.startswith('<?xml version="1.0" encoding="UTF-8"?>')

    def test_has_urlset_element(self):
        result = render_sitemap([], CONFIG)
        assert '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' in result

    def test_url_uses_site_url(self):
        result = render_sitemap([("1.html", None)], CONFIG)
        assert "<loc>https://example.com/1.html</loc>" in result

    def test_lastmod_included_when_present(self):
        result = render_sitemap([("1.html", "2026-05-24")], CONFIG)
        assert "<lastmod>2026-05-24</lastmod>" in result

    def test_lastmod_omitted_when_none(self):
        result = render_sitemap([("1.html", None)], CONFIG)
        assert "lastmod" not in result

    def test_multiple_pages_each_have_url_element(self):
        pages = [("1.html", "2026-05-24"), ("2.html", "2026-05-23"), ("index.html", None)]
        result = render_sitemap(pages, CONFIG)
        assert result.count("<url>") == 3

    def test_trailing_slash_stripped_from_site_url(self):
        result = render_sitemap([("1.html", None)], CONFIG_TRAILING_SLASH)
        assert "<loc>https://example.com/1.html</loc>" in result

    def test_empty_pages_produces_valid_xml(self):
        result = render_sitemap([], CONFIG)
        assert "</urlset>" in result


class TestRenderRobotsTxt:

    def test_contains_user_agent(self):
        result = render_robots_txt(CONFIG)
        assert "User-agent: *" in result

    def test_contains_allow(self):
        result = render_robots_txt(CONFIG)
        assert "Allow: /" in result

    def test_contains_sitemap_url(self):
        result = render_robots_txt(CONFIG)
        assert "Sitemap: https://example.com/sitemap.xml" in result

    def test_trailing_slash_stripped_from_site_url(self):
        result = render_robots_txt(CONFIG_TRAILING_SLASH)
        assert "Sitemap: https://example.com/sitemap.xml" in result
