import pytest
from website import *

test_website = Website('../tests/config/test_magnetizer.cfg')
test_website.refresh()


def test_website_css_filename():

    assert test_website.css_filename == "test-stylesheet.css?c2459f7c370ffd41171a4265a4132352"


def test_website_partial_html():

    assert test_website.partial_html('_announcement.html') == "<div class='announcement'>Announcement</div>"
