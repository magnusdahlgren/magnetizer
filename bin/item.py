import html
from re import sub
from re import search
from datetime import datetime
from markdown import markdown
from template import *
from mutil import *


class Item:

    ARTICLE_ITEM = "magnetizer-article-item"
    STATIC_ITEM = "magnetizer-static-item"

    ARTICLE_ITEM_TEMPLATE_FILENAME = "_article_item_template.html"
    STATIC_ITEM_TEMPLATE_FILENAME = "_static_item_template.html"

    def __init__(self, website):

        self.website = website
        self.template = None
        self.markdown_source = None
        self.filename = None
        self.html_summary = None
        self.html_full = None
        self.date_html = None
        self.date = None
        self.type = None
        self.indexable = True


    def from_md_filename(self, filename):
        """Populate Item with contents from file.

        Keyword arguments:
        filename -- the filename, without any path
        """

        if filename.split('.', 1)[1] == 'md':

            with open(self.website.config.value('source_path') + filename, 'r') as myfile:
                self.markdown_source = myfile.read()

            if self.is_valid():

                filename = filename.split('.', 1)[0] + '.html'

                # Remove first part of filename if it is a number
                if filename.split('-', 1)[0].isdigit():
                    filename = filename.split('-', 1)[1]
                    self.type = Item.ARTICLE_ITEM
                else:
                    self.type = Item.STATIC_ITEM

                self.template = Template(self.website.tag['content'],
                                         self.website.config.value('template_path') +
                                         self.template_filename())

                self.filename = filename

                if self.website.tag['noindex'] in self.markdown_source:
                    self.indexable = False

                self.html_full = self.template.render(markdown(self.markdown_source))

                if self.type == Item.STATIC_ITEM:
                    self.date = None
                    self.date_html = None

                    self.html_full = self.html_full.replace(
                        self.website.tag['item_footer'],
                        self.website.static_item_footer_html, 1)

                else:
                    self.date = self.date_from_markdown_source()
                    self.date_html = self.date_html_from_date()

                    self.html_full = self.html_full.replace(
                        self.website.tag['item_footer'],
                        self.website.article_item_footer_html, 1)

                self.html_full = self.html_full.replace(self.website.tag['break'], '')

                if self.html_full.count(self.website.tag['creative_commons']) > 0:

                    self.html_full = self.html_full.replace(
                        self.website.tag['cc_here'], self.cc_license(), 1)

                    self.html_full = self.html_full.replace(
                        self.website.tag['creative_commons'], '')

                s = self.markdown_source.split(self.website.tag['break'], maxsplit=1)[0]

                # Show 'read more' if post has been abbreviated
                if s != self.markdown_source:
                    readmore = "<a href='%s' class='magnetizer-more'>Read more</a>" % \
                        self.filename
                else:
                    readmore = ""

                self.html_summary = markdown(s) + readmore
                self.html_summary = MUtil.link_h1(self.html_summary, self.filename)
                self.html_summary = MUtil.downgrade_headings(self.html_summary)
                self.html_summary = self.template.render(self.html_summary)
                self.html_summary = self.html_summary.replace(
                    self.website.tag['item_footer'], '', 1)
                self.html_summary = sub(r'<!-- MAGNETIZER_INCLUDE (.*?)-->', '', self.html_summary)

                if self.date_html is not None:

                    self.html_full = self.html_full.replace(
                        self.website.tag['date'], self.date_html, 1)

                    # date in short html should be a link
                    self.html_summary = self.html_summary.replace(
                        self.website.tag['date'],
                        MUtil.wrap_it_in_a_link(self.date_html, self.filename), 1)

                return True

            else:

                print(colours.ERROR + ' (!) ' + colours.END +
                      "'%s' must include exactly one h1 and a date)" % filename)

                return False

        else:
            return False


    def title(self):
        """Identify the title for the Item, i.e. the contents of the first <h1>."""

        title = "Untitled"

        if self.html_full is not None:

            match = re.search(r"<h1>(.*?)<\/h1>", self.html_full)

            if match:
                title = MUtil.strip_tags_from_html(match.group(1))

        return '%s - %s' % (title, self.website.config.value('website_name'))


    def meta_description(self):
        """Identify the meta_description for the Item, i.e. the contents of the
        <!-- META_DESCRIPTION --> tag."""

        match = re.search(r"<!-- *META_DESCRIPTION *= *(.*?) *-->", self.markdown_source)

        if match:
            return match.group(1)

        return None


    def feed_entry(self):
        """Returns an Atom feed entry for the item"""

        full_url = '%s/%s' % (self.website.config.value('website_base_url'), self.filename)

        entry = '<entry>'
        entry += '<title>%s</title>' % html.escape(self.title(), False)
        entry += '<link href="%s"/>' % full_url
        entry += '<id>%s</id>' % full_url
        entry += '<updated>%sT00:00:01Z</updated>' % self.date
        entry += '<summary>%s</summary>' % html.escape(self.abstract(), False)
        entry += '</entry>'

        return entry


    def date_html_from_date(self):
        """Renders a html <time> element based on the item's date.
        e.g. "<time datetime='2019-08-03'>3 August 2019</time>"""

        if self.date is not None:
            result = "<time datetime='%s'>" % self.date.isoformat()
            result += self.date.strftime('%-d %B %Y')
            result += "</time>"
            return result

        return None


    def date_from_markdown_source(self):
        """Identify the date for the Item from a comment in the markdown source,
        e.g. <!-- 24/12/2019 -->"""


        match = search(r'.*<!-- (\d\d?/\d\d?/\d\d\d\d?) -->.*', self.markdown_source)

        if match:
            return datetime.strptime(match[1], '%d/%m/%Y').date()

        return None


    def cc_license(self):
        """Renders html to show Creative Commons license information for the item"""

        cc_license = '<p class="magntetizer-license">'
        cc_license += '<a rel="license" href="http://creativecommons.org/licenses/by/4.0/">'
        cc_license += '<img alt="Creative Commons Licence" style="border-width:0" '
        cc_license += 'src="https://i.creativecommons.org/l/by/4.0/88x31.png" />'
        cc_license += '</a><br />This work by <a xmlns:cc="http://creativecommons.org/ns#" href="'
        cc_license += self.website.config.value('website_base_url') + '/' + self.filename
        cc_license += '" property="cc:attributionName" rel="cc:attributionURL">'
        cc_license += self.website.config.value('website_author')
        cc_license += '</a> is licensed under a <a rel="license" '
        cc_license += 'href="http://creativecommons.org/licenses/by/4.0/">'
        cc_license += 'Creative Commons Attribution 4.0 International License</a>.'
        cc_license += '</p>'

        return cc_license


    def twitter_card(self):
        """Generates meta data for a Twitter card for the item"""

        try:
            twitter_handle = self.website.config.value('website_twitter')

            card = '<meta name="twitter:card" content="summary_large_image" />'
            card += '<meta name="twitter:site" content="%s" />' % twitter_handle
            card += '<meta name="twitter:title" content="%s" />' % self.title()

            img_url = MUtil.first_image_url_from_html(markdown(self.markdown_source))

            card += '<meta name="twitter:description" content="%s" />' % self.abstract()

            if img_url:

                if not img_url.startswith('http'):
                    img_url = self.website.config.value('website_base_url') + '/' + img_url

                card += '<meta name="twitter:image" content="%s" />' % img_url

            return card

        except:

            print(colours.ERROR + ' (!) ' + colours.END +
                  "'website_twitter' not defined in config. Twitter cards will be disabled.")

            return ''


    def abstract(self):
        """Generate a short abstract for the item"""

        return MUtil.abstract_from_html(markdown(self.markdown_source))


    def is_valid(self):
        """Determine whether the item is valid, i.e. whether it contains a <h1> and a date."""

        return "<h1>" in markdown(self.markdown_source) and \
            search(r'.*<!-- (\d\d?/\d\d?/\d\d\d\d?) -->.*', self.markdown_source)


    def template_filename(self):
        """Determine which template to use for the item."""

        filename = None

        if self.type == Item.ARTICLE_ITEM:
            filename = Item.ARTICLE_ITEM_TEMPLATE_FILENAME
        elif self.type == Item.STATIC_ITEM:
            filename = Item.STATIC_ITEM_TEMPLATE_FILENAME

        return filename


    @staticmethod
    def html_contents_from_multiple_md_files(website, filenames):
        """Splice the html contents of the files specified into one blob of html

        Keyword Arguments:
        filenames - a list of filenames"""

        item = Item(website)
        html_content = ''

        for filename in filenames:

            if filename.split('-', 1)[0].isdigit():
                if item.from_md_filename(filename):
                    html_content += item.html_summary

        return html_content
