from website import *
from template import *
from article import *
from markdown import markdown
from os import listdir
from math import ceil


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


    def homepage_from_md_filenames(self, filenames):

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
        self.html = self.html.replace(self.website.tag['page_class'], 'magnetizer-homepage', 1)


    def list_page_from_md_filenames(self, filenames, page_no):

        article = Article(self.website)
        html = ''

        for filename in filenames:

            if filename.split('-', 1)[0].isdigit():
                if article.from_md_filename(filename):
                    html += article.html

        self.title = "%s - Page %s" % (self.website.config.value('website_name'), str(page_no))
        self.html = self.template.template.replace(self.website.tag['content'], html, 1)
        self.html = self.html.replace(self.website.tag['meta'], self.meta(), 1)
        self.html = self.html.replace(self.website.tag['page_class'], 'magnetizer-homepage', 1)


    def meta(self):

        m = '<title>%s</title>' % self.title
        m += '<link rel="alternate" type="application/rss+xml" href="%s/atom.xml" />' % self.website.config.value('website_base_url')
        return m


    def write(self):

        if self.filename is not None:
            if path.isfile(path.join(self.website.config.value('output_path'), self.filename)):
                print (colours.ERROR + ' (!) ' + colours.END + "'%s' already exists and will be overwritten" % self.filename)

            with open(self.website.config.value('output_path') + self.filename, 'w') as myfile:
                myfile.write(self.html)


    @staticmethod
    def write_article_pages_from_md_filenames(website, filenames):

        print('Generating article pages --> %s' % website.config.value('output_path'))
        generated = 0
        ignored = 0

        for filename in filenames: 

            webpage = Webpage(website)
            if webpage.article_from_md_filename(filename):
                webpage.write()
                generated += 1
            else:
                ignored +=1

        print (colours.OK + ' --> ' + colours.END + 'Generated %s articles, ignored %s files' % (generated, ignored))


    @staticmethod
    def write_article_pages_from_directory(website, directory):

        filenames = Webpage.filenames_from_directory(directory)        
        Webpage.write_article_pages_from_md_filenames(website, filenames)


    @staticmethod
    def write_homepage_from_directory(website, directory):

        filenames = Webpage.filenames_from_directory(directory)        
        webpage = Webpage(website)

        webpage.homepage_from_md_filenames(filenames)
        webpage.filename = 'index.html'
        webpage.write()

        print('Generating homepage --> %s' % website.config.value('output_path'))
        print(colours.OK + ' --> ' + colours.END + '%s' % webpage.filename)


    @staticmethod
    def write_list_pages_from_directory(website, directory):

        articles_per_page = int(website.config.value('articles_per_page'))

        filenames = MUtil.filter_out_non_article_filenames(Webpage.filenames_from_directory(directory))       
        webpage = Webpage(website)

        print('Generating %s list pages --> %s' % (str(ceil (len(filenames) / articles_per_page)), website.config.value('output_path')))

        for n in range (1, 1 + ceil (len(filenames) / articles_per_page)):
            page_filenames = filenames[articles_per_page * (n - 1 ) : articles_per_page * n]
            webpage.list_page_from_md_filenames(page_filenames, n)
            webpage.filename = 'blog-%s.html' % str(n)
            webpage.write()

        print(colours.OK + ' --> ' + colours.END + '%s etc' % webpage.filename)


    @staticmethod
    def filenames_from_directory(directory):

        return sorted(listdir(directory), reverse=True)


