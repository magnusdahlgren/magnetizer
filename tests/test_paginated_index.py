import pytest
from webpage import *
from website import *
from random import *
from os import listdir, path, remove
import shutil

test_website = Website('../tests/config/test_magnetizer.cfg')
test_website.refresh()

test_website.config.set('source_path', '../tests/temp/')

def test_single_list_page():

    test_website.wipe()
    clean_up_test_articles_md()
    generate_test_articles_md(4)
    generate_non_indexable_test_articles_md()

    Webpage.write_list_pages_from_directory(test_website, test_website.config.value('source_path'))

    # There should be exactly 1 blog-n.html files
    assert path.isfile(test_website.config.value('output_path') + 'blog-1.html')
    assert not path.isfile(test_website.config.value('output_path') + 'blog-2.html')

    with open(test_website.config.value('output_path') + 'blog-1.html', 'r') as myfile:
        blog_1_content = myfile.read()

    assert blog_1_content.count('<article>') == 4
    assert 'Article 4.' in blog_1_content 
    assert 'Article 3.' in blog_1_content 
    assert 'Article 2.' in blog_1_content
    assert 'Article 1.' in blog_1_content

    # Homepage header should not be present
    assert '<div>header</div>' not in blog_1_content

    # Index title = "Website Name - Page 1"
    assert '<title>Test website name - Page 1</title>' in blog_1_content

    # Don't show article footers on list page 
    assert '<footer>footer</footer>' not in blog_1_content

    # Body should have class='magnetizer-list'
    assert "<body class='magnetizer-homepage'>" in blog_1_content

    # Twitter card should *not* be present (todo: yet!)
    assert '<meta name="twitter:card" content="summary" />' not in blog_1_content

    # Link to Atom feed should be present
    assert '<link rel="alternate" type="application/rss+xml" href="https://example.com/atom.xml" />' in blog_1_content

    # No links previous/next page should be present
    # assert 'class="magnetizer-pagination"' not in blog_1_content
    # assert 'class="magnetizer-newer"' not in blog_1_content
    # assert 'class="magnetizer-older"' not in blog_1_content


def test_three_paginated_list_pages():

    test_website.wipe()
    clean_up_test_articles_md()
    generate_test_articles_md(10)

    Webpage.write_list_pages_from_directory(test_website, test_website.config.value('source_path'))

    # There should be exactly 3 blog-n.html files
    assert path.isfile(test_website.config.value('output_path') + 'blog-1.html')
    assert path.isfile(test_website.config.value('output_path') + 'blog-2.html')
    assert path.isfile(test_website.config.value('output_path') + 'blog-3.html')
    assert not path.isfile(test_website.config.value('output_path') + 'blog-4.html')

    with open(test_website.config.value('output_path') + 'blog-1.html', 'r') as myfile:
        blog_1_content = myfile.read()

    with open(test_website.config.value('output_path') + 'blog-2.html', 'r') as myfile:
        blog_2_content = myfile.read()

    with open(test_website.config.value('output_path') + 'blog-3.html', 'r') as myfile:
        blog_3_content = myfile.read()

    assert blog_1_content.count('<article>') == 4
    assert 'Article 10.' in blog_1_content 
    assert 'Article 9.' in blog_1_content 
    assert 'Article 8.' in blog_1_content
    assert 'Article 7.' in blog_1_content

    assert blog_2_content.count('<article>') == 4
    assert 'Article 6.' in blog_2_content 
    assert 'Article 5.' in blog_2_content 
    assert 'Article 4.' in blog_2_content
    assert 'Article 3.' in blog_2_content

    assert blog_3_content.count('<article>') == 2
    assert 'Article 2.' in blog_3_content 
    assert 'Article 1.' in blog_3_content 

    # Page title = "Website Name - Page n"
    assert '<title>Test website name - Page 1</title>' in blog_1_content
    assert '<title>Test website name - Page 2</title>' in blog_2_content
    assert '<title>Test website name - Page 3</title>' in blog_3_content

    # First page should have link to older posts but not newer
    # assert '<a href="blog-2.html" class="magnetizer-older">Older posts</a>' in blog_1_content
    # assert 'class="magnetizer-newer"' not in blog_1_content

    # Middle page should have link to older posts and newer
    # assert '<a href="blog-3.html" class="magnetizer-older">Older posts</a>' in blog_2_content
    # assert '<a href="blog-1.html" class="magnetizer-newer">Newer posts</a>' in blog_2_content

    # Last page should have link to newer posts but not older
    # assert 'class="magnetizer-older"' not in blog_2_content
    # assert '<a href="blog-2.html" class="magnetizer-newer">Newer posts</a>' in blog_2_content

def test_pagination_none():

    webpage = Webpage(test_website)
    assert webpage.pagination_html() == None

def test_pagination_next_only():

    webpage = Webpage(test_website)
    webpage.url_next = 'page-2.html'

    result = '<nav class="magnetizer-pagination"><ul>'
    result += '<li class="magnetizer-next"><a href="page-2.html">Older posts</a></li>'
    result += '</ul></nav>'

    assert webpage.pagination_html() == result

def test_pagination_previous_only():

    webpage = Webpage(test_website)
    webpage.url_previous = 'page-1.html'

    result = '<nav class="magnetizer-pagination"><ul>'
    result += '<li class="magnetizer-previous"><a href="page-1.html">Newer posts</a></li>'
    result += '</ul></nav>'

    assert webpage.pagination_html() == result

def test_pagination_previous_and_next():

    webpage = Webpage(test_website)
    webpage.url_previous = 'page-3.html'
    webpage.url_next = 'page-5.html'

    result = '<nav class="magnetizer-pagination"><ul>'
    result += '<li class="magnetizer-previous"><a href="page-3.html">Newer posts</a></li>'
    result += '<li class="magnetizer-next"><a href="page-5.html">Older posts</a></li>'
    result += '</ul></nav>'

    assert webpage.pagination_html() == result


def generate_non_indexable_test_articles_md():

    for n in range(1, 6):

        md = '# Ignore me %s.\n<!-- %s/1/1998 -->' % (n, n)
        filename = 'ignore-test-article-%s.md' % n

        with open(test_website.config.value('source_path') + filename, 'w') as myfile:
            myfile.write(md)


def generate_test_articles_md(number_of_posts):

    # delete old posts

    for n in range(1, number_of_posts + 1):

        md = '# Article %s.\n<!-- %s/1/1998 -->' % (n, n)
        filename = str(n).zfill(3) + '-test-article-%s.md' % n

        with open(test_website.config.value('source_path') + filename, 'w') as myfile:
            myfile.write(md)


def clean_up_test_articles_md():

    # Todo: Make this more generic but without risking to deleting unintended files

    for n in range(1, 50):

        filename = str(n).zfill(3) + '-test-article-%s.md' % n

        if path.isfile(test_website.config.value('source_path') + filename):
            remove(test_website.config.value('source_path') + filename)


