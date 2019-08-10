import pytest
from mutil import *


def test_link_first_tag():

    url = '/link.html'

    examples_link = [ "<h1>link</h1>", "<img src='link.jpg'>" ]
    examples_dont = [ "<p>no link</p>" ]

    more_html = "\n<p>text</p>\n<img src='image.png'>\n<h1>no link</h1>"
    linked = "<a href='/link.html'>"

    # h1 should be wrapped in <a>, no other links should be added
    assert MUtil.link_first_tag("<h1>link</h1>" + more_html, url) == linked + "<h1>link</h1></a>" + more_html

    # all the positive examples should be linked
    for example in examples_link:
        assert MUtil.link_first_tag(example + more_html, url).count(linked) == 1

    # none of the negative examples should be linked
    for example in examples_dont:
        assert MUtil.link_first_tag(example + more_html, url).count(linked) == 0


def test_wrap_it_in_a_link():

    assert MUtil.wrap_it_in_a_link('<b>text</b>', 'my_url') == "<a href='my_url'><b>text</b></a>"
