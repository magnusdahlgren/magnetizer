""" Main module for Magnetizer to trigger generation of all pages.

Usage:

$ python magnetizer.py -config magnetizer.cfg

"""

from sys import argv
from webpage import Webpage
from website import Website
from atom import Atom

def main():
    """ Main method to trigger generation of all pages
    """

    if len(argv) == 3 and argv[1] == '-config':
        config_filename = argv[2]
    else:
        config_filename = '../config/magnetizer.cfg'

    print('Using config ' + config_filename + '...')

    website = Website(config_filename)
    website.wipe()

    Webpage.write_homepage_from_directory(website, website.config.value('source_path'))
    Webpage.write_list_pages_from_directory(website, website.config.value('source_path'))
    Webpage.write_item_pages_from_directory(website, website.config.value('source_path'))

    website.copy_resources()
    website.sitemap.write(website.config.value('output_path'))

    atom = Atom(website)
    atom.write()

if __name__ == "__main__":
    main()
