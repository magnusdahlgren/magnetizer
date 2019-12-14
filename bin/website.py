from os import listdir, path, remove, mkdir, rename
from config import *
import shutil
import hashlib
from mutil import *
from sitemap import *
from template import *

class Website:

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
        self.template = Template(self.tag['content'], self.config.value('template_path') + Website.WEBSITE_TEMPLATE)
        self.refresh()
                
    tag = {
        'content'           : '<!-- MAGNETIZER_CONTENT -->',
        'page_content'      : '<!-- MAGNETIZER_PAGE_CONTENT -->',
        'meta'              : '<!-- MAGNETIZER_META -->',
        'index_footer'      : '<!-- MAGNETIZER_INDEX_FOOTER -->',
        'item_footer'       : '<!-- MAGNETIZER_ARTICLE_FOOTER -->',
        'article_back_link' : '<!-- MAGNETIZER_ARTICLE_BACK_LINK -->',
        'date'              : '<!-- MAGNETIZER_DATE -->',
        'page_class'        : '<!-- MAGNETIZER_PAGE_CLASS -->',
        'pagination'        : '<!-- MAGNETIZER_PAGINATION -->',
        'cc_here'           : '<!-- MAGNETIZER_CC -->',
        'break'             : '<!-- BREAK -->',
        'noindex'           : '<!-- NOINDEX -->',
        'creative_commons'  : '<!-- CC -->'
    }

    def refresh(self):

        self.article_item_footer_html = Website.read_file(self.config.value('template_path'), self.ARTICLE_ITEM_FOOTER_TEMPLATE_FILENAME)
        self.static_item_footer_html = Website.read_file(self.config.value('template_path'), self.STATIC_ITEM_FOOTER_TEMPLATE_FILENAME)

        css_contents = Website.read_file(self.config.value('resources_path'), self.config.value('website_css_filename'))
        css_hash = hashlib.md5(bytes(css_contents, encoding='utf-8')).hexdigest()
        self.css_filename = self.config.value('website_css_filename') + '?' + css_hash


    def partial_html(self, filename):

        if path.isfile(path.join(self.config.value('template_path'), filename)):
            return Website.read_file(self.config.value('template_path'), filename)

        else:
            print (colours.ERROR + ' (!) ' + colours.END + "Include '%s' does not exist!" % filename)
            return "[ ERROR: Include '%s' does not exist! ]" % filename


    def copy_resources(self):

        print("Copying resources --> %s " % self.config.value('output_path'))
        copied = 0
        ignored = 0

        for filename in listdir(self.config.value('resources_path')):

            if path.isfile(self.config.value('resources_path') + filename):

                extension = filename.split('.')[-1]

                if '.' + extension in self.config.value('approved_filetypes'):
                    shutil.copyfile(self.config.value('resources_path') + filename , self.config.value('output_path') + filename)
                    copied += 1
                else:
                    ignored += 1

        print (colours.OK + ' --> ' + colours.END + 'Copied %s files, ignored %s' % (copied, ignored) )


    def wipe(self):

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

        print (colours.OK + ' --> ' + colours.END + 'Deleted %s files, ignored %s' % (deleted, ignored) )


    @staticmethod
    def read_file(directory, filename):

        with open(directory + filename, 'r') as myfile:
            return myfile.read()
