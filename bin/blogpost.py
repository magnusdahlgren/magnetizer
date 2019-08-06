from template import *
from markdown import markdown
from re import sub


class Blogpost:

    def __init__(self, website):
        
        self.website = website
        self.template = Template(website.config_template_path + website.template_blogpost)
        self.md = None
        self.filename = None
        self.title = None


    def read(self, filename):

        with open(self.website.config_source_path + filename, 'r') as myfile:
            self.md = myfile.read()

        self.html = self.template.render(markdown(self.md))
        self.filename = filename.split('-', 1)[1].split('.', 1)[0] + '.html'
        self.title = self.title_from_markdown_source(self.md)

    
    def title_from_markdown_source(self, md):

        rows = md.split('\n')

        for row in rows:
            candidate = row
            candidate = markdown(candidate)
            candidate = sub('<[^>]*>', '', candidate)
            candidate = candidate.strip()
            if candidate != '':
                return candidate

        return 'Untitled'

