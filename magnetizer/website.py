""" Module representing a website.

A website consists of:
- configuartion
- a sitemap
- a website template
"""


from os import listdir, path, remove
import shutil
import hashlib
from config import Config
from sitemap import Sitemap
from template import Template
from mutil import COLOUR_OK, COLOUR_ERROR, COLOUR_END

class Website:
    """ Class representing a website
    """

    WEBSITE_TEMPLATE = '_website_template.html'

    HOMEPAGE_PAGE_TEMPLATE_FILENAME = '_homepage_page_template.html'
    LISTING_PAGE_TEMPLATE_FILENAME = '_listing_page_template.html'
    ARTICLE_PAGE_TEMPLATE_FILENAME = '_article_page_template.html'
    STATIC_PAGE_TEMPLATE_FILENAME = '_static_page_template.html'

    ARTICLE_ITEM_FOOTER_TEMPLATE_FILENAME = "_article_item_footer_template.html"
    STATIC_ITEM_FOOTER_TEMPLATE_FILENAME = "_static_item_footer_template.html"


    def __init__(self, config_file_name):

        self.config = Config(config_file_name)
        self.sitemap = Sitemap(self.config.value('website_base_url'))
        self.template = Template(self.tag['content'],
                                 self.config.value('template_path') + Website.WEBSITE_TEMPLATE)
        self.refresh()

    tag = {
        'content'           : '<!-- MAGNETIZER_CONTENT -->',
        'page_content'      : '<!-- MAGNETIZER_PAGE_CONTENT -->',
        'meta'              : '<!-- MAGNETIZER_META -->',
        'item_footer'       : '<!-- MAGNETIZER_ITEM_FOOTER -->',
        'date'              : '<!-- MAGNETIZER_DATE -->',
        'page_class'        : '<!-- MAGNETIZER_PAGE_CLASS -->',
        'pagination'        : '<!-- MAGNETIZER_PAGINATION -->',
        'cc_here'           : '<!-- MAGNETIZER_CC -->',
        'break'             : '<!-- BREAK -->',
        'noindex'           : '<!-- NOINDEX -->',
        'creative_commons'  : '<!-- CC -->'
    }

    def refresh(self):
        """ Run as part of init to populate the Website elements

        - reads item footer templates
        - calculates cache bursting checksum for css filename
        """

        self.article_footer_html = Website.read_file(self.config.value('template_path'),
                                                     self.ARTICLE_ITEM_FOOTER_TEMPLATE_FILENAME)
        self.static_footer_html = Website.read_file(self.config.value('template_path'),
                                                    self.STATIC_ITEM_FOOTER_TEMPLATE_FILENAME)

        css_contents = Website.read_file(self.config.value('resources_path'),
                                         self.config.value('website_css_filename'))
        css_hash = hashlib.md5(bytes(css_contents, encoding='utf-8')).hexdigest()
        self.css_filename = self.config.value('website_css_filename') + '?' + css_hash


    def include(self, filename):
        """ Reads the contents of an include file

        Parameters:
        - filename

        Returns:
        - the contents of the include file or an error message
        """

        if path.isfile(path.join(self.config.value('template_path'), filename)):
            return Website.read_file(self.config.value('template_path'), filename)

        print(COLOUR_ERROR + ' (!) ' + COLOUR_END + "Include '%s' does not exist!" % filename)
        return "[ ERROR: Include '%s' does not exist! ]" % filename


    def copy_resources(self):
        """ Copies resource files from the resources directory to the output directory,
        e.g. css, images etc. Files not included in approved_filetypes will be ignored.

        """

        print("Copying resources --> %s " % self.config.value('output_path'))
        copied = 0
        ignored = 0

        for filename in listdir(self.config.value('resources_path')):

            if path.isfile(self.config.value('resources_path') + filename):

                extension = filename.split('.')[-1]

                if '.' + extension in self.config.value('approved_filetypes'):
                    shutil.copyfile(self.config.value('resources_path') + filename,
                                    self.config.value('output_path') + filename)
                    copied += 1
                else:
                    ignored += 1

        message = COLOUR_OK + ' --> ' + COLOUR_END + 'Copied %s files, ignored %s'
        print(message % (copied, ignored))


    def wipe(self):
        """ Delete the files from the output directory, typically when regenerating the site.
        Ignores files not ending with .html or not in approved_filetypes.
        """

        print('Deleting previous files from %s ' % self.config.value('output_path'))
        deleted = 0
        ignored = 0

        for filename in listdir(self.config.value('output_path')):

            if path.isfile(self.config.value('output_path') + filename):
                extension = '.' + filename.split('.')[-1]

                if extension == '.html' or extension in self.config.value('approved_filetypes'):
                    remove(self.config.value('output_path') + filename)
                    deleted += 1
                else:
                    ignored += 1

        self.sitemap.clear()

        message = COLOUR_OK + ' --> ' + COLOUR_END + 'Deleted %s files, ignored %s'
        print(message % (deleted, ignored))


    @staticmethod
    def read_file(directory, filename):
        """ Helper method for reading files.
        """

        with open(directory + filename, 'r') as myfile:
            return myfile.read()
