from website import *
from template import *
from article import *
from markdown import markdown
from os import listdir


class Webpage:

    def __init__(self, website):
        
        self.website  = website
        self.template = Template(website, website.config.value('template_path') + website.config.value('webpage_template_filename'))
        self.filename = None
        self.html     = None
        self.title    = None

    
    def article_from_md_filename(self, filename):

        article = Article(self.website)
        
        if article.from_md_filename(filename):

            self.filename = article.filename
            self.title = article.title
            self.html = self.template.template.replace(self.website.tag['content'], article.html_full, 1)
            self.html = self.html.replace(self.website.tag['index_header'], '')
            self.html = self.html.replace(self.website.tag['meta'], article.meta(), 1)
            self.html = self.html.replace(self.website.tag['page_class'], 'magnetizer-article', 1)
            return True

        else:
            return False


    def index_from_md_filenames(self, filenames):

        article = Article(self.website)
        html = ''

        for filename in filenames:

            if filename.split('-', 1)[0].isdigit():
                if article.from_md_filename(filename):
                    html += article.html

        self.title = "%s - %s" % (self.website.config.value('website_name'), self.website.config.value('website_tagline'))
        self.html = self.template.template.replace(self.website.tag['content'], html, 1)
        self.html = self.html.replace(self.website.tag['meta'], self.meta(), 1)
        self.html = self.html.replace(self.website.tag['index_header'], self.website.index_header_html)
        self.html = self.html.replace(self.website.tag['page_class'], 'magnetizer-index', 1)


    def meta(self):

        m = '<title>%s</title>' % self.title
        m += '<link rel="alternate" type="application/rss+xml" href="%s/atom.xml" />' % self.website.config.value('website_base_url')
        return m


    def write(self):

        if self.filename is not None:
            with open(self.website.config.value('output_path') + self.filename, 'w') as myfile:
                myfile.write(self.html)
                print('  W  %s' % self.filename)
        else:
            print('  !  WARNING: Did not write file.')


    @staticmethod
    def write_article_pages_from_md_filenames(website, filenames):

        print('Generating article pages --> %s' % website.config.value('output_path'))

        for filename in filenames: 

            webpage = Webpage(website)
            webpage.article_from_md_filename(filename)
            webpage.write()


    @staticmethod
    def write_article_pages_from_directory(website, directory):

        filenames = Webpage.filenames_from_directory(directory)        
        Webpage.write_article_pages_from_md_filenames(website, filenames)


    @staticmethod
    def write_index_page_from_directory(website, directory):

        filenames = Webpage.filenames_from_directory(directory)        
        webpage = Webpage(website)

        webpage.index_from_md_filenames(filenames)
        webpage.filename = 'index.html'
        webpage.write()

        print('Generating index pages --> %s' % website.config.value('output_path'))
        print('  W  %s (index)' % webpage.filename)


    @staticmethod
    def filenames_from_directory(directory):

        return sorted(listdir(directory), reverse=True)