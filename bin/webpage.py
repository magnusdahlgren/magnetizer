from template import *
from markdown import markdown

TEMPLATE_CONTENT = "<!-- MAGNETIZER_CONTENT -->"

class Webpage:

    def __init__(self, template):
        
        self.template = template
        self.md = None

    def read(self, filename):

        with open('../content/' + filename, 'r') as myfile:
            self.md = myfile.read()

    def write(self):

        with open('../public/my-post.html', 'w') as myfile:
            myfile.write(self.html())

    def html(self):

        return self.template.template.replace(TEMPLATE_CONTENT, markdown(self.md), 1)

