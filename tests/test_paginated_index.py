import pytest
from webpage import *
from website import *
from random import *
from os import listdir, path, remove
import shutil

test_website = Website('../tests/config/test_magnetizer.cfg')
test_website.refresh()

test_website.config.set('source_path', '../tests/temp/')

def test_single_index_page():

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


def test_two_paginated_index_pages():

    test_website.wipe()
    clean_up_test_articles_md()
    generate_test_articles_md(5)

    Webpage.write_list_pages_from_directory(test_website, test_website.config.value('source_path'))

    # There should be exactly 2 blog-n.html files
    assert path.isfile(test_website.config.value('output_path') + 'blog-1.html')
    assert path.isfile(test_website.config.value('output_path') + 'blog-2.html')
    assert not path.isfile(test_website.config.value('output_path') + 'blog-3.html')

    with open(test_website.config.value('output_path') + 'blog-1.html', 'r') as myfile:
        blog_1_content = myfile.read()

    with open(test_website.config.value('output_path') + 'blog-2.html', 'r') as myfile:
        blog_2_content = myfile.read()

    assert blog_1_content.count('<article>') == 4
    assert 'Article 5.' in blog_1_content 
    assert 'Article 4.' in blog_1_content 
    assert 'Article 3.' in blog_1_content
    assert 'Article 2.' in blog_1_content

    assert blog_2_content.count('<article>') == 1
    assert 'Article 1.' in blog_2_content 


def test_three_paginated_index_pages():

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


