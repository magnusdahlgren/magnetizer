import pytest
from webpage import *
from website import *
from random import *
from os import listdir, path, remove
import shutil

test_website = Website('../tests/config/test_magnetizer.cfg')
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

    # Meta title should be "Blogpost title - Website name"
    assert webpage.title == 'This is the first post - Test website name'

    # Blogpost footer should be present
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
    webpage.template = Template(test_website.config.value('template_path') + '_test_webpage_with_header.html')

    webpage.read_multiple(['001-test-number-one.md'])

    assert webpage.html == RESULT


def test_write_index_page():

    Webpage.write_index_page_from_directory(test_website, test_website.config.value('source_path'))

    with open(test_website.config.value('output_path') + 'index.html', 'r') as myfile:
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


def test_blogpost_with_date():

    COMMENT = '<!-- 1/8/1998 -->'
    RESULT_NO_LINK = "<date class='magnetizer-date'>1 August 1998</date>"
    RESULT_WITH_LINK = "<date class='magnetizer-date'><a href='blogpost-with-date.html'>1 August 1998</a></date>"

    blogpost = Blogpost(test_website)
    blogpost.read('009-blogpost-with-date.md')

    #blogpost should have the correct date
    assert blogpost.date == "1 August 1998"

    #blogpost full html should have date (not link)
    assert blogpost.html_full.count(RESULT_WITH_LINK) == 0
    assert blogpost.html_full.count(RESULT_NO_LINK) == 1

    #blogpost short html should have date with link
    assert blogpost.html.count(RESULT_WITH_LINK) == 1


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

    print(test_website.config.value('output_path') + webpage.filename)

    with open(test_website.config.value('output_path') + webpage.filename, 'r') as myfile:
        assert myfile.read() == RESULT

    test_website.wipe()


def test_webpage_write_multiple_from_filenames():

    test_website.wipe()

    filenames = ['001-test-number-one.md', '002-test-number-two.md', '003-test-number-three.md']

    Webpage.write_webpages_from_filenames(test_website, filenames)

    assert len(filenames) == len([name for name in listdir(test_website.config.value('output_path')) if path.isfile(path.join(test_website.config.value('output_path'), name))])

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


def test_webpage_title_in_html():

    RESULT = '<head><title>This is blog post number four - Test website name</title></head>'

    webpage = Webpage(test_website)
    webpage.template.template = '<head><title><!-- MAGNETIZER_TITLE --></title></head>'
    webpage.read('004-test-number-four.md')

    assert webpage.html.count(RESULT) == 1


def test_resources_copy_to_public():

    test_website.wipe()
    test_website.copy_resources()

    assert path.isfile(test_website.config.value('output_path') + 'resource.txt')
    assert path.isfile(test_website.config.value('output_path') + 'resource.jpg')
    assert not path.isfile(test_website.config.value('output_path') + 'resource.xxx')


def test_wipe_output_directory():

    files_to_delete = ['wipe_me.html', 'wipe_me_2.html', 'wipe_me.jpg', 'wipe_me.pdf']
    files_to_leave_in_place = ['leave_me.xxx']

    # create some test files
    for filename in files_to_delete + files_to_leave_in_place:
        with open(test_website.config.value('output_path') + filename, 'w') as myfile:
                myfile.write('test file content')

    # testing the test - remove once working
    assert path.isfile(test_website.config.value('output_path') + 'wipe_me.html')

    test_website.wipe()

    for filename in files_to_delete:
        assert not path.isfile(test_website.config.value('output_path') + filename)

    for filename in files_to_leave_in_place:
        assert path.isfile(test_website.config.value('output_path') + filename)
        remove(test_website.config.value('output_path') + filename)


# run the tests from bin with $ python -m pytest ../tests/