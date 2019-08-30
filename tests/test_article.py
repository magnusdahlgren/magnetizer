import pytest
from webpage import *
from website import *
from random import *
from os import listdir, path, remove
import shutil

test_website = Website('../tests/config/test_magnetizer.cfg')
test_website.refresh()


def test_article_is_valid():

    article = Article(test_website)

    article.md = 'Just some text'
    assert not article.is_valid()

    article.md = '# Starting with heading\nBut no date'
    assert not article.is_valid()

    article.md = 'Date but not starting with heading\n# Heading\n<!-- 1/1/1980 -->'
    assert not article.is_valid()

    article.md = '# Both heading and date\n<!-- 1/1/1980 -->'
    assert article.is_valid()

    # Article without heading or date should be rejected
    assert not article.from_md_filename('004-invalid-article.md')


def test_article_basic():

    article = Article(test_website)
    article.from_md_filename('001-basic-article.md')

    # filename should be without number and .html instead of .md
    assert article.filename == 'basic-article.html'

    # title should be first row of file
    assert article.title == 'This is the heading - Test website name'

    # title should be present in article meta data
    assert '<title>This is the heading - Test website name</title>' in article.meta()

    # short html (for index) should NOT include a footer
    assert '<footer>footer</footer>' not in article.html

    # full html (for article page) should have a footer
    assert '<footer>footer</footer>' in article.html_full

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
    assert article.title == "This should be the title - Test website name"

    # The bit after the break tag should only show in the full html
    dont_show = "Don't show this bit on the index page"
    assert article.html.count(dont_show) == 0
    assert article.html_full.count(dont_show) == 1

    # The short html should have a 'read more' link, but not the full html
    read_more = "<a href='article-with-h1-break-and-date.html' class='magnetizer-more'>Read more</a>"
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

