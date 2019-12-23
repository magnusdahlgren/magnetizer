""" Tests for website.py
"""

from os import path, remove
from website import Website

TEST_WEBSITE = Website('tests/config/test_magnetizer.cfg')
TEST_WEBSITE.refresh()


def test_resources_copy_to_output():
    """ Test of Website.copy_resources
    """

    TEST_WEBSITE.wipe()
    TEST_WEBSITE.copy_resources()

    # supported files should have been copied
    assert path.isfile(TEST_WEBSITE.config.value('output_path') + 'resource.txt')
    assert path.isfile(TEST_WEBSITE.config.value('output_path') + 'resource.jpg')

    # unsupported files should not have been copied
    assert not path.isfile(TEST_WEBSITE.config.value('output_path') + 'resource.xxx')

    TEST_WEBSITE.wipe()


def test_wipe_output_directory():
    """ Test of Website.wipe()
    """

    files_to_delete = ['wipe_me.html', 'wipe_me_2.html', 'wipe_me.jpg', 'wipe_me.pdf']
    files_to_leave_in_place = ['leave_me.xxx']

    # create some test files
    for filename in files_to_delete + files_to_leave_in_place:
        with open(TEST_WEBSITE.config.value('output_path') + filename, 'w') as myfile:
            myfile.write('test file content')

    TEST_WEBSITE.wipe()

    for filename in files_to_delete:
        assert not path.isfile(TEST_WEBSITE.config.value('output_path') + filename)

    for filename in files_to_leave_in_place:
        assert path.isfile(TEST_WEBSITE.config.value('output_path') + filename)

        # Remove the test file
        remove(TEST_WEBSITE.config.value('output_path') + filename)

    assert TEST_WEBSITE.sitemap.pages == []


def test_website_css_filename():
    """ Test to make sure website.css_filename is set correctly
    """

    assert TEST_WEBSITE.css_filename == "test-stylesheet.css?c2459f7c370ffd41171a4265a4132352"


def test_website_include():
    """ Test of website.include()
    """

    assert TEST_WEBSITE.include('_include_1.html') == "<div class='include'>Include 1</div>"


def test_website_template():
    """ Test to make sure website uses the correct template
    """

    # Website should be using _website_template.html
    assert '<!-- MAGNETIZER_PAGE_CONTENT -->' in TEST_WEBSITE.template.template
