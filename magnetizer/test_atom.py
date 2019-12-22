""" Test atom.py

 Example feed:

<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">

  <title>Example Feed</title>
  <link href="http://example.org/"/>
  <updated>2003-12-13T18:30:02Z</updated>
  <author>
    <name>John Doe</name>
  </author>
  <generator uri="/myblog.php" version="1.0">
        Example Toolkit
  </generator>
  <id>urn:uuid:60a76c80-d399-11d9-b93C-0003939e0af6</id>

  <entry>
    <title>Atom-Powered Robots Run Amok</title>
    <link href="http://example.org/2003/12/13/atom03"/>
    <id>urn:uuid:1225c695-cfb8-4ebb-aaaa-80da344efa6a</id>
    <updated>2003-12-13T18:30:02Z</updated>
    <summary>Some text.</summary>
  </entry>

</feed>
"""

from item import Item
from website import Website
from atom import Atom

TEST_WEBSITE = Website('tests/config/test_magnetizer.cfg')
TEST_WEBSITE.refresh()

ATOM = Atom(TEST_WEBSITE)
FEED = ATOM.feed(['004-invalid-article.md', '003-another-article.md',
                  '002-article-with-h1-break-and-date.md', '001-basic-article.md',
                  'dont-index-this-article.md', '100-ignore-this.txt'])

def test_feed():
    """ Test to ensure Atom feed is correct
    """

    # Should start with xml version
    assert FEED.startswith('<?xml version="1.0" encoding="utf-8"?>')

    # XML namespace should be Atom
    assert '<feed xmlns="http://www.w3.org/2005/Atom">' in FEED

    # Title should be website name - tagline (amps must be escaped)
    assert '<title>Test website name - test tag &amp; line</title>' in FEED

    # Author should be site author
    assert '<author><name>Test Author</name></author>' in FEED

    # Generator should be Magnetizer
    assert ('<generator uri="https://github.com/magnusdahlgren/magnetizer">' +
            'Magnetizer</generator>') in FEED

    # Id should be site URL
    assert '<id>https://example.com/</id>' in FEED

    # Updated should be when the latest post was updated
    assert '<updated>1998-08-02T00:00:02Z</updated>' in FEED

    # Feed should have 3 entries
    assert FEED.count('<entry>') == 3

    # Feed tag should be closed
    assert FEED.endswith('</feed>')


def test_feed_entry():
    """ Test to ensure Atom entry is correct
    """

    item = Item(TEST_WEBSITE)
    item.from_md_filename('002-article-with-h1-break-and-date.md')

    entry = item.feed_entry()

    # Entry should be nested in <entry></entry>
    assert entry.startswith('<entry>')
    assert entry.endswith('</entry>')

    # Title should be article title
    assert '<title>This should be the title - Test website name</title>' in entry

    # Link and id should both be full article URL
    assert '<link href="https://example.com/article-with-h1-break-and-date.html"/>' in entry
    assert '<id>https://example.com/article-with-h1-break-and-date.html</id>' in entry

    # Updated should be date of the article
    assert '<updated>1998-08-01T00:00:01Z</updated>' in entry

    # Summary should be article abstract (amps must be escaped)
    assert ("<summary>This text should always be here Don't show this bit on " +
            "the index page</summary>") in entry


def test_write_feed_from_directory():
    """ Test to ensure Atom feed is correct when generated from files in a directory
    """


    TEST_WEBSITE.wipe()

    atom = Atom(TEST_WEBSITE)
    atom.write()

    with open(TEST_WEBSITE.config.value('output_path') + 'atom.xml', 'r') as myfile:
        feed = myfile.read()

    # Feed should be atom feed
    assert '<feed xmlns="http://www.w3.org/2005/Atom">' in feed

    # Feed should contain a number of articles
    assert feed.count('<entry>') >= 3

    TEST_WEBSITE.wipe()
