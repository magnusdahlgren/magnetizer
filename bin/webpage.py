from website import *
from template import *
from item import *
from markdown import markdown
from os import listdir
from math import ceil


class Webpage:

    def __init__(self, website):
        
        self.website      = website
        self.template     = Template(website, website.config.value('template_path') + website.config.value('webpage_template_filename'))
        self.filename     = None
        self.html         = None
        self.title        = None
        self.twitter_card = None
        self.url_previous = None
        self.url_next     = None
        self.meta_description = None
        self.indexable    = True

    
    def item_from_md_filename(self, filename):

        item = Item(self.website)
        
        if item.from_md_filename(filename):

            self.filename = item.filename
            self.title = item.title()
            self.indexable = item.indexable
            self.meta_description = item.meta_description()
            self.twitter_card = item.twitter_card()
            self.populate_html(item.html_full, item.type)
            return True

        else:
            return False


    def homepage_from_md_filenames(self, filenames):

        filenames = MUtil.filter_out_non_article_filenames(filenames)[0:3]
        html = Item.html_contents_from_multiple_md_files(self.website, filenames)

        self.title = "%s - %s" % (self.website.config.value('website_name'), self.website.config.value('website_tagline'))
        self.meta_description = self.website.config.value('homepage_meta_description')
        self.populate_html(html, 'magnetizer-homepage')


    def list_page_from_md_filenames(self, filenames, page_no, total_no_of_pages):

        self.title = "%s - Page %s" % (self.website.config.value('website_name'), str(page_no))

        # Show 'next' link if there is a next page
        if page_no < total_no_of_pages:
            self.url_next = 'blog-%s.html' % str(page_no + 1)

        # Show 'previous' link if there is a previous page
        if page_no > 1:
            self.url_previous = 'blog-%s.html' % str(page_no - 1)

        html = Item.html_contents_from_multiple_md_files(self.website, filenames)
        self.populate_html(html, 'magnetizer-listing')


    def populate_html_new(self, html, page_class):

        if self.twitter_card is not None:
            meta = self.meta() + self.twitter_card
        else:
            meta = self.meta()

        self.html = self.website.template # MAIN TEMPLATE
        # To do: pick the correct page_template based on page type
        self.html = self.html.replace(self.website.tag['page_content'], self.template.template)
        self.html = self.html.replace(self.website.tag['content'], html, 1)
        self.html = self.html.replace(self.website.tag['page_class'], page_class, 1)
        self.html = self.html.replace(self.website.tag['meta'], meta, 1)


    def populate_html(self, html, page_class):

        if self.twitter_card is not None:
            meta = self.meta() + self.twitter_card
        else:
            meta = self.meta()

        self.html = self.website.template.template # MAIN TEMPLATE
        # To do: pick the correct page_template based on page type
        self.html = self.html.replace(self.website.tag['page_content'], self.template.template)
        self.html = self.html.replace(self.website.tag['content'], html, 1)
        self.html = self.html.replace(self.website.tag['page_class'], page_class, 1)
        self.html = self.html.replace(self.website.tag['meta'], meta, 1)

        if page_class == 'magnetizer-homepage':
            self.html = self.html.replace(self.website.tag['index_header'], self.website.index_header_html)
            self.html = self.html.replace(self.website.tag['index_footer'], self.website.index_footer_html)

        if page_class == 'magnetizer-listing' or page_class == 'magnetizer-article-item':
            self.html = self.html.replace(self.website.tag['list_page_header'], self.website.list_page_header_html)

        if self.pagination_html() is not None:
            self.html = self.html.replace(self.website.tag['pagination'], self.pagination_html(), 1)

        includes = self.includes()

        for include in includes:
            self.html = self.html.replace('<!-- MAGNETIZER_INCLUDE %s -->' % include, self.website.partial_html(include))

        # Remove all remaining comment tags
        self.html = sub(r'<!--(.*?)-->', '', self.html)


    def meta(self):

        m = '<title>%s</title>\n' % self.title

        if self.meta_description is not None:
            m += '<meta name="description" content="%s">\n' % self.meta_description.replace('"','\\"')

        if not self.indexable:
            m += '<meta name="robots" content="noindex">'

        m += '<link rel="alternate" type="application/rss+xml" href="%s/atom.xml" />\n' % self.website.config.value('website_base_url')
        m += '<link rel="stylesheet" type="text/css" href="%s">\n' % self.website.css_filename
        return m


    def includes(self):

        return set(re.findall(r"<!-- *MAGNETIZER_INCLUDE *(.*?) *-->", self.html))


    def pagination_html(self):

        start = '<nav class="magnetizer-pagination"><ul>'
        items = ''
        end = '</ul></nav>'

        if self.url_previous is not None:
            items += '<li>'
            items += '<a href="%s" class="magnetizer-previous">Newer posts</a>' % self.url_previous
            items += '</li>'

        if self.url_next is not None:
            items += '<li>'
            items += '<a href="%s" class="magnetizer-next">Older posts</a>' % self.url_next
            items += '</li>'

        if self.url_previous is not None or self.url_next is not None:
            return start + items + end
        else:
            return None


    def write(self):

        if self.filename is not None:

            if path.isfile(path.join(self.website.config.value('output_path'), self.filename)):
                print (colours.ERROR + ' (!) ' + colours.END + "'%s' already exists and will be overwritten" % self.filename)

            with open(self.website.config.value('output_path') + self.filename, 'w') as myfile:
                myfile.write(self.html)

            self.website.sitemap.append(self.filename)


    @staticmethod
    def write_item_pages_from_md_filenames(website, filenames):

        print('Generating item pages --> %s' % website.config.value('output_path'))
        generated = 0
        ignored = 0

        for filename in filenames: 

            webpage = Webpage(website)
            if webpage.item_from_md_filename(filename):
                webpage.write()
                generated += 1
            else:
                ignored +=1

        print (colours.OK + ' --> ' + colours.END + 'Generated %s item pages, ignored %s files' % (generated, ignored))


    @staticmethod
    def write_item_pages_from_directory(website, directory):

        filenames = Webpage.filenames_from_directory(directory)        
        Webpage.write_item_pages_from_md_filenames(website, filenames)


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

        total_no_of_pages = ceil (len(filenames) / articles_per_page)

        print('Generating %s list pages --> %s' % (str(total_no_of_pages), website.config.value('output_path')))

        for n in range (1, 1 + total_no_of_pages):
            webpage = Webpage(website)
            page_filenames = filenames[articles_per_page * (n - 1 ) : articles_per_page * n]
            webpage.list_page_from_md_filenames(page_filenames, n, total_no_of_pages)
            webpage.filename = 'blog-%s.html' % str(n)
            webpage.write()

        print(colours.OK + ' --> ' + colours.END + '%s etc' % webpage.filename)


    @staticmethod
    def filenames_from_directory(directory):

        return sorted(listdir(directory), reverse=True)


