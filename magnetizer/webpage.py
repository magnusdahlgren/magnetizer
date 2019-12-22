""" A module to generate .html files for the homepage, listings pages and item pages.
"""

from os import path, listdir
from math import ceil
from re import findall, sub

from mutil import MUtil, colours
from website import Website
from template import Template
from item import Item


class Webpage:
    """ A class representing a webpage
    """

    HOMEPAGE_PAGE_TYPE = "magnetizer-homepage-page"
    LISTING_PAGE_TYPE = "magnetizer-listing-page"
    ARTICLE_PAGE_TYPE = "magnetizer-article-page"
    STATIC_PAGE_TYPE = "magnetizer-static-page"


    def __init__(self, website):

        self.website = website
        self.filename = None
        self.item = None
        self.html = None
        self.title = None
        self.url_previous = None
        self.url_next = None


    def item_from_md_filename(self, filename):
        """ Creates an Item by reading a .md file

            Returns:
            True - if the file was successfully imported to an Item
            False - otherwise
        """

        success = False

        self.item = Item(self.website)

        if self.item.from_md_filename(filename):

            self.filename = self.item.filename
            self.title = self.item.title()

            if self.item.type == Item.ARTICLE_ITEM:
                page_type = Webpage.ARTICLE_PAGE_TYPE
            elif self.item.type == Item.STATIC_ITEM:
                page_type = Webpage.STATIC_PAGE_TYPE
            else:
                page_type = None

            self.populate_html(self.item.html_full, page_type)
            success = True

        return success


    def homepage_from_md_filenames(self, filenames):
        """ Populates the Webpage with homepage contents

        Parameters:
        filenames - a list of the latest articles to include on the homepage
        """

        filenames = MUtil.purge_non_article_filenames(filenames)[0:3]
        html = Item.html_contents_from_multiple_md_files(self.website, filenames)

        website_name = self.website.config.value('website_name')
        website_tagline = self.website.config.value('website_tagline')

        self.title = "%s - %s" % (website_name, website_tagline)
        self.populate_html(html, Webpage.HOMEPAGE_PAGE_TYPE)


    def listing_page_from_md_filenames(self, filenames, page_no, total_no_of_pages):
        """ Populates the Webpage with listing page contents

        Parameters:
        filenames - a list of the articles to include on the page
        page_no - which page in the pagination this is
        total_no_of_pages - how many listing pages in total there are
        """

        self.title = "%s - Page %s" % (self.website.config.value('website_name'), str(page_no))

        # Show 'next' link if there is a next page
        if page_no < total_no_of_pages:
            self.url_next = 'blog-%s.html' % str(page_no + 1)

        # Show 'previous' link if there is a previous page
        if page_no > 1:
            self.url_previous = 'blog-%s.html' % str(page_no - 1)

        html = Item.html_contents_from_multiple_md_files(self.website, filenames)
        self.populate_html(html, Webpage.LISTING_PAGE_TYPE)


    def populate_html(self, html, page_type):
        """ Inserting the page content into the appropriate template, based on what type
        of page it is.

        Parameters:
        html - the html content of the page
        page_type - the type of page
        """

        if self.item is not None:
            meta = self.meta(page_type) + self.item.twitter_card()
        else:
            meta = self.meta(page_type)

        self.html = self.website.template.template

        if page_type == Webpage.HOMEPAGE_PAGE_TYPE:
            page_template_filename = Website.HOMEPAGE_PAGE_TEMPLATE_FILENAME
        elif page_type == Webpage.LISTING_PAGE_TYPE:
            page_template_filename = Website.LISTING_PAGE_TEMPLATE_FILENAME
        elif page_type == Webpage.STATIC_PAGE_TYPE:
            page_template_filename = Website.STATIC_PAGE_TEMPLATE_FILENAME
        elif page_type == Webpage.ARTICLE_PAGE_TYPE:
            page_template_filename = Website.ARTICLE_PAGE_TEMPLATE_FILENAME
        else:
            page_template_filename = None

        template = Template(self.website,
                            self.website.config.value('template_path') + page_template_filename)

        self.html = self.html.replace(self.website.tag['page_content'], template.template)
        self.html = self.html.replace(self.website.tag['content'], html, 1)
        self.html = self.html.replace(self.website.tag['page_class'], page_type, 1)
        self.html = self.html.replace(self.website.tag['meta'], meta, 1)

        if self.pagination_html() is not None:
            self.html = self.html.replace(self.website.tag['pagination'], self.pagination_html(), 1)

        includes = self.includes()

        for include in includes:
            self.html = self.html.replace('<!-- MAGNETIZER_INCLUDE %s -->' % \
                include, self.website.include(include))

        # Remove all remaining comment tags
        self.html = sub(r'<!--(.*?)-->', '', self.html)


    def meta(self, page_type):
        """ Returns a html block of appropriate meta data for the webpage
        """

        meta_alternate = '<link rel="alternate" type="application/rss+xml" href="%s/atom.xml" />\n'
        meta_stylesheet = '<link rel="stylesheet" type="text/css" href="%s">\n'
        meta_description = '<meta name="description" content="%s">\n'

        meta_html = '<title>%s</title>\n' % self.title

        if self.meta_description(page_type) is not None:
            meta_html += meta_description % self.meta_description(page_type).replace('"', '\\"')

        if not self.is_indexable():
            meta_html += '<meta name="robots" content="noindex">'

        meta_html += meta_alternate % self.website.config.value('website_base_url')
        meta_html += meta_stylesheet % self.website.css_filename
        return meta_html

    def is_indexable(self):
        """ Determines if the page should be indexable by search engines. Only item pages
        with a noindex tag are not indexable.
        """

        if self.item is not None:
            return self.item.is_indexable()

        return True


    def meta_description(self, page_type):
        """ Determine the meta description for the web page:

        Returns:
        Item page - meta desctiption from the Item
        Homepage - homepage meta descripti0n from config
        Listing page - None
        """

        description = None

        if page_type in [Webpage.STATIC_PAGE_TYPE, Webpage.ARTICLE_PAGE_TYPE]:
            description = self.item.meta_description()
        elif page_type == Webpage.HOMEPAGE_PAGE_TYPE:
            description = self.website.config.value('homepage_meta_description')

        return description


    def includes(self):
        """ Replaces include tags in the webpage html with the appropriate includes
        """

        return set(findall(r"<!-- *MAGNETIZER_INCLUDE *(.*?) *-->", self.html))


    def pagination_html(self):
        """ Returns html for links to the next and previous page, if they exist
        """

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

        return None


    def write(self):
        """ Writes the webpage to file
        """

        if self.filename is not None:

            error = colours.ERROR + ' (!) ' + colours.END + "Overwriting existing '%s'"

            if path.isfile(path.join(self.website.config.value('output_path'), self.filename)):
                print(error % self.filename)

            with open(self.website.config.value('output_path') + self.filename, 'w') as myfile:
                myfile.write(self.html)

            self.website.sitemap.append(self.filename)


    @staticmethod
    def write_item_pages_from_md_filenames(website, filenames):
        """ Writes multiple item pages to file

        Parameters:
        filenames - the list of .md filenames to generate .html files from
        """

        print('Generating item pages --> %s' % website.config.value('output_path'))
        generated = 0
        ignored = 0

        for filename in filenames:

            webpage = Webpage(website)
            if webpage.item_from_md_filename(filename):
                webpage.write()
                generated += 1
            else:
                ignored += 1

        success = colours.OK + ' --> ' + colours.END + 'Generated %s item pages, ignored %s files'
        print(success % (generated, ignored))


    @staticmethod
    def write_item_pages_from_directory(website, directory):
        """ Writes multiple item pages to file

        Parameters:
        directory - the directory containing the .md filenames to generate .html files from
        """

        filenames = Webpage.filenames_from_directory(directory)
        Webpage.write_item_pages_from_md_filenames(website, filenames)


    @staticmethod
    def write_homepage_from_directory(website, directory):
        """ Writes the homepage to file

        Parameters:
        directory - the directory containing the .md filenames for the article listing
        on the homepage
        """

        filenames = Webpage.filenames_from_directory(directory)

        webpage = Webpage(website)
        webpage.homepage_from_md_filenames(filenames)
        webpage.filename = 'index.html'
        webpage.write()

        print('Generating homepage --> %s' % website.config.value('output_path'))
        print(colours.OK + ' --> ' + colours.END + '%s' % webpage.filename)


    @staticmethod
    def write_list_pages_from_directory(website, directory):
        """ Writes list pages to file

        Parameters:
        directory - the directory containing the .md filenames for the article listing
        """

        per_page = int(website.config.value('articles_per_page'))

        filenames = MUtil.purge_non_article_filenames(Webpage.filenames_from_directory(directory))

        total_no_of_pages = ceil(len(filenames) / per_page)

        output_path = website.config.value('output_path')
        print('Generating %s list pages --> %s' % (str(total_no_of_pages), output_path))

        for counter in range(1, 1 + total_no_of_pages):
            webpage = Webpage(website)
            page_filenames = filenames[per_page * (counter - 1) : per_page * counter]
            webpage.listing_page_from_md_filenames(page_filenames, counter, total_no_of_pages)
            webpage.filename = 'blog-%s.html' % str(counter)
            webpage.write()

        print(colours.OK + ' --> ' + colours.END + '%s etc' % webpage.filename)


    @staticmethod
    def filenames_from_directory(directory):
        """ Returns a alphabetically sorted list of filenames from a directory

        Parameters:
        directory - The directory to list the files from
        """

        return sorted(listdir(directory), reverse=True)
