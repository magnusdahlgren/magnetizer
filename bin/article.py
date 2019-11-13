import html
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
        self.date = None
        self.type = 'magnetizer-article'


    def from_md_filename(self, filename):

        if filename.split('.', 1)[1] == 'md':

            with open(self.website.config.value('source_path') + filename, 'r') as myfile:
                self.md = myfile.read()

            if self.is_valid():

                filename = filename.split('.', 1)[0] + '.html'

                # Remove first part of filename if it is a number
                if filename.split('-', 1)[0].isdigit():
                    filename  = filename.split('-', 1)[1]
                    is_special_article = False
                else:
                    is_special_article = True

                self.filename  = filename
                self.title     = '%s - %s' % (self.title_from_markdown_source(self.md), self.website.config.value('website_name'))
                self.html_full = self.template.render(self.website, markdown(self.md))

                if is_special_article:
                    back_link = '<a href="/" class="magnetizer-nav-back">Back to homepage</a>'
                    self.type = 'magnetizer-special'
                    self.date = None
                    self.date_html = None
                    self.html_full = self.html_full.replace(self.website.tag['article_footer'], '', 1)
                else:
                    back_link = '<a href="blog-1.html" class="magnetizer-nav-back">Back to blog</a>'
                    self.date      = self.date_from_markdown_source()
                    self.date_html = self.date_html_from_date()
                    self.html_full = self.html_full.replace(self.website.tag['article_footer'], self.footer_html, 1)

                self.html_full = self.html_full.replace(self.website.tag['article_back_link'], back_link)
                self.html_full = self.html_full.replace(self.website.tag['break'], '')

                if self.html_full.count(self.website.tag['creative_commons']) > 0:
                    self.html_full = self.html_full.replace(self.website.tag['cc_here'], self.cc_license(), 1)
                    self.html_full = self.html_full.replace(self.website.tag['creative_commons'], '')

                s = self.md.split(self.website.tag['break'], maxsplit=1)[0]

                # Show 'read more' if post has been abbreviated  
                if s != self.md:
                    readmore = "<a href='%s' class='magnetizer-more'>Read more</a>" % (self.filename)
                else:
                    readmore = ""

                self.html = markdown(s) + readmore
                self.html = MUtil.link_first_tag(self.html, self.filename)
                self.html = MUtil.downgrade_headings(self.html)
                self.html = self.template.render(self.website, self.html)
                self.html = self.html.replace(self.website.tag['article_footer'], '', 1)
                self.html = self.html.replace(self.website.tag['announcement'], '')

                if self.date_html is not None:

                    self.html_full = self.html_full.replace(self.website.tag['date'], self.date_html, 1)

                    # date in short html should be a link
                    self.html = self.html.replace(self.website.tag['date'], MUtil.wrap_it_in_a_link(self.date_html, self.filename), 1)

                return True

            else:
                print (colours.ERROR + ' (!) ' + colours.END + "'%s' doesn't start with h1 and/or misses date)" % filename)
                return False

        else:
            return False

 
    def new_title(self):

        if self.html_full is None:
            return "Untitled"
        else:

            match = re.search(r"<h1>(.*?)<\/h1>", self.html_full)
            
            if match:
                return MUtil.strip_tags_from_html(match.group(1))
            else:
                return "Untitled"

    
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


    def feed_entry(self):

        full_url = '%s/%s' % (self.website.config.value('website_base_url'),self.filename)

        f = '<entry>'
        f += '<title>%s</title>' % html.escape(self.title, False)
        f += '<link href="%s"/>' % full_url
        f += '<id>%s</id>' % full_url
        f += '<updated>%sT00:00:01Z</updated>' % self.date
        f += '<summary>%s</summary>' % html.escape(self.abstract(), False)
        f += '</entry>'

        return f

    
    def date_html_from_date(self):

        # e.g. "<time datetime='2019-08-03'>3 August 2019</time>"

        if self.date is not None:
            result = "<time datetime='%s'>" % self.date.isoformat()
            result += self.date.strftime('%-d %B %Y')
            result += "</time>"
            return result
        else:
            return None


    def date_from_markdown_source(self):

        match = search(r'.*<!-- (\d\d?/\d\d?/\d\d\d\d?) -->.*', self.md)

        if match:
            return datetime.strptime(match[1], '%d/%m/%Y').date()
        else:
            return None

    
    def cc_license(self):

        cc_license = '<p class="magntetizer-license">'
        cc_license += '<a rel="license" href="http://creativecommons.org/licenses/by/4.0/">'
        cc_license += '<img alt="Creative Commons Licence" style="border-width:0" src="https://i.creativecommons.org/l/by/4.0/88x31.png" />'
        cc_license += '</a><br />This work by <a xmlns:cc="http://creativecommons.org/ns#" href="'
        cc_license += self.website.config.value('website_base_url') + '/' + self.filename
        cc_license += '" property="cc:attributionName" rel="cc:attributionURL">'
        cc_license += self.website.config.value('website_author')
        cc_license += '</a> is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by/4.0/">'
        cc_license += 'Creative Commons Attribution 4.0 International License</a>.'
        cc_license += '</p>'

        return cc_license

    
    def twitter_card(self):

        try:
            twitter_handle = self.website.config.value('website_twitter')

            card = '<meta name="twitter:card" content="summary_large_image" />'
            card += '<meta name="twitter:site" content="%s" />' % twitter_handle
            card += '<meta name="twitter:title" content="%s" />' % self.title

            img_url = MUtil.first_image_url_from_html(markdown(self.md))

            card += '<meta name="twitter:description" content="%s" />' % self.abstract()

            if img_url:

                if not img_url.startswith('http'):
                    img_url = self.website.config.value('website_base_url') + '/' + img_url

                card += '<meta name="twitter:image" content="%s" />' % img_url

            return card

        except:
            print(colours.ERROR + ' (!) ' + colours.END + "'website_twitter' not defined in config. Twitter cards will be disabled.")
            return ''


    def abstract(self):

        return MUtil.abstract_from_html(markdown(self.md))


    def is_valid(self):

        if self.md.startswith('# ') and search(r'.*<!-- (\d\d?/\d\d?/\d\d\d\d?) -->.*', self.md):
            return True
        else:
            return False


    @staticmethod
    def html_contents_from_multiple_md_files(website, filenames):

        article = Article(website)
        html = ''

        for filename in filenames:

            if filename.split('-', 1)[0].isdigit():
                if article.from_md_filename(filename):
                    html += article.html

        return html