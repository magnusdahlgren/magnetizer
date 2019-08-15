from template import *
from markdown import markdown
from re import sub
from datetime import *
from re import search
from mutil import *


class Article:

    def __init__(self, website):
        
        self.website = website
        self.template = Template(website, website.config.value('template_path') + website.config.value('article_template_filename'))
        self.md = None
        self.filename = None
        self.title = None
        self.footer_html = website.article_footer_html
        self.html = None
        self.html_full = None
        self.date_html = None


    def from_md_filename(self, filename):

        if filename.split('.', 1)[1] == 'md':

            with open(self.website.config.value('source_path') + filename, 'r') as myfile:
                self.md = myfile.read()
    
            filename = filename.split('.', 1)[0] + '.html'

            # Remove first part of filename if it is a number
            if filename.split('-', 1)[0].isdigit():
                filename  = filename.split('-', 1)[1]

            self.filename  = filename
            self.title     = self.title_from_markdown_source(self.md)
            self.date_html = self.date_html_from_markdown_source()

            self.html_full = self.template.render(self.website, markdown(self.md))
            self.html_full = self.html_full.replace(self.website.tag['article_footer'], self.footer_html, 1)
            self.html_full = self.html_full.replace(self.website.tag['break'], '', 1)

            s = self.md.split(self.website.tag['break'], maxsplit=1)[0]

            # Show 'read more' if post has been abbreviated  
            if s != self.md:
                readmore = "<a href='%s'>Read more</a>" % (self.filename)
            else:
                readmore = ""

            self.html = markdown(s) + readmore
            self.html = MUtil.link_first_tag(self.html, self.filename)
            self.html = MUtil.downgrade_headings(self.html)
            self.html = self.template.render(self.website, self.html)
            self.html = self.html.replace(self.website.tag['article_footer'], '', 1)

            if self.date_html is not None:

                self.html_full = self.html_full.replace(self.website.tag['date'], self.date_html, 1)

                # date in short html should be a link
                self.html = self.html.replace(self.website.tag['date'], MUtil.wrap_it_in_a_link(self.date_html, self.filename), 1)

            # Remove all remaining comment tags from html
            self.html = sub(r'<!--(.*?)-->', '', self.html)
            self.html_full = sub(r'<!--(.*?)-->', '', self.html_full)

            return True

        else:
            print("Ignored '%s' (not a .md file)" % filename)
            return False

 
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

    
    def date_html_from_markdown_source(self):

        # e.g. "<time datetime='2019-08-03'>3 August 2019</time>"

        match = search(r'.*<!-- (\d\d?/\d\d?/\d\d\d\d?) -->.*', self.md)

        if match:
            article_date = datetime.strptime(match[1], '%d/%m/%Y').date()
            result = "<time datetime='%s'>" % article_date.isoformat()
            result += article_date.strftime('%-d %B %Y')
            result += "</time>"
            return result
        else:
            return None