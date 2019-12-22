""" A module to generate a sitemap, i.e. a file with a list of URLs for search engines
to index.
"""

from mutil import colours

class Sitemap:
    """ A class to populate a sitemap and then write it to file
    """

    def __init__(self, base_url):

        self.base_url = base_url
        self.pages = []


    def append(self, page):
        """ Add page to sitemap (or '/' if page is index.html)
        """

        if page == 'index.html':
            page = ''
        self.pages.append(self.base_url + '/' + page)


    def write(self, output_path):
        """ Write sitemap to sitemap.txt in output_path
        """

        print('Generating sitemap --> %s' % output_path)
        counter = 0
        with open(output_path + 'sitemap.txt', 'w') as myfile:
            for page in self.pages:
                myfile.write(page + '\n')
                counter += 1
        print(colours.OK + ' --> ' + colours.END + 'Generated sitemap with %s items' % counter)


    def clear(self):
        """ Remove all pages from sitemap
        """
        self.pages = []
