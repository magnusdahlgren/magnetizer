import pytest
from os import listdir, path, remove
from random import *
import shutil
from magnetizer import *

test_website = Website('tests/config/test_magnetizer.cfg')
test_website.refresh()

def test_sitemap():

    base_url = 'https://example.com'

    page1 = 'example-%s.html' % randint(0, 999999)
    page2 = 'example-%s.html' % randint(0, 999999)
    page3 = 'example-%s.html' % randint(0, 999999)

    sitemap = Sitemap(base_url)

    # New sitemap should include no pages
    assert len(sitemap.pages) == 0

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

    sitemap.write(test_website.config.value('output_path'))

    with open(test_website.config.value('output_path') + 'sitemap.txt', 'r') as f:
        sitemap_from_file = f.read().splitlines()

    # sitemap written to file should contain our 3 pages
    assert len(sitemap.pages) == 4
    assert sitemap_from_file[0] == "%s/%s" % (base_url, page1)
    assert sitemap_from_file[1] == "%s/%s" % (base_url, page2)
    assert sitemap_from_file[2] == "%s/%s" % (base_url, page3)
    assert sitemap_from_file[3] == "%s/" % base_url
