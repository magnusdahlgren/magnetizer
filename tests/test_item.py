import pytest
from webpage import *
from website import *
from random import *
from os import listdir, path, remove
import shutil

test_website = Website('../tests/config/test_magnetizer.cfg')
test_website.refresh()


def test_article_is_valid():

    article = Item(test_website)

    article.md = 'Just some text'
    assert not article.is_valid()

    article.md = '# Starting with h1\nBut no date'
    assert not article.is_valid()

    article.md = 'Date but not starting with h1\n# Heading\n<!-- 1/1/1980 -->'
    assert article.is_valid()

    article.md = '# Both h1 and date\n<!-- 1/1/1980 -->\n# But more than one h1'
    print (article.html_full)
    assert not article.is_valid()

    article.md = '# Both h1 and date\n<!-- 1/1/1980 -->'
    assert article.is_valid()

    article.md = '<!-- Some random comment -->\n\n# Both heading and date\n<!-- 1/1/1980 -->'
    assert article.is_valid()

    # Article without heading or date should be rejected
    assert not article.from_md_filename('004-invalid-article.md')


def test_article_title():

    article = Item(test_website)

    # Title should be 'Untitled' if article contains no html
    article.html_full = None
    assert article.title() == "Untitled - Test website name"
    
    # Title should be 'Untitled' if article contains no <h1>
    article.html_full = "Blah <h2>Blah</h2> Blah"
    assert article.title() == "Untitled - Test website name"

    # Title should be the (first) <h1> if the article contains at least one <h1>
    article.html_full = 'Blah <h1>Article title!</h1> Blah <h1>Not article title</h1> Blah'
    assert article.title() == "Article title! - Test website name"

    # Any html tags should be stripped from the title
    article.html_full = 'Blah <h1>Article title <em>emphasis</em></h1> Blah'
    assert article.title() == "Article title emphasis - Test website name"


def test_item_template_filename():

    # Article with no type should not have a template filename
    item = Item(test_website)
    item.type = None
    assert item.template_filename() is None

    # Article item should use article item template
    item = Item(test_website)
    item.type = Item.ARTICLE_ITEM
    assert item.template_filename() == Item.ARTICLE_ITEM_TEMPLATE_FILENAME

    # Static item should use static item template
    item = Item(test_website)
    item.type = Item.STATIC_ITEM
    assert item.template_filename() == Item.STATIC_ITEM_TEMPLATE_FILENAME



def test_article_basic():

    article = Item(test_website)
    article.from_md_filename('001-basic-article.md')

    # Article item should use article item template
    assert '<article>' in article.html_full

    # filename should be without number and .html instead of .md
    assert article.filename == 'basic-article.html'

    # title should be the contents from <h1>
    assert article.title() == 'This is the heading - Test website name'

    # meta description should be pulled in from article
    assert article.meta_description() == 'Meta description from article'

    # short html (for index) should NOT include a footer
    assert '<footer>footer</footer>' not in article.html_summary

    # full html (for article page) should have a footer
    assert '<footer>footer</footer>' in article.html_full

    # full html should have a link back to the blog
    assert '<a href="blog-1.html" class="magnetizer-nav-back">Back to blog</a>' in article.html_full

    # article should NOT have a CC license
    cc_license = '<img alt="Creative Commons Licence" style="border-width:0" src="https://i.creativecommons.org/l/by-sa/4.0/88x31.png" />'
    assert article.html_summary.count(cc_license) == 0
    assert article.html_full.count(cc_license) == 0

    # includes should be stripped, from the short html only
    assert '<!-- MAGNETIZER_INCLUDE' in article.html_full
    assert '<!-- MAGNETIZER_INCLUDE' not in article.html_summary

    # comments should be left in the article html
    assert '<!-- Comment -->' in article.html_summary
    assert '<!-- Comment -->' in article.html_full


def test_article_with_h1_and_break_and_date_and_cc():

