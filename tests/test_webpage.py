import pytest
from webpage import *
from website import *
from random import *
from os import listdir, path

test_website = Website()

test_website.config_source_path = '../tests/content/'
test_website.config_template_path = '../tests/templates/'
test_website.config_output_path = '../tests/public/'

test_website.template_webpage  = '_test_webpage.html'
test_website.template_blogpost = '_test_blogpost.html'
test_website.template_index_header    = '_test_index_header.html'
test_website.template_blogpost_footer = '_test_blogpost_footer.html'
test_website.name = 'Test website name'
test_website.tagline = 'test tag line'

test_website.refresh()


def test_blogpost_from_file():

    RESULT = '<article><p>This is the first post</p></article><footer>footer</footer>'

    blogpost = Blogpost(test_website)
    blogpost.read('001-test-number-one.md')

    assert blogpost.html_full == RESULT


def test_blogpost_with_markdown():

    RESULT = '<article><p><strong>This text is strong</strong></p></article><footer>footer</footer>'

    blogpost = Blogpost(test_website)
    blogpost.read('002-test-number-two.md')

    assert blogpost.html_full == RESULT


def test_webpage_blogpost_from_file_with_footer():

    RESULT = "<html><article><p>This is the first post</p></article><footer>footer</footer></html>"

    webpage = Webpage(test_website)
    webpage.read('001-test-number-one.md')

    assert webpage.html == RESULT


def test_index_page():

    RESULT = "<html>"
    RESULT += "<article><p>This is the first post</p></article>"
    RESULT += "<article><p>This is the sixth post</p></article>"
    RESULT += "<article><p>This is the first post</p></article>"
    RESULT += "</html>"

    webpage = Webpage(test_website)
    webpage.read_multiple(['001-test-number-one.md', '006-test-number-six.md', '001-test-number-one.md'])

    # Make sure all the posts are showing
    assert webpage.html == RESULT

    # Index title = "Website Name - Tag Line"
    assert webpage.title == "Test website name - test tag line"

    # Don't show blogpost footers on index 
    assert webpage.html.count('<footer>footer</footer>') == 0


def test_index_page_with_header():

    RESULT = "<html><div>header</div><article><p>This is the first post</p></article></html>"

    webpage = Webpage(test_website)
    webpage.template = Template(test_website.config_template_path + '_test_webpage_with_header.html')

    webpage.read_multiple(['001-test-number-one.md'])

    assert webpage.html == RESULT


def test_write_index_page():

    Webpage.write_index_page_from_directory(test_website, test_website.config_source_path)

    with open(test_website.config_output_path + 'index.html', 'r') as myfile:
        assert myfile.read().count('<html>') == 1

    test_website.wipe()


def test_blogpost_full_and_short_html():

    RESULT_FULL = "<article><p>Don't hide(hidden)</p></article><footer>footer</footer>"
    RESULT_SHORT = "<article><p>Don't hide</p><a href='test-number-seven.html'>Read more</a></article>"

    blogpost = Blogpost(test_website)
    blogpost.read('007-test-number-seven.md')

    assert blogpost.html_full == RESULT_FULL
    assert blogpost.html == RESULT_SHORT


def test_blogpost_link_from_h1_on_first_row():

    RESULT_FULL = "<article><h1>This is a heading</h1>\n<p>This is the text</p></article><footer>footer</footer>"
    RESULT_SHORT = "<article><h1><a href='test-number-eight.html'>This is a heading</a></h1>\n<p>This is the text</p></article>"

    blogpost = Blogpost(test_website)
    blogpost.read('008-test-number-eight.md')

    assert blogpost.html_full == RESULT_FULL
    assert blogpost.html == RESULT_SHORT


def test_blogpost_filename_from_source_file():

    RESULT = "test-number-one.html"

    blogpost = Blogpost(test_website)
    blogpost.read('001-test-number-one.md')

    assert blogpost.filename == RESULT


def test_webpage_filename_from_blogpost_filename():

    blogpost = Blogpost(test_website)
    blogpost.read('001-test-number-one.md')

    webpage = Webpage(test_website)
    webpage.read('001-test-number-one.md')

    assert webpage.filename == blogpost.filename


def test_webpage_write():

    RESULT = "This is a test!"

    webpage = Webpage(test_website)
    webpage.html = RESULT
    webpage.filename = 'my-post.html'
    webpage.write()

    print(test_website.config_output_path + webpage.filename)

    with open(test_website.config_output_path + webpage.filename, 'r') as myfile:
        assert myfile.read() == RESULT

    test_website.wipe()


def test_website_wipe():

    # Make sure there is at least one file in output directory
    webpage = Webpage(test_website)
    webpage.html = ''
    webpage.filename = 'my-post.html'
    webpage.write()

    test_website.wipe()

    assert 0 == len([name for name in listdir(test_website.config_output_path) if path.isfile(path.join(test_website.config_output_path, name))])


def test_webpage_write_multiple_from_filenames():

    test_website.wipe()

    filenames = ['001-test-number-one.md', '002-test-number-two.md', '003-test-number-three.md']

    Webpage.write_webpages_from_filenames(test_website, filenames)

    assert len(filenames) == len([name for name in listdir(test_website.config_output_path) if path.isfile(path.join(test_website.config_output_path, name))])

    test_website.wipe()


def test_blogpost_title_from_first_row_of_file():

    RESULT = "This is blog post number four"

    blogpost = Blogpost(test_website)
    blogpost.read('004-test-number-four.md')

    assert blogpost.title == RESULT


def test_blogpost_title_from_other_row_of_file():

    RESULT = "This is blog post number five"

    blogpost = Blogpost(test_website)
    blogpost.read('005-test-number-five.md')

    assert blogpost.title == RESULT


def test_webpage_title_from_first_row_of_file():

    RESULT = "This is blog post number four"

    webpage = Webpage(test_website)
    webpage.read('004-test-number-four.md')

    assert webpage.title == RESULT


def test_webpage_title_in_html():

    RESULT = '<head><title>This is blog post number four</title></head>'

    webpage = Webpage(test_website)
    webpage.template.template = '<head><title><!-- MAGNETIZER_TITLE --></title></head>'
    webpage.read('004-test-number-four.md')

    assert webpage.html.count(RESULT) == 1



# run the tests from bin with $ python -m pytest ../tests/