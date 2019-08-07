import pytest
from webpage import *
from website import *
from random import *
from os import listdir, path

test_website = Website()

test_website.config_source_path = '../tests/content/'
test_website.config_template_path = '../tests/templates/'
test_website.config_output_path = '../tests/public/'

test_website.template_blogpost = '_test_blogpost.html'
test_website.template_webpage  = '_test_webpage.html'


def test_blogpost_from_file():

    RESULT = '<article><p>This is the first post</p></article>'

    blogpost = Blogpost(test_website)
    blogpost.read('001-test-number-one.md')

    assert blogpost.html == RESULT


def test_blogpost_with_markdown():

    RESULT = '<article><h1>This is a test heading</h1></article>'

    blogpost = Blogpost(test_website)
    blogpost.read('002-test-number-two.md')

    assert blogpost.html == RESULT


def test_blogpost_footer():

    RESULT = '<article><p>This is the first post</p></article><footer>footer</footer>'

    blogpost = Blogpost(test_website)
    blogpost.template.template += test_website.magnetizer_blogpost_footer_tag
    blogpost.read('001-test-number-one.md')

    assert blogpost.html == RESULT

def test_webpage_from_file():

    RESULT = '<html><article><p>This is the first post</p></article></html>'

    webpage = Webpage(test_website)
    webpage.read('001-test-number-one.md')

    assert webpage.html == RESULT

def test_webpage_from_multiple_files():

    RESULT = "<html>"
    RESULT += '<article><p>This is the first post</p></article>'
    RESULT += '<article><p>This is the sixth post</p></article>'
    RESULT += '<article><p>This is the first post</p></article>'
    RESULT += "</html>"

    webpage = Webpage(test_website)
    webpage.read_multiple(['001-test-number-one.md', '006-test-number-six.md', '001-test-number-one.md'])

    assert webpage.html == RESULT


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

    print (webpage.html.count(RESULT))

    assert webpage.html.count(RESULT) == 1


def test_index_page():

    Webpage.write_index_page_from_directory(test_website, test_website.config_source_path)

    with open(test_website.config_output_path + 'index.html', 'r') as myfile:
        assert myfile.read().count('<html>') == 1

    test_website.wipe()


  

# run the tests from bin with $ python -m pytest ../tests/