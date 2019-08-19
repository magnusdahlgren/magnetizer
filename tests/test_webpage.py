import pytest
from webpage import *
from website import *
from random import *
from os import listdir, path, remove
import shutil

test_website = Website('../tests/config/test_magnetizer.cfg')
test_website.refresh()


def test_article_basic():

    # post starts with a h2 tag (downgraded to h3), so there shouldn't be a link
    expected = '<article><h3>This is the heading</h3>\n'
    expected += '<p>And here is some text...</p></article>'

    expected_full = '<article><h2>This is the heading</h2>\n'
    expected_full += '<p>And here is some text...</p></article>'
    expected_full += '<footer>footer</footer>'

    article = Article(test_website)
    article.from_md_filename('001-basic-article-with-h2.md')

    # filename should be without number and .html instead of .md
    assert article.filename == 'basic-article-with-h2.html'

    # title should be first row of file
    assert article.title == 'This is the heading'

    # short html (for index) should NOT include a footer
    assert article.html == expected

    # full html (for article page) should have a footer
    assert article.html_full.count('<footer>footer</footer>') == 1

    # article should NOT have a CC license
    cc_license = '<img alt="Creative Commons Licence" style="border-width:0" src="https://i.creativecommons.org/l/by-sa/4.0/88x31.png" />'
    assert article.html.count(cc_license) == 0
    assert article.html_full.count(cc_license) == 0


def test_article_with_h1_and_break_and_date_and_cc():

#   # This should be the title
#   ![alt text](resources/image.png)
#   <!-- CREATIVE COMMONS -->
#   This text should always be here
#   <!-- BREAK -->
#   Don't show this bit on the index page
#   <!-- 1/8/1998 -->

    article = Article(test_website)
    article.from_md_filename('002-article-with-h1-break-and-date.md')

    # The title should be the first usable row (so not the image)
    assert article.title == "This should be the title"

    # The bit after the break tag should only show in the full html
    dont_show = "Don't show this bit on the index page"
    assert article.html.count(dont_show) == 0
    assert article.html_full.count(dont_show) == 1

    # The short html should have a 'read more' link, but not the full html
    read_more = "<a href='article-with-h1-break-and-date.html'>Read more</a>"
    assert article.html.count(read_more) == 1
    assert article.html_full.count(read_more) == 0

    # The short html should contain a link around the heading, but not the full html
    heading_link = "<h2><a href='article-with-h1-break-and-date.html'>This should be the title</a></h2>"
    assert article.html.count(heading_link) == 1
    assert article.html_full.count("<a href='article-with-h1-break-and-date.html'>") == 0

    # The article should have the correct date
    assert article.date_html == "<time datetime='1998-08-01'>1 August 1998</time>"

    # The article should have a date in the html
    date = "<time datetime='1998-08-01'>1 August 1998</time>"
    assert article.html.count(date) == 1
    assert article.html_full.count(date) == 1

    # Only the short html should show the date with a link
    date_with_link = "<a href='article-with-h1-break-and-date.html'><time datetime='1998-08-01'>1 August 1998</time></a>"
    assert article.html.count(date_with_link) == 1
    assert article.html_full.count(date_with_link) == 0

    # Only the full html should have a CC license
    cc_license = '<img alt="Creative Commons Licence" style="border-width:0" src="https://i.creativecommons.org/l/by/4.0/88x31.png" />'
    assert article.html.count(cc_license) == 0
    assert article.html_full.count(cc_license) == 1


def test_article_cc():

    article = Article(test_website)
    article.filename = 'test_filename.html'

    cc_license = '<p class="magntetizer-license">'
    cc_license += '<a rel="license" href="http://creativecommons.org/licenses/by/4.0/">'
    cc_license += '<img alt="Creative Commons Licence" style="border-width:0" src="https://i.creativecommons.org/l/by/4.0/88x31.png" />'
    cc_license += '</a><br />This work by <a xmlns:cc="http://creativecommons.org/ns#" href="'
    cc_license += 'https://example.com/' + article.filename
    cc_license += '" property="cc:attributionName" rel="cc:attributionURL">'
    cc_license += 'Test Author</a> is licensed under a '
    cc_license += '<a rel="license" href="http://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution 4.0 International License</a>.'
    cc_license += '</p>'

    assert article.cc_license() == cc_license


def test_webpage_from_single_article():

    webpage = Webpage(test_website)
    webpage.article_from_md_filename('001-basic-article-with-h2.md')

    # Page title should be "Article title - Website name"
    title = 'This is the heading - Test website name'
    assert webpage.title == title
    assert webpage.html.count('<title>' + title + '</title>') == 1

    # Webpage should contain the text from the article
    assert webpage.html.count('<p>And here is some text...</p>') == 1

    # Article footer should be present
    assert webpage.html.count('<footer>footer</footer>') == 1

    # Filename for webpage should be based on the article
    article = Article(test_website)
    article.from_md_filename('001-basic-article-with-h2.md')
    assert webpage.filename == article.filename

    # Body should have class='magnetizer-article'
    assert webpage.html.count("<body class='magnetizer-article'>") == 1


def test_index_page():

    webpage = Webpage(test_website)
    webpage.index_from_md_filenames(['001-basic-article-with-h2.md', '002-article-with-h1-break-and-date.md', '003-another-article.md', 'dont-index-this-article.md', '100-ignore-this.txt'] )

    # Index header should be present
    assert webpage.html.count('<div>header</div>') == 1

    # 3 articles should be present
    assert webpage.html.count('<article>') == 3

    # Index title = "Website Name - Tag Line"
    assert webpage.title == "Test website name - test tag line"

    # Don't show article footers on index 
    assert webpage.html.count('<footer>footer</footer>') == 0

    # Body should have class='magnetizer-index'
    assert webpage.html.count("<body class='magnetizer-index'>") == 1


def test_write_index_page():

    Webpage.write_index_page_from_directory(test_website, test_website.config.value('source_path'))

    with open(test_website.config.value('output_path') + 'index.html', 'r') as myfile:
        assert myfile.read().count('<html>') == 1

    test_website.wipe()


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

    filenames = ['001-basic-article-with-h2.md', '002-article-with-h1-break-and-date.md', '003-another-article.md', '100-ignore-this.txt', 'dont-index-this-article.md']
    Webpage.write_article_pages_from_md_filenames(test_website, filenames)

    written_filenames = listdir(test_website.config.value('output_path'))

    # All the normal articles should have been written
    assert 'basic-article-with-h2.html' in written_filenames
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