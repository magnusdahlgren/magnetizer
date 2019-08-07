from os import listdir, path, remove
from config import *

MAGNETIZER_CONTENT_TAG         = '<!-- MAGNETIZER_CONTENT -->'
MAGNETIZER_TITLE_TAG           = '<!-- MAGNETIZER_TITLE -->'
MAGNETIZER_BLOGPOST_FOOTER_TAG = '<!-- MAGNETIZER_BLOGPOST_FOOTER -->'

TEMPLATE_WEBPAGE  = '_page.html'
TEMPLATE_BLOGPOST = '_blogpost.html'
TEMPLATE_BLOGPOST_FOOTER = '_blogpost_footer.html'

class Website:

    def __init__(self):
        
        self.name = CONFIG_WEBSITE_NAME
        
        self.config_source_path     = CONFIG_SOURCE_PATH
        self.config_template_path   = CONFIG_TEMPLATE_PATH
        self.config_output_path     = CONFIG_OUTPUT_PATH

        self.magnetizer_content_tag = MAGNETIZER_CONTENT_TAG
        self.magnetizer_title_tag   = MAGNETIZER_TITLE_TAG
        self.magnetizer_blogpost_footer_tag = MAGNETIZER_BLOGPOST_FOOTER_TAG

        self.template_webpage       = TEMPLATE_WEBPAGE
        self.template_blogpost      = TEMPLATE_BLOGPOST
        self.template_blogpost_footer = TEMPLATE_BLOGPOST_FOOTER

        self.blogpost_footer = Website.read_file(self.config_template_path, self.template_blogpost_footer)


    def refresh(self):
        self.blogpost_footer = Website.read_file(self.config_template_path, self.template_blogpost_footer)


    def wipe(self):

        print('### Deleting html files from ' + self.config_output_path)
        for filename in listdir(self.config_output_path):
            filename_parts = filename.split('.', 1)
            if len(filename_parts) > 1 and filename_parts[1] == 'html':
                print('  x ' + filename)
                remove(self.config_output_path + filename)

    @staticmethod
    def read_file(directory, filename):

        with open(directory + filename, 'r') as myfile:
            return myfile.read()

