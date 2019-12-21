from config import *

class Template:

    def __init__(self, content_tag, filename):

        self.content_tag = content_tag

        if filename is not None:
            with open(filename, 'r') as myfile:
                self.template = myfile.read()
        else:
            self.template = self.content_tag

    def render(self, html):

        return self.template.replace(self.content_tag, html, 1)
