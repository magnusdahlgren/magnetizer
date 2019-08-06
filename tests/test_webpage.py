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


def test_webpage_from_file():

    RESULT = '<html><article><p>This is the first post</p></article></html>'

    webpage = Webpage(test_website)
    webpage.read('001-test-number-one.md')

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


# run the tests from bin with $ python -m pytest ../tests/