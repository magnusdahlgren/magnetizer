import pytest
from webpage import *
from website import *
from random import *
from os import listdir, path, remove
import shutil

test_website = Website('../tests/config/test_magnetizer.cfg')
test_website.refresh()

def test_webpage_from_single_article():

    webpage = Webpage(test_website)
    webpage.item_from_md_filename('001-basic-article.md')

    # Page title should be "Article title - Website name"
    title = 'This is the heading - Test website name'
    assert webpage.title == title
    assert webpage.html.count('<title>' + title + '</title>') == 1

    # Homepage header should not be present
    assert webpage.html.count('<div>header</div>') == 0

    # List page header should be present
    assert webpage.html.count('<div>list page header</div>') == 1

    # Webpage should contain the text from the article
    assert webpage.html.count('<p>And here is some text...</p>') == 1

    # Article footer should be present
    assert webpage.html.count('<footer>footer</footer>') == 1

    # Filename for webpage should be based on the article
    article = Item(test_website)
    article.from_md_filename('001-basic-article.md')
    assert webpage.filename == article.filename

    # Body should have class='magnetizer-article'
    assert webpage.html.count("<body class='magnetizer-article'>") == 1

    # Twitter card should be present
    assert '<meta name="twitter:card" content="summary_large_image" />' in webpage.html

    # Link to Atom feed should be present
    assert '<link rel="alternate" type="application/rss+xml" href="https://example.com/atom.xml" />' in webpage.html

    # Link to CSS should be present
    assert '<link rel="stylesheet" type="text/css" href="test-stylesheet.css' in webpage.html

    # Includes should be included, as per the .md file
    assert webpage.html.count("<div class='include'>Include 1</div>") == 2
    assert webpage.html.count("<div class='include'>Include 2</div>") == 1
    assert webpage.html.count("<div class='include'>Include 3</div>") == 1
    assert "[ ERROR: Include 'inexistent_file.html' does not exist! ]" in webpage.html

    # No html comments should be left in page
    assert '<!--' not in webpage.html

    # Meta description should be pulled in from article
    assert '<meta name="description" content="Meta description from article">' in webpage.html 


def test_special_page():

    webpage = Webpage(test_website)
    webpage.item_from_md_filename('dont-show-on-list-page.md')

    # Page title should be "Article title - Website name"
    title = 'This post should not be in the index - Test website name'
    assert webpage.title == title
    assert webpage.html.count('<title>' + title + '</title>') == 1

    # Homepage header should NOT be present
    assert webpage.html.count('<div>header</div>') == 0

    # List page header should NOT present
    assert webpage.html.count('<div>list page header</div>') == 0

    # Webpage should contain the text from the article
    assert webpage.html.count("<p>That's why it doesn't start with") == 1

    # Article footer should NOT be present
    assert webpage.html.count('<footer>footer</footer>') == 0

    # Filename for webpage should be based on the article
    article = Item(test_website)
    article.from_md_filename('dont-show-on-list-page.md')
    assert webpage.filename == article.filename

    # Body should have class='magnetizer-special'
    assert webpage.html.count("<body class='magnetizer-special'>") == 1

    # Twitter card should be present
    assert '<meta name="twitter:card" content="summary_large_image" />' in webpage.html

    # Link to Atom feed should be present
    assert '<link rel="alternate" type="application/rss+xml" href="https://example.com/atom.xml" />' in webpage.html

    # Link to CSS should be present
    assert '<link rel="stylesheet" type="text/css" href="test-stylesheet.css' in webpage.html

    # No html comments should be left in page
    assert '<!--' not in webpage.html


def test_home_page():

    webpage = Webpage(test_website)
    webpage.homepage_from_md_filenames(['001-basic-article.md', '002-article-with-h1-break-and-date.md', '003-another-article.md', 'dont-index-this-article.md', '100-ignore-this.txt', '005-simple-article-1.md', '006-simple-article-2.md'] )

    # Homepage header should be present
    assert webpage.html.count('<div>header</div>') == 1

    # Include (from homepage header) should be present
    assert "<div class='include'>Include 1</div>" in webpage.html

    # Homepage footer should be present
    assert webpage.html.count('<div>homepage footer</div>') == 1

    # 3 articles should be present
    assert webpage.html.count('<article>') == 3

    # Index title = "Website Name - Tag Line"
    assert webpage.title == "Test website name - test tag & line"

    # Don't show article footers on index 
    assert webpage.html.count('<footer>footer</footer>') == 0

    # Body should have class='magnetizer-homepage'
    assert webpage.html.count("<body class='magnetizer-homepage'>") == 1

    # Twitter card should *not* be present (todo: yet!)
    assert '<meta name="twitter:card" content="summary" />' not in webpage.html

    # Link to CSS should be present
    assert '<link rel="stylesheet" type="text/css" href="test-stylesheet.css' in webpage.html

    # Link to Atom feed should be present
    assert '<link rel="alternate" type="application/rss+xml" href="https://example.com/atom.xml" />' in webpage.html

    # Meta description from config file should be present
    assert '<meta name="description" content="Meta \\"description\\" from config">' in webpage.html

    # Noindex tag must not be present
    assert '<meta name="robots" content="noindex">' not in webpage.html


