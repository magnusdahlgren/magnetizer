from os import listdir, path, remove, mkdir, rename
from config import *
import shutil

class Website:

    def __init__(self, config_file_name):

        self.config = Config(config_file_name)
        self.refresh()
                
    tag = {
        'content'        : '<!-- MAGNETIZER_CONTENT -->',
        'title'          : '<!-- MAGNETIZER_TITLE -->',
        'index_header'   : '<!-- MAGNETIZER_INDEX_HEADER -->',
        'article_footer' : '<!-- MAGNETIZER_ARTICLE_FOOTER -->',
        'date'           : '<!-- MAGNETIZER_DATE -->',
        'break'          : '<!-- BREAK -->',
        'page_class'     : '<!-- MAGNETIZER_PAGE_CLASS -->'
    }

    def refresh(self):
        self.article_footer_html = Website.read_file(self.config.value('template_path'), self.config.value('article_footer_template_filename'))
        self.index_header_html = Website.read_file(self.config.value('template_path'), self.config.value('index_header_template_filename'))


    def copy_resources(self):

        print("Copying resources --> %s" % self.config.value('output_path'))
        for filename in listdir(self.config.value('resources_path')):

            if path.isfile(self.config.value('resources_path') + filename):

                extension = filename.split('.')[-1]

                if '.' + extension in self.config.value('approved_filetypes'):
                    shutil.copyfile(self.config.value('resources_path') + filename , self.config.value('output_path') + filename)
                    print ('  C  %s' % filename)
                else:
                    print ('  -  %s (filetype %s not allowed)' % (filename, extension))


    def wipe(self):

        print('Deleting previous files from ' + self.config.value('output_path'))
        for filename in listdir(self.config.value('output_path')):
            
            if path.isfile(self.config.value('output_path') + filename):
                extension = '.' + filename.split('.')[-1]

                if extension == '.html' or extension in self.config.value('approved_filetypes'):
                    remove(self.config.value('output_path') + filename)
                    print ('  X  %s' % filename)
                else:
                    print ('  -  %s (filetype %s)' % (filename, extension))

                
    @staticmethod
    def read_file(directory, filename):

        with open(directory + filename, 'r') as myfile:
            return myfile.read()
