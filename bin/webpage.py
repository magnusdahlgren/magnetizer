from template import *
from blogpost import *
from markdown import markdown
from os import listdir


TEMPLATE_CONTENT = "<!-- MAGNETIZER_CONTENT -->"

class Webpage:

    def __init__(self, template):
        
        self.template = template
        self.md = None
        self.filename = None

    def read(self, filename):

        with open('../content/' + filename, 'r') as myfile:
            self.md = myfile.read()

        output_filename = filename.split('-', 1)[1].split('.', 1)[0] + '.html'

        self.filename = output_filename

    def write(self):

        with open('../public/' + self.filename, 'w') as myfile:
            myfile.write(self.html())

    def html(self):

        return self.template.template.replace(TEMPLATE_CONTENT, markdown(self.md), 1)


    @staticmethod
    def write_posts_from_filenames(filenames):

        template = Template('_page.html')

        for filename in filenames: 

            webpage = Webpage(template)
            webpage.read(filename)
            webpage.write()
            print('Generated: ' + filename) 


    @staticmethod
    def write_posts_from_directory(directory):

        filenames = sorted(listdir(directory), reverse=True)
        Webpage.write_posts_from_filenames(filenames)

   