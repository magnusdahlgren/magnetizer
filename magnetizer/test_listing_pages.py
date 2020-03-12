""" Tests for listing pages (webpage.py)
"""

from os import path, remove, makedirs
from webpage import Webpage
from website import Website

TEST_WEBSITE = Website('tests/config/test_magnetizer.cfg')
TEST_WEBSITE.refresh()

TEST_WEBSITE.config.set('source_path', 'tests/temp/')

def test_single_list_page():
    """ Test when there is just one listing page, so no pagination etc
    """

    TEST_WEBSITE.wipe()
    _clean_up_test_items_md()
    _generate_test_items_md(4)
    _generate_non_indexable_test_items_md()

    Webpage.write_list_pages_from_directory(TEST_WEBSITE, TEST_WEBSITE.config.value('source_path'))

    # There should be exactly 1 blog-n.html files
    assert path.isfile(TEST_WEBSITE.config.value('output_path') + 'blog-1.html')
    assert not path.isfile(TEST_WEBSITE.config.value('output_path') + 'blog-2.html')

    with open(TEST_WEBSITE.config.value('output_path') + 'blog-1.html', 'r') as myfile:
        blog_1_content = myfile.read()

    assert blog_1_content.count('<article>') == 4
    assert 'Article 4.' in blog_1_content
    assert 'Article 3.' in blog_1_content
    assert 'Article 2.' in blog_1_content
    assert 'Article 1.' in blog_1_content

    # Page should use listing page template
    assert '<p>Listing page template</p>' in blog_1_content

    # Index title = "Website Name - Page 1"
    assert 'Test website name - test tag & line' in blog_1_content

    # Don't show article footers on list page
    assert '<footer>footer</footer>' not in blog_1_content

    # Body should have class='magnetizer-listing-page'
    assert "<body class='magnetizer-listing-page'>" in blog_1_content

    # Twitter card should *not* be present
    assert '<meta name="twitter:card" content="summary" />' not in blog_1_content

    # Link to Atom feed should be present
    assert ('<link rel="alternate" type="application/rss+xml" ' +
            'href="https://example.com/atom.xml" />') in blog_1_content

    # No links previous/next page should be present
    assert 'class="magnetizer-pagination"' not in blog_1_content
    assert 'class="magnetizer-previous"' not in blog_1_content
    assert 'class="magnetizer-next"' not in blog_1_content

    # The blog-1 page should be present in the sitemap
    assert 'https://example.com/blog-1.html' in TEST_WEBSITE.sitemap.pages


def test_three_paginated_list_pages():
    """ Test 3 listing pages, with pagination
    """

    TEST_WEBSITE.wipe()
    _clean_up_test_items_md()
    _generate_test_items_md(10)

    Webpage.write_list_pages_from_directory(TEST_WEBSITE, TEST_WEBSITE.config.value('source_path'))

    # There should be exactly 3 blog-n.html files
    assert path.isfile(TEST_WEBSITE.config.value('output_path') + 'blog-1.html')
    assert path.isfile(TEST_WEBSITE.config.value('output_path') + 'blog-2.html')
    assert path.isfile(TEST_WEBSITE.config.value('output_path') + 'blog-3.html')
    assert not path.isfile(TEST_WEBSITE.config.value('output_path') + 'blog-4.html')

    with open(TEST_WEBSITE.config.value('output_path') + 'blog-1.html', 'r') as myfile:
        blog_1_content = myfile.read()

    with open(TEST_WEBSITE.config.value('output_path') + 'blog-2.html', 'r') as myfile:
        blog_2_content = myfile.read()

    with open(TEST_WEBSITE.config.value('output_path') + 'blog-3.html', 'r') as myfile:
        blog_3_content = myfile.read()

    assert blog_1_content.count('<article>') == 4
    assert 'Article 10.' in blog_1_content
    assert 'Article 9.' in blog_1_content
    assert 'Article 8.' in blog_1_content
    assert 'Article 7.' in blog_1_content
    assert '<p>Listing page template</p>' in blog_1_content


    assert blog_2_content.count('<article>') == 4
    assert 'Article 6.' in blog_2_content
    assert 'Article 5.' in blog_2_content
    assert 'Article 4.' in blog_2_content
    assert 'Article 3.' in blog_2_content
    assert '<p>Listing page template</p>' in blog_2_content

    assert blog_3_content.count('<article>') == 2
    assert 'Article 2.' in blog_3_content
    assert 'Article 1.' in blog_3_content
    assert '<p>Listing page template</p>' in blog_3_content


    # Page title = "Website Name - Page n"
    assert 'Test website name - test tag & line' in blog_1_content
    assert '<title>Test website name - Page 2</title>' in blog_2_content
    assert '<title>Test website name - Page 3</title>' in blog_3_content

    # First page should have link to older posts but not newer
    assert '<a href="blog-2.html" class="magnetizer-next">Older posts</a>' in blog_1_content
    assert 'class="magnetizer-previous"' not in blog_1_content

    # Middle page should have link to older posts and newer
    assert '<a href="blog-3.html" class="magnetizer-next">Older posts</a>' in blog_2_content
    assert '<a href="blog-1.html" class="magnetizer-previous">Newer posts</a>' in blog_2_content

    # Last page should have link to newer posts but not older
    assert 'class="magnetizer-next"' not in blog_3_content
    assert '<a href="blog-2.html" class="magnetizer-previous">Newer posts</a>' in blog_3_content

    # The blog-n pages should be present in the sitemap
    assert 'https://example.com/blog-1.html' in TEST_WEBSITE.sitemap.pages
    assert 'https://example.com/blog-2.html' in TEST_WEBSITE.sitemap.pages
    assert 'https://example.com/blog-3.html' in TEST_WEBSITE.sitemap.pages