#   # This should be the title
#   ![alt text](resources/image.png)
#   <!-- CREATIVE COMMONS -->
#   This text should always be here
#   <!-- BREAK -->
#   Don't show this bit on the index page
#   <!-- 1/8/1998 -->

    article = Item(test_website)
    article.from_md_filename('002-article-with-h1-break-and-date.md')

    # The title should be the <h1> contents
    assert article.title() == "This should be the title - Test website name"

    # Meta data should be None (not set in article)
    assert article.meta_description() is None

    # The bit after the break tag should only show in the full html
    dont_show = "Don't show this bit on the index page"
    assert article.html_summary.count(dont_show) == 0
    assert article.html_full.count(dont_show) == 1

    # The short html should have a 'read more' link, but not the full html
    read_more = "<a href='article-with-h1-break-and-date.html' class='magnetizer-more'>Read more</a>"
    assert article.html_summary.count(read_more) == 1
    assert article.html_full.count(read_more) == 0

    # The short html should contain a link around the heading, but not the full html
    heading_link = "<h2><a href='article-with-h1-break-and-date.html'>This should be the title</a></h2>"
    assert article.html_summary.count(heading_link) == 1
    assert article.html_full.count("<a href='article-with-h1-break-and-date.html'>") == 0

    # The article should have the correct date
    assert article.date_html == "<time datetime='1998-08-01'>1 August 1998</time>"

    # The article should have a date in the html
    date = "<time datetime='1998-08-01'>1 August 1998</time>"
    assert article.html_summary.count(date) == 1
    assert article.html_full.count(date) == 1

    # Only the short html should show the date with a link
    date_with_link = "<a href='article-with-h1-break-and-date.html'><time datetime='1998-08-01'>1 August 1998</time></a>"
    assert article.html_summary.count(date_with_link) == 1
    assert article.html_full.count(date_with_link) == 0

    # Only the full html should have a CC license
    cc_license = '<img alt="Creative Commons Licence" style="border-width:0" src="https://i.creativecommons.org/l/by/4.0/88x31.png" />'
    assert article.html_summary.count(cc_license) == 0
    assert article.html_full.count(cc_license) == 1


def test_static_item():

    item = Item(test_website)
    item.from_md_filename('dont-show-on-list-page.md')

    # Static item should use static item template
    assert '<main>' in item.html_full

    # Special article should not have a date
    assert '<time datetime' not in item.html_full

    # Special article should not have a footer
    assert '<footer>footer</footer>' not in item.html_full

    # Special article should still have a link back to the homepage
    assert '<a href="/" class="magnetizer-nav-back">Back to homepage</a>' in item.html_full


def test_noindex_article():

    article_index = Item(test_website)
    article_dont_index = Item(test_website)

    article_index.from_md_filename('001-basic-article.md')
    article_dont_index.from_md_filename('009-unindexed-article.md')

    assert article_index.indexable == True
    assert article_dont_index.indexable == False


def test_article_cc():

    item = Item(test_website)
    item.filename = 'test_filename.html'

    cc_license = '<p class="magntetizer-license">'
    cc_license += '<a rel="license" href="http://creativecommons.org/licenses/by/4.0/">'
    cc_license += '<img alt="Creative Commons Licence" style="border-width:0" src="https://i.creativecommons.org/l/by/4.0/88x31.png" />'
    cc_license += '</a><br />This work by <a xmlns:cc="http://creativecommons.org/ns#" href="'
    cc_license += 'https://example.com/' + item.filename
    cc_license += '" property="cc:attributionName" rel="cc:attributionURL">'
    cc_license += 'Test Author</a> is licensed under a '
    cc_license += '<a rel="license" href="http://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution 4.0 International License</a>.'
    cc_license += '</p>'

    assert item.cc_license() == cc_license


def test_html_contents_from_multiple_md_files():

    filenames = ['005-simple-article-1.md', '006-simple-article-2.md', '007-simple-article-3.md',]

    html = Item.html_contents_from_multiple_md_files(test_website, filenames)

    assert html.count('<article>') == 3
    assert 'Article 5' in html
    assert 'Article 6' in html
    assert 'Article 7' in html