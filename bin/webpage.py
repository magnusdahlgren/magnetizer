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
        self.title = blogpost.title       
        self.html = self.template.template.replace(self.website.magnetizer_content_tag, blogpost.html, 1)

        self.html = self.html.replace(self.website.magnetizer_title_tag, self.title, 1)


    def write(self):

        with open(self.website.config_output_path + self.filename, 'w') as myfile:
            myfile.write(self.html)



    @staticmethod
    def write_webpages_from_filenames(website, filenames):

        # template = Template('_page.html')

        for filename in filenames: 

            webpage = Webpage(website)
            webpage.read(filename)
            webpage.write()

            print('Generated: ' + filename) 


    @staticmethod
    def write_webpages_from_directory(website, directory):

        filenames = sorted(listdir(directory), reverse=True)
        Webpage.write_webpages_from_filenames(website, filenames)

   