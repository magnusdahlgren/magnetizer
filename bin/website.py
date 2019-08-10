from os import listdir, path, remove, mkdir, rename
from config import *
import shutil

class Website:

    def __init__(self, config_file_name):

        self.config = Config(config_file_name)
                
        self.blogpost_footer = Website.read_file(self.config.value('template_path'), self.config.value('blogpost_footer_template_filename'))
        self.index_header = Website.read_file(self.config.value('template_path'), self.config.value('index_header_template_filename'))

    tag = {
        'content'        : '<!-- MAGNETIZER_CONTENT -->',
        'title'          : '<!-- MAGNETIZER_TITLE -->',
        'index_header'   : '<!-- MAGNETIZER_INDEX_HEADER -->',
        'blogpost_footer': '<!-- MAGNETIZER_BLOGPOST_FOOTER -->',
        'date'           : '<!-- MAGNETIZER_DATE -->',
        'break'          : '<!-- BREAK -->'
    }

    def refresh(self):
        # todo: remove duplication with above
        self.blogpost_footer = Website.read_file(self.config.value('template_path'), self.config.value('blogpost_footer_template_filename'))
        self.index_header = Website.read_file(self.config.value('template_path'), self.config.value('index_header_template_filename'))


    # def move_out(self):

        archive_directory_path = self.config.value('output_path')[:-1] + '_/'
        print ('Renaming ' + self.config.value('output_path') + ' --> ' + archive_directory_path)

        shutil.rmtree(archive_directory_path, ignore_errors=True)

        rename(self.config.value('output_path'), archive_directory_path)
        mkdir(self.config.value('output_path'))
        print ('Created new directory ' + self.config.value('output_path'))


    def copy_resources(self):

        print('### Copying resources: ' + self.config.value('resources_path') + ' --> ' + self.config.value('output_path'))


        for filename in listdir(self.config.value('resources_path')):

            if path.isfile(self.config.value('resources_path') + filename):

                extension = filename.split('.')[-1]

                if '.' + extension in self.config.value('approved_filetypes'):
                    shutil.copyfile(self.config.value('resources_path') + filename , self.config.value('output_path') + filename)
                    print ('  copied: ' + filename)
                else:
                    print ('  ignored: ' + filename + ' (filetype .' + extension + ' not allowed)')


    def wipe(self):

        print('### Deleting previous files from ' + self.config.value('output_path'))
        for filename in listdir(self.config.value('output_path')):
            
            if path.isfile(self.config.value('output_path') + filename):
                extension = filename.split('.')[-1]

                if extension == 'html' or '.' + extension in self.config.value('approved_filetypes'):
                    remove(self.config.value('output_path') + filename)
                    print ('  deleted: ' + filename)
                else:
                    print ('  ignored: ' + filename + ' (filetype .' + extension + ')')

                
    @staticmethod
    def read_file(directory, filename):

        with open(directory + filename, 'r') as myfile:
            return myfile.read()

    TAG = {}

