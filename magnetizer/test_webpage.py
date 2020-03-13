""" Tests for webpage.py
"""

from os import listdir
from website import Website
from item import Item
from webpage import Webpage

TEST_WEBSITE = Website('tests/config/test_magnetizer.cfg')
TEST_WEBSITE.refresh()

def test_webpage_from_single_article():
    """ Test creating an article item page using item_from_md_filename()
    """

    webpage = Webpage(TEST_WEBSITE)
    webpage.item_from_md_filename('001-basic-article.md')

    # Page title should be "Article title - Website name"
    title = 'This is the heading - Test website name'
    assert webpage.title == title
    assert webpage.html.count('<title>' + title + '</title>') == 1

    # Page should use static page template
    assert '<p>Article page template</p>' in webpage.html

    # List page header should be present
    assert webpage.html.count('<div>list page header</div>') == 1

    # Webpage should contain the text from the article
    assert webpage.html.count('<p>And here is some text...</p>') == 1

    # Article item footer should be present
    assert webpage.html.count('<footer class="article-footer">') == 1

    # Filename for webpage should be based on the article
    article = Item(TEST_WEBSITE)
    article.from_md_filename('001-basic-article.md')
    assert webpage.filename == article.filename

    # Body should have class='magnetizer-article-page'
    assert webpage.html.count("<body class='magnetizer-article-page'>") == 1

    # Twitter card should be present
    assert '<meta name="twitter:card" content="summary_large_image" />' in webpage.html

    # Link to Atom feed should be present
    assert ('<link rel="alternate" type="application/rss+xml" ' +
            'href="https://example.com/atom.xml" />') in webpage.html

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

    # Footnote link should have been added
    assert "<a href='#1'>[1]</a>" in webpage.html

    # Footnote anchor should have been added
    assert "<a id='1'></a>[1]:" in webpage.html


def test_static_item_page():
    """ Test creating a static item page using item_from_md_filename()
    """

    webpage = Webpage(TEST_WEBSITE)
    webpage.item_from_md_filename('dont-show-on-list-page.md')

    # Page title should be "Article title - Website name"
    title = 'This post should not be in the index - Test website name'
    assert webpage.title == title
    assert webpage.html.count('<title>' + title + '</title>') == 1

    # Page should use static page template
    assert '<p>Static page template</p>' in webpage.html

    # List page header should NOT present
    assert webpage.html.count('<div>list page header</div>') == 0

    # Webpage should contain the text from the article
    assert webpage.html.count("<p>That's why it doesn't start with") == 1

    # Article footer should NOT be present
    assert webpage.html.count('<footer>footer</footer>') == 0

    # Filename for webpage should be based on the article
    article = Item(TEST_WEBSITE)
    article.from_md_filename('dont-show-on-list-page.md')
    assert webpage.filename == article.filename

    # Body should have class='magnetizer-static-page'
    assert webpage.html.count("<body class='magnetizer-static-page'>") == 1

    # Twitter card should be present
    assert '<meta name="twitter:card" content="summary_large_image" />' in webpage.html

    # Link to Atom feed should be present
    assert ('<link rel="alternate" type="application/rss+xml" ' +
            'href="https://example.com/atom.xml" />') in webpage.html

    # Link to CSS should be present
    assert '<link rel="stylesheet" type="text/css" href="test-stylesheet.css' in webpage.html

    # No html comments should be left in page
    assert '<!--' not in webpage.html


def test_page_indexability():
    """ Test to make sure indexability carries through from item to webpage
    """

    webpage_index = Webpage(TEST_WEBSITE)
    webpage_index.item_from_md_filename('001-basic-article.md')

    webpage_dont_index = Webpage(TEST_WEBSITE)
    webpage_dont_index.item_from_md_filename('009-unindexed-article.md')

    # Don't include noindex tag for article page that SHOULD be indexed
    assert '<meta name="robots" content="noindex">' not in webpage_index.html

    # Include noindex tag for article page that should NOT be indexed
    assert '<meta name="robots" content="noindex">' in webpage_dont_index.html


def test_webpage_write():
    """ Test of webpage.write()
    """

    result = "This is a test!"

    webpage = Webpage(TEST_WEBSITE)
    webpage.html = result
    webpage.filename = 'my-post.html'
    webpage.write()

    # File should have the correct contents
    with open(TEST_WEBSITE.config.value('output_path') + webpage.filename, 'r') as myfile:
        assert myfile.read() == result

    # Page should be included in sitemap
    assert 'https://example.com/my-post.html' in TEST_WEBSITE.sitemap.pages


    TEST_WEBSITE.wipe()


def test_webpage_write_multiple_from_filenames():
    """ Test of write_item_pages_from_md_filenames()
    """

    TEST_WEBSITE.wipe()

    filenames = ['001-basic-article.md', '002-article-with-h1-break-and-date.md',
                 '003-another-article.md', '100-ignore-this.txt', 'dont-show-on-list-page.md',
                 '009-unindexed-article.md']
    Webpage.write_item_pages_from_md_filenames(TEST_WEBSITE, filenames)

    written_filenames = listdir(TEST_WEBSITE.config.value('output_path'))

    # All the normal articles should have been written
    assert 'basic-article.html' in written_filenames
    assert 'article-with-h1-break-and-date.html' in written_filenames
    assert 'another-article.html' in written_filenames
    assert 'unindexed-article.html' in written_filenames

    # The static pages should have been written too
    assert 'dont-show-on-list-page.html' in written_filenames

    # The file not ending in .md should not have been written
    assert 'ignore-this.html' not in written_filenames
    assert '100-ignore-this.txt' not in written_filenames

    # The written files should be included in the sitemap...
    assert 'https://example.com/basic-article.html' in TEST_WEBSITE.sitemap.pages
    assert 'https://example.com/article-with-h1-break-and-date.html' in TEST_WEBSITE.sitemap.pages
    assert 'https://example.com/another-article.html' in TEST_WEBSITE.sitemap.pages
    assert 'https://example.com/dont-show-on-list-page.html' in TEST_WEBSITE.sitemap.pages

    # ... except for the unindexed article
    assert 'https://example.com/unindexed-article.html' not in TEST_WEBSITE.sitemap.pages

    # Ignored files should not be included in the sitemap
    assert 'https://example.com/ignore-this.html' not in TEST_WEBSITE.sitemap.pages

    TEST_WEBSITE.wipe()


def test_includes():
    """ Test of webpage.includes()
    """

    webpage = Webpage(TEST_WEBSITE)
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
