from os import listdir, path, remove, mkdir, rename
from config import *
import shutil
from mutil import *

class Website:

    def __init__(self, config_file_name):

        self.config = Config(config_file_name)
        self.refresh()
                
    tag = {
        'content'           : '<!-- MAGNETIZER_CONTENT -->',
        'meta'              : '<!-- MAGNETIZER_META -->',
        'index_header'      : '<!-- MAGNETIZER_INDEX_HEADER -->',
        'article_footer'    : '<!-- MAGNETIZER_ARTICLE_FOOTER -->',
        'article_back_link' : '<!-- MAGNETIZER_ARTICLE_BACK_LINK -->',
        'date'              : '<!-- MAGNETIZER_DATE -->',
        'page_class'        : '<!-- MAGNETIZER_PAGE_CLASS -->',
        'cc_here'           : '<!-- MAGNETIZER_CC -->',
        'break'             : '<!-- BREAK -->',
        'creative_commons'  : '<!-- CC -->'
    }

    def refresh(self):
        self.article_footer_html = Website.read_file(self.config.value('template_path'), self.config.value('article_footer_template_filename'))
        self.index_header_html = Website.read_file(self.config.value('template_path'), self.config.value('index_header_template_filename'))


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

        print (colours.OK + ' --> ' + colours.END + 'Deleted %s files, ignored %s' % (deleted, ignored) )


    def generate_sitemap(self):

        print('Generating sitemap in %s' % self.config.value('output_path'))
        sitemap = []

        for filename in listdir(self.config.value('output_path')):
            
            if path.isfile(self.config.value('output_path') + filename):
                extension = '.' + filename.split('.')[-1]

                if extension == '.html':

                    if filename == 'index.html':
                        filename = ''
                        
                    sitemap.append(self.config.value('website_base_url') + '/' + filename)

        with open(self.config.value('output_path') + 'sitemap.txt', 'w') as myfile:
            myfile.write('\n'.join(sitemap))

        print (colours.OK + ' --> ' + colours.END + 'sitemap.txt (%s links)' %  len(sitemap))


    @staticmethod
    def read_file(directory, filename):

        with open(directory + filename, 'r') as myfile:
            return myfile.read()
