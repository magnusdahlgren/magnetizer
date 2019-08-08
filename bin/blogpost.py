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
        self.footer = website.blogpost_footer
        self.html = None

        self.html_full = None
        self.html_short_version = None


    def read(self, filename):

        with open(self.website.config_source_path + filename, 'r') as myfile:
            self.md = myfile.read()

        self.filename = filename.split('-', 1)[1].split('.', 1)[0] + '.html'
        self.title = self.title_from_markdown_source(self.md)

        self.html_full = self.template.render(markdown(self.md))
        self.html_full = self.html_full.replace(self.website.magnetizer_blogpost_footer_tag, self.footer, 1)
        self.html_full = self.html_full.replace(self.website.magnetizer_break_tag, '', 1)

        s = self.md.split(self.website.magnetizer_break_tag, maxsplit=1)[0]

        if s != self.md:
            readmore = "<a href=''>Read more</a>"
        else:
            readmore = ""

        self.html = self.template.render(markdown(s) + readmore)
        self.html = self.html.replace(self.website.magnetizer_blogpost_footer_tag, '', 1)


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

