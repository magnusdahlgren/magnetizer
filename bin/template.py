from config import *

class Template:

    MAGNETIZER_CONTENT_TAG = "<!-- MAGNETIZER_CONTENT -->"

    def __init__(self, filename):

        if filename is not None:

            with open(filename, 'r') as myfile:
                self.template = myfile.read()

        else:
            self.template = Template.MAGNETIZER_CONTENT_TAG

    def render(self, html):
        
        return self.template.replace(Template.MAGNETIZER_CONTENT_TAG, html, 1)
