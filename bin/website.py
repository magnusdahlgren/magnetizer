from os import listdir, path, remove, mkdir, rename
from config import *
import shutil

# remove
CONFIG_SOURCE_PATH    = '../content/'
CONFIG_TEMPLATE_PATH  = '../templates/'
CONFIG_RESOURCES_PATH = '../resources/'
CONFIG_OUTPUT_PATH    = '../public/'
# end remove

MAGNETIZER_CONTENT_TAG         = '<!-- MAGNETIZER_CONTENT -->'
MAGNETIZER_TITLE_TAG           = '<!-- MAGNETIZER_TITLE -->'
MAGNETIZER_INDEX_HEADER_TAG    = '<!-- MAGNETIZER_INDEX_HEADER -->'
MAGNETIZER_BLOGPOST_FOOTER_TAG = '<!-- MAGNETIZER_BLOGPOST_FOOTER -->'
MAGNETIZER_DATE_TAG            = '<!-- MAGNETIZER_DATE -->'
MAGNETIZER_BREAK_TAG           = '<!-- BREAK -->'

TEMPLATE_WEBPAGE  = '_page.html'
TEMPLATE_BLOGPOST = '_blogpost.html'
TEMPLATE_INDEX_HEADER    = '_index_header.html'
TEMPLATE_BLOGPOST_FOOTER = '_blogpost_footer.html'

class Website:

    def __init__(self, config_file_name):

        self.config = Config(config_file_name)
                
        self.config_output_path     = CONFIG_OUTPUT_PATH
        self.config_resources_path  = CONFIG_RESOURCES_PATH

        self.magnetizer_content_tag         = MAGNETIZER_CONTENT_TAG
        self.magnetizer_title_tag           = MAGNETIZER_TITLE_TAG
        self.magnetizer_index_header_tag    = MAGNETIZER_INDEX_HEADER_TAG
        self.magnetizer_blogpost_footer_tag = MAGNETIZER_BLOGPOST_FOOTER_TAG
        self.magnetizer_date_tag            = MAGNETIZER_DATE_TAG
        self.magnetizer_break_tag           = MAGNETIZER_BREAK_TAG

        self.template_webpage         = TEMPLATE_WEBPAGE
        self.template_blogpost        = TEMPLATE_BLOGPOST

        self.blogpost_footer = Website.read_file(self.config.value('template_path'), self.config.value('blogpost_footer_template_filename'))
        self.index_header = Website.read_file(self.config.value('template_path'), self.config.value('index_header_template_filename'))

    def refresh(self):
        # todo: remove duplication with above
        self.blogpost_footer = Website.read_file(self.config.value('template_path'), self.config.value('blogpost_footer_template_filename'))
        self.index_header = Website.read_file(self.config.value('template_path'), self.config.value('index_header_template_filename'))


    def move_out(self):

        archive_directory_path = self.config_output_path[:-1] + '_/'
        print ('Renaming ' + self.config_output_path + ' --> ' + archive_directory_path)

        shutil.rmtree(archive_directory_path, ignore_errors=True)

        rename(self.config_output_path, archive_directory_path)
        mkdir(self.config_output_path)
        print ('Created new directory ' + self.config_output_path)


    def copy_resources(self):

        for filename in listdir(self.config_resources_path):

            if path.isfile(self.config_resources_path + filename):

                shutil.copyfile(self.config_resources_path + filename , self.config_output_path + filename)
                print ('copied: ' + filename)


    @staticmethod
    def read_file(directory, filename):

        with open(directory + filename, 'r') as myfile:
            return myfile.read()