def test_page_indexability():

    webpage_index = Webpage(test_website)
    webpage_index.item_from_md_filename('001-basic-article.md')

    webpage_dont_index = Webpage(test_website)
    webpage_dont_index.item_from_md_filename('009-unindexed-article.md')

    # Don't include noindex tag for article page that SHOULD be indexed
    assert '<meta name="robots" content="noindex">' not in webpage_index.html

    # Include noindex tag for article page that should NOT be indexed
    assert '<meta name="robots" content="noindex">' in webpage_dont_index.html


def test_write_homepage():

    Webpage.write_homepage_from_directory(test_website, test_website.config.value('source_path'))

    # Homepage should contain some html content
    with open(test_website.config.value('output_path') + 'index.html', 'r') as myfile:
        assert myfile.read().count('<html>') == 1

    # Homepage should be included in sitemap
    assert 'https://example.com/' in test_website.sitemap.pages

    test_website.wipe()


def test_webpage_write():

    RESULT = "This is a test!"

    webpage = Webpage(test_website)
    webpage.html = RESULT
    webpage.filename = 'my-post.html'
    webpage.write()

    # File should have the correct contents
    with open(test_website.config.value('output_path') + webpage.filename, 'r') as myfile:
        assert myfile.read() == RESULT

    # Page should be included in sitemap
    assert 'https://example.com/my-post.html' in test_website.sitemap.pages


    test_website.wipe()


def test_webpage_write_multiple_from_filenames():

    test_website.wipe()

    filenames = ['001-basic-article.md', '002-article-with-h1-break-and-date.md', '003-another-article.md', '100-ignore-this.txt', 'dont-show-on-list-page.md']
    Webpage.write_item_pages_from_md_filenames(test_website, filenames)

    written_filenames = listdir(test_website.config.value('output_path'))

    # All the normal articles should have been written
    assert 'basic-article.html' in written_filenames
    assert 'article-with-h1-break-and-date.html' in written_filenames
    assert 'another-article.html' in written_filenames

    # The un-indexed articles should have been written too
    assert 'dont-show-on-list-page.html' in written_filenames

    # The file not ending in .md should not have been written
    assert 'ignore-this.html' not in written_filenames
    assert '100-ignore-this.txt' not in written_filenames

    # ... so in total, 4 files should have been written
    assert len([name for name in written_filenames if path.isfile(path.join(test_website.config.value('output_path'), name))]) == 4

    print(test_website.sitemap.pages)

    # The written files should be included in the sitemap
    assert 'https://example.com/basic-article.html' in test_website.sitemap.pages
    assert 'https://example.com/article-with-h1-break-and-date.html' in test_website.sitemap.pages
    assert 'https://example.com/another-article.html' in test_website.sitemap.pages
    assert 'https://example.com/dont-show-on-list-page.html' in test_website.sitemap.pages

    # Ignored files should not be included in the sitemap
    assert 'https://example.com/ignore-this.html' not in test_website.sitemap.pages

    test_website.wipe()


def test_resources_copy_to_output():

    test_website.wipe()

    test_website.copy_resources()

    # supported files should have been copied
    assert path.isfile(test_website.config.value('output_path') + 'resource.txt')
    assert path.isfile(test_website.config.value('output_path') + 'resource.jpg')

    # unsupported files should not have been copied
    assert not path.isfile(test_website.config.value('output_path') + 'resource.xxx')

    test_website.wipe()


def test_wipe_output_directory():

    files_to_delete = ['wipe_me.html', 'wipe_me_2.html', 'wipe_me.jpg', 'wipe_me.pdf']
    files_to_leave_in_place = ['leave_me.xxx']

    # create some test files
    for filename in files_to_delete + files_to_leave_in_place:
        with open(test_website.config.value('output_path') + filename, 'w') as myfile:
                myfile.write('test file content')

    test_website.wipe()

    for filename in files_to_delete:
        assert not path.isfile(test_website.config.value('output_path') + filename)

    for filename in files_to_leave_in_place:
        assert path.isfile(test_website.config.value('output_path') + filename)

        # Remove the test file
        remove(test_website.config.value('output_path') + filename)

    assert test_website.sitemap.pages == []


def test_includes():

    webpage = Webpage(test_website)
    webpage.html = '<h1>Some html</h1>'
    webpage.html += "<!-- MAGNETIZER_INCLUDE _include1.html -->"
    webpage.html += "<!-- MAGNETIZER_INCLUDE _include2.html -->"
    webpage.html += '<div>More html...</div>'
    webpage.html += "<!-- MAGNETIZER_INCLUDE _include3.html -->"
    webpage.html += "<!-- MAGNETIZER_INCLUDE _include1.html -->"

    correct_includes = ['_include1.html', '_include2.html', '_include3.html']
    includes = webpage.includes()

    # Set should contain each include from the html 
    for correct_include in correct_includes:
        assert correct_include in includes

    assert len(includes) == len(correct_includes)


# run the tests from bin with $ python -m pytest ../tests/