def test_pagination_none():
    """ Test that webpage.pagination_html() returns None when no pagination needed
    """

    webpage = Webpage(TEST_WEBSITE)
    assert webpage.pagination_html() is None

def test_pagination_next_only():
    """ Test that webpage.pagination_html() returns next page correctly when no
    previous page
    """

    webpage = Webpage(TEST_WEBSITE)
    webpage.url_next = 'page-2.html'

    result = '<nav class="magnetizer-pagination"><ul>'
    result += '<li><a href="page-2.html" class="magnetizer-next">Older posts</a></li>'
    result += '</ul></nav>'

    assert webpage.pagination_html() == result

def test_pagination_previous_only():
    """ Test that webpage.pagination_html() returns previous page correctly when no
    next page
    """
    webpage = Webpage(TEST_WEBSITE)
    webpage.url_previous = 'page-1.html'

    result = '<nav class="magnetizer-pagination"><ul>'
    result += '<li><a href="page-1.html" class="magnetizer-previous">Newer posts</a></li>'
    result += '</ul></nav>'

    assert webpage.pagination_html() == result

def test_pagination_previous_and_next():
    """ Test that webpage.pagination_html() returns next and previous pages correctly
    when both are available
    """

    webpage = Webpage(TEST_WEBSITE)
    webpage.url_previous = 'page-3.html'
    webpage.url_next = 'page-5.html'

    result = '<nav class="magnetizer-pagination"><ul>'
    result += '<li><a href="page-3.html" class="magnetizer-previous">Newer posts</a></li>'
    result += '<li><a href="page-5.html" class="magnetizer-next">Older posts</a></li>'
    result += '</ul></nav>'

    assert webpage.pagination_html() == result


def _generate_non_indexable_test_items_md():

    for counter in range(1, 6):

        markdown_data = '# Ignore me %s.\n<!-- %s/1/1998 -->' % (counter, counter)
        filename = 'ignore-test-item-%s.md' % counter

        with open(TEST_WEBSITE.config.value('source_path') + filename, 'w') as myfile:
            myfile.write(markdown_data)


def _generate_test_items_md(number_of_posts):

    if not path.exists(TEST_WEBSITE.config.value('source_path')):
        makedirs(TEST_WEBSITE.config.value('source_path'))

    for counter in range(1, number_of_posts + 1):

        markdown_data = '# Article %s.\n<!-- %s/1/1998 -->' % (counter, counter)
        filename = str(counter).zfill(3) + '-test-item-%s.md' % counter

        with open(TEST_WEBSITE.config.value('source_path') + filename, 'w') as myfile:
            myfile.write(markdown_data)


def _clean_up_test_items_md():

    for counter in range(1, 50):

        filename = str(counter).zfill(3) + '-test-item-%s.md' % counter

        if path.isfile(TEST_WEBSITE.config.value('source_path') + filename):
            remove(TEST_WEBSITE.config.value('source_path') + filename)
