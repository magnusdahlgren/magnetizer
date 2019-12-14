import pytest
from website import *

test_website = Website('../tests/config/test_magnetizer.cfg')
test_website.refresh()


def test_website_css_filename():

    assert test_website.css_filename == "test-stylesheet.css?c2459f7c370ffd41171a4265a4132352"


def test_website_partial_html():

    assert test_website.include('_include_1.html') == "<div class='include'>Include 1</div>"


def test_website_template():

    # Website should be using _website_template.html
    assert '<!-- MAGNETIZER_PAGE_CONTENT -->' in test_website.template.template

