""" Tests for Item Twitter cards
"""

from item import Item
from website import Website

TEST_WEBSITE = Website('tests/config/test_magnetizer.cfg')
TEST_WEBSITE.refresh()

def test_twitter_card_meta_data():
    """ Test to ensure Twitter card meta data is correctly generated
    """

    test_item = Item(TEST_WEBSITE)

    test_item.markdown_source = ('<!-- comment -->\n'
                                 '# Heading\n'
                                 '\n'
                                 'Some text\n'
                                 '![alt text](http://example.com/first_image.jpg)\n'
                                 '![alt text](http://example.com/second_image.jpg)\n'
                                 '\n'
                                 'Some text\n'
                                 '\n'
                                 'Some more text')

    test_item.html_full = '<h1>Heading</h1><p>Some text ...</p>'
    test_item.url = 'https://example.com/test.html'

    card = test_item.twitter_card()

    # Twitter card should be of type "summary_large_image"
    assert '<meta name="twitter:card" content="summary_large_image" />' in card

    # Site should be @magnusdahlgren_test_1234
    assert '<meta name="twitter:site" content="@magnusdahlgren_test_1234" />' in card

    # Title should be article title
    assert '<meta name="twitter:title" content="Heading - Test website name" />' in card

    # Image should be first image from article html_full
    # Image with absolute URL should keep the URL
    assert '<meta name="twitter:image" content="http://example.com/first_image.jpg" />' in card

    # Leading h1 should be stripped out from description
    # Include abstract in description
    assert ('<meta name="twitter:description" ' +
            'content="Some text Some text Some more text" />') in card


def test_twitter_card_relative_image_url():
    """ Test to ensure relative image URL becomes absolute in Twitter card
    """

    test_item = Item(TEST_WEBSITE)

    test_item.markdown_source = ('# Heading\n'
                                 '\n'
                                 'Some text\n'
                                 '\n'
                                 '![alt text](first_image.jpg)\n'
                                 '![alt text](http://example.com/second_image.jpg)\n'
                                 '\n'
                                 'Some text\n'
                                 '\n'
                                 'Some more text')

    test_item.url = 'https://example.com/test.html'

    card = test_item.twitter_card()

    # Relative URL should be converted to absolute URL
    assert '<meta name="twitter:image" content="https://example.com/first_image.jpg" />' in card


def test_twitter_card_no_image_url():
    """ Test to ensure Twitter card is still valid when item contains no image
    """

    test_item = Item(TEST_WEBSITE)

    test_item.markdown_source = '# Heading\n\nSome text\n\nSome more text'
    test_item.url = 'https://example.com/test.html'

    card = test_item.twitter_card()

    # twitter:image should not be present if no image in post
    assert '<meta name="twitter:image"' not in card


def test_twitter_card_from_article_from_file():
    """ Test to ensure Twitter card is possible to generate when reading item from file
    """

    test_item = Item(TEST_WEBSITE)
    test_item.from_md_filename('002-article-with-h1-break-and-date.md')

    card = test_item.twitter_card()

    # h1 tag should be stripped out
    assert '<meta name="twitter:description" content="This text should always be here' in card
