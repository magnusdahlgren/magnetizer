from template import *
from markdown import markdown

TEMPLATE_CONTENT = "<!-- MAGNETIZER_CONTENT -->"

class Webpage:

    def __init__(self, template):
        
        self.template = template
        self.md = None

    def read(self, filename):

        with open(filename, 'r') as myfile:
            self.md = myfile.read()

    def html(self):

        return self.template.template.replace(TEMPLATE_CONTENT, markdown(self.md), 1)

