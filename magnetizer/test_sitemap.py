""" Tests for sitemap.py
"""

from random import randint
from sitemap import Sitemap
from website import Website

TEST_WEBSITE = Website('tests/config/test_magnetizer.cfg')
TEST_WEBSITE.refresh()

def test_sitemap():
    """ Test of test_sitemap()
    """

    base_url = 'https://example.com'

    page1 = 'example-%s.html' % randint(0, 999999)
    page2 = 'example-%s.html' % randint(0, 999999)
    page3 = 'example-%s.html' % randint(0, 999999)

    sitemap = Sitemap(base_url)

    # New sitemap should include no pages
    assert not sitemap.pages

    sitemap.append(page1)

    # after appending one page, sitemap should contain that page and only that page
    assert len(sitemap.pages) == 1
    assert sitemap.pages[0] == "%s/%s" % (base_url, page1)

    sitemap.append(page2)
    sitemap.append(page3)

    # after appebding two more pages, sitemap should contain 3 pages
    assert len(sitemap.pages) == 3
    assert sitemap.pages[0] == "%s/%s" % (base_url, page1)
    assert sitemap.pages[1] == "%s/%s" % (base_url, page2)
    assert sitemap.pages[2] == "%s/%s" % (base_url, page3)

    sitemap.append('index.html')

    # index.html should be included as '/', without 'index.html'
    assert len(sitemap.pages) == 4
    assert sitemap.pages[3] == "%s/" % base_url

    sitemap.write(TEST_WEBSITE.config.value('output_path'))

    with open(TEST_WEBSITE.config.value('output_path') + 'sitemap.txt', 'r') as my_file:
        sitemap_from_file = my_file.read().splitlines()

    # sitemap written to file should contain our 3 pages
    assert len(sitemap.pages) == 4
    assert sitemap_from_file[0] == "%s/%s" % (base_url, page1)
    assert sitemap_from_file[1] == "%s/%s" % (base_url, page2)
    assert sitemap_from_file[2] == "%s/%s" % (base_url, page3)
    assert sitemap_from_file[3] == "%s/" % base_url
