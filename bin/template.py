from config import *

class Template:

    def __init__(self, website, filename):

        if filename is not None:
            with open(filename, 'r') as myfile:
                self.template = myfile.read()
        else:
            self.template = website.tag['content']

    def render(self, website, html):

        return self.template.replace(website.tag['content'], html, 1)
