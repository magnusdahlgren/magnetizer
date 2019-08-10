from template import *
from markdown import markdown
from re import sub
from datetime import *
from re import search


class Article:

    def __init__(self, website):
        
        self.website = website
        self.template = Template(website, website.config.value('template_path') + website.config.value('article_template_filename'))
        self.md = None
        self.filename = None
        self.title = None
        self.footer = website.article_footer
        self.html = None
        self.html_full = None
        self.date = None


    def read(self, filename):

        with open(self.website.config.value('source_path') + filename, 'r') as myfile:
            self.md = myfile.read()

        self.filename  = filename.split('-', 1)[1].split('.', 1)[0] + '.html'
        self.title     = self.title_from_markdown_source(self.md)
        self.date = self.date_from_markdown_source()

        self.html_full = self.template.render(self.website, markdown(self.md))
        self.html_full = self.html_full.replace(self.website.tag['article_footer'], self.footer, 1)
        self.html_full = self.html_full.replace(self.website.tag['break'], '', 1)

        s = self.md.split(self.website.tag['break'], maxsplit=1)[0]

        # Show 'read more' if post has been abbreviated  
        if s != self.md:
            readmore = "<a href='" + self.filename + "'>Read more</a>"
        else:
            readmore = ""

        self.html = markdown(s) + readmore
        self.html = Article.turn_first_row_into_link_if_h1(self.html, self.filename)
        self.html = self.template.render(self.website, self.html)
        self.html = self.html.replace(self.website.tag['article_footer'], '', 1)

        if self.date is not None:

            self.html_full = self.html_full.replace(self.website.tag['date'], "<date class='magnetizer-date'>" + self.date + "</date>", 1)

            # date in short html should be a link
            self.html = self.html.replace(self.website.tag['date'], "<date class='magnetizer-date'>" + Article.make_it_a_link(self.date, self.filename) + "</date>", 1)

        # Remove all remaining comment tags from html
        self.html = sub(r'<!--(.*?)-->', '', self.html)
        self.html_full = sub(r'<!--(.*?)-->', '', self.html_full)

 
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

 
    def date_from_markdown_source(self):

        match = search(r'.*<!-- (\d\d?/\d\d?/\d\d\d\d?) -->.*', self.md)

        if match:
            date = datetime.strptime(match[1], '%d/%m/%Y')
            return date.strftime('%-d %B %Y')
        else:
            return None

    
    @staticmethod
    def turn_first_row_into_link_if_h1(html, url):

        rows = html.split('\n', 1)

        if rows[0].startswith('<h1>'):
            rows[0] = rows[0].replace('<h1>', '')
            rows[0] = rows[0].replace('</h1>', '')
            rows[0] = "<h1>" + Article.make_it_a_link(rows[0], url) + "</h1>"

        return '\n'.join(rows)


    @staticmethod
    def make_it_a_link(text, url):

        return "<a href='" + url + "'>" + text + "</a>"