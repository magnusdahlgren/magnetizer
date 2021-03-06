""" Tests for item.py
"""

from item import Item
from website import Website

TEST_WEBSITE = Website('tests/config/test_magnetizer.cfg')
TEST_WEBSITE.refresh()


def test_article_is_valid():
    """ Verify the Item.is_valid() function
    """

    article = Item(TEST_WEBSITE)

    article.markdown_source = 'Just some text'
    assert not article.is_valid()

    article.markdown_source = '# Starting with h1\nBut no date'
    assert not article.is_valid()

    article.markdown_source = 'Date but not starting with h1\n# Heading\n<!-- 1/1/1980 -->'
    assert article.is_valid()

    article.markdown_source = '# Both h1 and date\n<!-- 1/1/1980 -->'
    assert article.is_valid()

    article.markdown_source = ('# Both h1 and date\n<!-- 1/1/1980 -->\n' +
                               '# and more than one h1')
    assert article.is_valid()

    article.markdown_source = ('<!-- Some random comment -->\n\n' +
                               '# Both heading and date\n<!-- 1/1/1980 -->')
    assert article.is_valid()

    # Article without heading or date should be rejected
    assert not article.from_md_filename('004-invalid-article.md')


def test_article_title():
    """ Verify the item's title
    """

    article = Item(TEST_WEBSITE)

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
    """ Verify the Item gets the appropriate template based on whether it is a static
    item or an article item.
    """

    # Article with no type should not have a template filename
    item = Item(TEST_WEBSITE)
    item.type = None
    assert item.template_filename() is None

    # Article item should use article item template
    item = Item(TEST_WEBSITE)
    item.type = Item.ARTICLE_ITEM
    assert item.template_filename() == Item.ARTICLE_ITEM_TEMPLATE_FILENAME

    # Static item should use static item template
    item = Item(TEST_WEBSITE)
    item.type = Item.STATIC_ITEM
    assert item.template_filename() == Item.STATIC_ITEM_TEMPLATE_FILENAME


def test_article_basic():
    """ Verify article item is generated correctly from file
    """

    article = Item(TEST_WEBSITE)
    article.from_md_filename('001-basic-article.md')

    # Article item should use article item template
    assert '<article>' in article.html_full

    # filename should be without number and .html instead of .md
    assert article.filename == 'basic-article.html'

    # title should be the contents from <h1>
    assert article.title() == 'This is the heading - Test website name'

    # meta description should be pulled in from article
    assert article.meta_description() == 'Meta description from article'

    # full html should have ARTICLE item footer
    assert '<footer class="article-footer">' in article.html_full
    assert '<footer' not in article.html_summary

    # full html should have a link back to the blog (from article item footer)
    assert '<a href="blog-1.html" class="magnetizer-nav-back">Back to blog</a>' in article.html_full

    # article should NOT have a CC license
    cc_license = 'src="https://i.creativecommons.org/l/by-sa/4.0/88x31.png"'
    assert article.html_summary.count(cc_license) == 0
    assert article.html_full.count(cc_license) == 0

    # includes should be stripped, from the short html only
    assert '<!-- MAGNETIZER_INCLUDE' in article.html_full
    assert '<!-- MAGNETIZER_INCLUDE' not in article.html_summary

    # comments should be left in the article html
    assert '<!-- Comment -->' in article.html_summary
    assert '<!-- Comment -->' in article.html_full


def test_article_with_h1_and_break_and_date_and_cc():
    """ Derify logic for title, break, date and creatice commons
    """

#   # This should be the title
#   ![alt text](resources/image.png)
#   <!-- CREATIVE COMMONS -->
#   This text should always be here
#   <!-- BREAK -->
#   Don't show this bit on the index page
#   <!-- 1/8/1998 -->

    article = Item(TEST_WEBSITE)
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
    read_more = ("<a href='article-with-h1-break-and-date.html' " +
                 "class='magnetizer-more'>Read more</a>")
    assert article.html_summary.count(read_more) == 1
    assert article.html_full.count(read_more) == 0

    # The short html should contain a link around the heading, but not the full html
    heading_link = ("<h2><a href='article-with-h1-break-and-date.html'>" +
                    "This should be the title</a></h2>")
    assert article.html_summary.count(heading_link) == 1
    assert article.html_full.count("<a href='article-with-h1-break-and-date.html'>") == 0

    # The article should have the correct date
    assert article.date_html_from_date() == "<time datetime='1998-08-01'>1 August 1998</time>"

    # The article should have a date in the html
    date = "<time datetime='1998-08-01'>1 August 1998</time>"
    assert article.html_summary.count(date) == 1
    assert article.html_full.count(date) == 1

    # Only the short html should show the date with a link
    date_with_link = ("<a href='article-with-h1-break-and-date.html'>" +
                      "<time datetime='1998-08-01'>1 August 1998</time></a>")
    assert article.html_summary.count(date_with_link) == 1
    assert article.html_full.count(date_with_link) == 0

    # Only the full html should have a CC license
    cc_license = ('<img alt="Creative Commons Licence" style="border-width:0" ' +
                  'src="https://i.creativecommons.org/l/by/4.0/88x31.png" />')
    assert article.html_summary.count(cc_license) == 0
    assert article.html_full.count(cc_license) == 1


def test_static_item():
    """ Verify that static item is correctly generated from file
    """

    item = Item(TEST_WEBSITE)
    item.from_md_filename('dont-show-on-list-page.md')

    # Static item should use static item template
    assert '<main>' in item.html_full

    # Static item should not have a date
    assert '<time datetime' not in item.html_full

    # full html should have STATIC item footer
    assert '<footer class="static-footer">' in item.html_full
    assert '<footer' not in item.html_summary

    # Static item should have a link back to the homepage (from static item footer)
    assert '<a href="/" class="magnetizer-nav-back">Back to homepage</a>' in item.html_full


def test_noindex_article():
    """ Verify logic for item.is_indexable()
    """

    article_index = Item(TEST_WEBSITE)
    article_dont_index = Item(TEST_WEBSITE)

    article_index.from_md_filename('001-basic-article.md')
    article_dont_index.from_md_filename('009-unindexed-article.md')

    assert article_index.is_indexable()
    assert not article_dont_index.is_indexable()


def test_article_cc():
    """ Verify logic for Creative Commons
    """

    item = Item(TEST_WEBSITE)
    item.filename = 'test_filename.html'

    assert ('This work by <a xmlns:cc="http://creativecommons.org/ns#" href="' +
            'https://example.com/' + item.filename +
            '" property="cc:attributionName" rel="cc:attributionURL">' +
            'Test Author</a>') in item.cc_license()


def test_html_contents_from_multiple_md_files():
    """ Verify Item.html_contents_from_multiple_md_files()
    """

    filenames = ['005-simple-article-1.md', '006-simple-article-2.md',
                 '007-simple-article-3.md']

    html = Item.html_contents_from_multiple_md_files(TEST_WEBSITE, filenames)

    assert html.count('<article>') == 3
    assert 'Article 5' in html
    assert 'Article 6' in html
    assert 'Article 7' in html
