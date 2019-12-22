import pytest
from mutil import *


def test_link_h1():

    url = '/link.html'

    leading_html = "<img src=''><p>Hello</p>"
    trailing_html = "\n<p>text</p>\n<img src='image.png'>\n<h1>no link</h1>"

    # If there's no <h1>, nothing should change
    assert MUtil.link_h1(leading_html, url) == leading_html

    # Leading <h1> should get a link, the rest of the html should be unchanged
    assert MUtil.link_h1("<h1>link</h1>" + trailing_html, url) == "<h1><a href='/link.html'>link</a></h1>" + trailing_html

    # Any other html before the <h1> should be ignored but h1 should still get a link
    assert MUtil.link_h1(leading_html + "<h1>link</h1>" + trailing_html, url) == leading_html + "<h1><a href='/link.html'>link</a></h1>" + trailing_html


def test_wrap_it_in_a_link():

    assert MUtil.wrap_it_in_a_link('<b>text</b>', 'my_url') == "<a href='my_url'><b>text</b></a>"


def test_downgrade_headings():

    input = '<h1>heading 1</h1>\n'
    input += '<p>Some text</p>\n'
    input += '<h2>heading 2</h2>\n'
    input += '<p>Some text</p>\n'
    input += '<h3>heading 3</h3>\n'
    input += '<p>Some text</p>\n'

    expected = '<h2>heading 1</h2>\n'
    expected += '<p>Some text</p>\n'
    expected += '<h3>heading 2</h3>\n'
    expected += '<p>Some text</p>\n'
    expected += '<h4>heading 3</h4>\n'
    expected += '<p>Some text</p>\n'

    assert MUtil.downgrade_headings(input) == expected


def test_first_image_url_from_html():

    example_with_no_image = '<h1>Heading</a>\n<p>Text</p>'
    example_with_one_image = '<h1>Heading</a>\n<img alt="alt" src="https://example.com/img.jpg">\n<p>Text</p>'
    example_with_three_images = "<h1>Heading</a>\n<p>Text</p><img src='https://example.com/img1.jpg' alt='alt'>\n<p>Text</p><img src=\"https://example.com/img2.jpg\">\n<p>Text</p><img src=\"https://example.com/img3.jpg>\"\n<p>Text</p>"

    assert MUtil.first_image_url_from_html(example_with_no_image) == None
    assert MUtil.first_image_url_from_html(example_with_one_image) == "https://example.com/img.jpg"
    assert MUtil.first_image_url_from_html(example_with_three_images) == "https://example.com/img1.jpg"

def test_abstract_from_html():

    html = "<h1>This is the heading</h1>\n\n"
    html += "<p>Lorem ipsum dolor <em>sit amet</em>, consectetur adipiscing elit, "
    html += "sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>\n\n"
    html += "<h2>Duis aute irure dolor in reprehenderit in voluptate</h2>\n\n"
    html += "<ul>\n<li>Velit esse cillum dolore eu fugiat nulla pariatur.</li>\n\n"
    html += "<p>Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia "
    html += "deserunt mollit anim id est laborum. Ut enim ad minim veniam, quis nostrud "
    html += "exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat</p>"

    s = MUtil.abstract_from_html(html)

    # abstract should not contain any html tags (todo: this check could/should be improved)
    assert '<' not in s
    assert '>' not in s

    # leading <h1>...</h1> should be stripped out
    assert s.startswith('Lorem ipsum')

    # text from html should be present
    assert 'Lorem ipsum dolor sit amet, consectetur' in s

    # text should be truncated at 300 characters (+1 for '…')
    assert len(s) == 301

    # text should end with '…' when truncated
    assert s.endswith('…')

    # new lines should be replaced by space
    assert '\n' not in s

    # no double spaces in text
    assert '  ' not in s


def test_strip_tags_from_html():

    html = "<img src='image.jpg'><p>Some text <a href='https://example.com'>with a link</a>."
    assert MUtil.strip_tags_from_html(html) == "Some text with a link."

    # html2 = "<h1>In other news</h1>\n\n<p>Fact: ants < giraffes and hippos > mice</p>"
    # assert MUtil.strip_tags_from_html(html2) == "In other news Fact:\n\nants < giraffes and hippos > mice"


def test_strip_anything_before_h1_from_html():

    # Strip anything before </h1>
    html2 = "<p>Some text</p><h1>Heading first</h1><p>The rest of the post</p>"
    assert MUtil.strip_anything_before_h1_from_html(html2) == "<p>The rest of the post</p>"


def test_filter_out_non_article_filenames():

    filenames = ['001-article-1.md', '002-article-2.md', 'non-article.md', '003-image.gif', '123-article-3.md']

    filtered_filenames = MUtil.purge_non_article_filenames(filenames)

    assert len(filtered_filenames) == 3
    assert '001-article-1.md' in filtered_filenames
    assert '002-article-2.md' in filtered_filenames
    assert '123-article-3.md' in filtered_filenames

