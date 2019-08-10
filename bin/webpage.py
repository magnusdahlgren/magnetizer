from website import *
from template import *
from blogpost import *
from markdown import markdown
from os import listdir


class Webpage:

    def __init__(self, website):
        
        self.website  = website
        self.template = Template(website.config.value('template_path') + website.config.value('webpage_template_filename'))
        self.filename = None
        self.html     = None
        self.title    = None

    
    def read(self, filename):

        blogpost = Blogpost(self.website)
        blogpost.read(filename)

        self.filename = blogpost.filename
        self.title = blogpost.title + ' - ' + self.website.config.value('website_name')
        self.html = self.template.template.replace(self.website.tag['content'], blogpost.html_full, 1)
        self.html = self.html.replace(self.website.tag['index_header'], '')
        self.html = self.html.replace(self.website.tag['title'], self.title, 1)


    def read_multiple(self, filenames):

        blogpost = Blogpost(self.website)
        html = ''

        for filename in filenames:
            blogpost.read(filename)
            html += blogpost.html

        self.title = self.website.config.value('website_name') + ' - ' + self.website.config.value('website_tagline')
        self.html = self.template.template.replace(self.website.tag['content'], html, 1)
        self.html = self.html.replace(self.website.tag['title'], self.title, 1)
        self.html = self.html.replace(self.website.tag['index_header'], self.website.index_header)


    def write(self):

        with open(self.website.config.value('output_path') + self.filename, 'w') as myfile:
            myfile.write(self.html)


    @staticmethod
    def write_webpages_from_filenames(website, filenames):

        print('### Generating files: ' + website.config.value('source_path') + ' --> ' + website.config.value('output_path'))

        for filename in filenames: 

            webpage = Webpage(website)
            webpage.read(filename)
            webpage.write()

            print('  Generated: ' + webpage.filename) 


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
        webpage.write()

        print('  Generated: ' + webpage.filename + ' (index)')


    @staticmethod
    def filenames_from_directory(directory):

        return sorted(listdir(directory), reverse=True)