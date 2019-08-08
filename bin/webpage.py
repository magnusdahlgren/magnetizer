from website import *
from template import *
from blogpost import *
from markdown import markdown
from os import listdir



class Webpage:

    def __init__(self, website):
        
        self.website  = website
        self.template = Template(website.config_template_path + website.template_webpage)
        self.filename = None
        self.html     = None
        self.title    = None

    
    def read(self, filename):

        blogpost = Blogpost(self.website)
        blogpost.read(filename)

        self.filename = blogpost.filename
        self.title = blogpost.title + ' - ' + self.website.name
        self.html = self.template.template.replace(self.website.magnetizer_content_tag, blogpost.html_full, 1)
        self.html = self.html.replace(self.website.magnetizer_index_header_tag, '')

        self.html = self.html.replace(self.website.magnetizer_title_tag, self.title, 1)


    def read_multiple(self, filenames):

        blogpost = Blogpost(self.website)
        html = ''

        for filename in filenames:
            blogpost.read(filename)
            html += blogpost.html

        self.title = self.website.name + ' - ' + self.website.tagline
        self.html = self.template.template.replace(self.website.magnetizer_content_tag, html, 1)
        self.html = self.html.replace(self.website.magnetizer_title_tag, self.title, 1)
        self.html = self.html.replace(self.website.magnetizer_index_header_tag, self.website.index_header)


    def write(self):

        with open(self.website.config_output_path + self.filename, 'w') as myfile:
            myfile.write(self.html)



    @staticmethod
    def write_webpages_from_filenames(website, filenames):

        for filename in filenames: 

            webpage = Webpage(website)
            webpage.read(filename)
            webpage.write()

            print('Generated: ' + webpage.filename) 


    @staticmethod
    def write_webpages_from_directory(website, directory):

        filenames = Webpage.filenames_from_directory(directory)        
        Webpage.write_webpages_from_filenames(website, filenames)


    @staticmethod
    def write_index_page_from_directory(website, directory):

        filenames = Webpage.filenames_from_directory(directory)        
        webpage = Webpage(website)

        webpage.read_multiple(filenames)
        webpage.filename = 'index.html'
        webpage.title = '(TBD)'
        webpage.write()

        print('Generated: ' + webpage.filename) 


   
    @staticmethod
    def filenames_from_directory(directory):

        return sorted(listdir(directory), reverse=True)