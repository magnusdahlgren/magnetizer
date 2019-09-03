import pytest
from os import listdir, path, remove
from website import *
import shutil

test_website = Website('../tests/config/test_magnetizer.cfg')
test_website.refresh()

def test_sitemap():

    test_website.wipe()

    filenames = ['index.html', 'page-1.html', 'page-2.html', 'page-3.html']

    # Create a bunch of files
    for filename in filenames:
        with open(test_website.config.value('output_path') + filename, 'w') as myfile:
            myfile.write('...')

    test_website.generate_sitemap()

    with open(test_website.config.value('output_path') + 'sitemap.txt', 'r') as myfile:
        sitemap_txt = myfile.read()

    # Sitemap should contain all the files we just created
    for filename in filenames:

        if filename == 'index.html':
            filename = '\n'

        assert 'https://example.com/' + filename in sitemap_txt

    # Sitemap should only contain the files we just created
    assert len(sitemap_txt.splitlines()) == len(filenames)
