from template import *
from markdown import markdown


TEMPLATE_CONTENT = "<!-- MAGNETIZER_CONTENT -->"

class Blogpost:

    def __init__(self, template):
        
        self.template = template
        self.md = None
        self.filename = None


    def read(self, filename):

        with open('../content/' + filename, 'r') as myfile:
            self.md = myfile.read()

        output_filename = filename.split('-', 1)[1].split('.', 1)[0] + '.html'

        self.filename = output_filename


    def html(self):

        return self.template.template.replace(TEMPLATE_CONTENT, markdown(self.md), 1)

