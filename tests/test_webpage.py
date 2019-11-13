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
    webpage.article_from_md_filename('001-basic-article.md')

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
    article = Article(test_website)
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

    # Announcement should be included twice, as per the .md file
    assert webpage.html.count("<div class='announcement'>Announcement</div>") == 2

    # No html comments should be left in page
    assert '<!--' not in webpage.html

    # Meta description should be pulled in from article
    assert '<meta name="description" content="Meta description from article">' in webpage.html 

def test_special_page():

    webpage = Webpage(test_website)
    webpage.article_from_md_filename('dont-index-this-article.md')

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
    article = Article(test_website)
    article.from_md_filename('dont-index-this-article.md')
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

    # Announcement (from homepage header) should be present
    assert "<div class='announcement'>Announcement</div>" in webpage.html

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


def test_write_homepage():

    Webpage.write_homepage_from_directory(test_website, test_website.config.value('source_path'))

    with open(test_website.config.value('output_path') + 'index.html', 'r') as myfile:
        assert myfile.read().count('<html>') == 1

    test_website.wipe()


def test_webpage_write():

    RESULT = "This is a test!"

    webpage = Webpage(test_website)
    webpage.html = RESULT
    webpage.filename = 'my-post.html'
    webpage.write()

    with open(test_website.config.value('output_path') + webpage.filename, 'r') as myfile:
        assert myfile.read() == RESULT

    test_website.wipe()


def test_webpage_write_multiple_from_filenames():

    test_website.wipe()

    filenames = ['001-basic-article.md', '002-article-with-h1-break-and-date.md', '003-another-article.md', '100-ignore-this.txt', 'dont-index-this-article.md']
    Webpage.write_article_pages_from_md_filenames(test_website, filenames)

    written_filenames = listdir(test_website.config.value('output_path'))

    # All the normal articles should have been written
    assert 'basic-article.html' in written_filenames
    assert 'article-with-h1-break-and-date.html' in written_filenames
    assert 'another-article.html' in written_filenames

    # The un-indexed article should have been written too
    assert 'dont-index-this-article.html' in written_filenames

    # The file not ending in .md should not have been written
    assert 'ignore-this.html' not in written_filenames
    assert '100-ignore-this.txt' not in written_filenames

    # ... so in total, 4 files should have been written
    assert len([name for name in written_filenames if path.isfile(path.join(test_website.config.value('output_path'), name))]) == 4

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


# run the tests from bin with $ python -m pytest ../tests/