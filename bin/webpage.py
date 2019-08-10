from website import *
from template import *
from article import *
from markdown import markdown
from os import listdir


class Webpage:

    def __init__(self, website):
        
        self.website  = website
        self.template = Template(website, website.config.value('template_path') + website.config.value('webpage_template_filename'))
        self.filename = None
        self.html     = None
        self.title    = None

    
    def read(self, filename):

        article = Article(self.website)
        article.read(filename)

        self.filename = article.filename
        self.title = article.title + ' - ' + self.website.config.value('website_name')
        self.html = self.template.template.replace(self.website.tag['content'], article.html_full, 1)
        self.html = self.html.replace(self.website.tag['index_header'], '')
        self.html = self.html.replace(self.website.tag['title'], self.title, 1)


    def read_multiple(self, filenames):

        article = Article(self.website)
        html = ''

        for filename in filenames:
            article.read(filename)
            html += article.html

        self.title = self.website.config.value('website_name') + ' - ' + self.website.config.value('website_tagline')
        self.html = self.template.template.replace(self.website.tag['content'], html, 1)
        self.html = self.html.replace(self.website.tag['title'], self.title, 1)
        self.html = self.html.replace(self.website.tag['index_header'], self.website.index_header_html)


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