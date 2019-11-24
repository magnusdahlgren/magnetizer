from mutil import *

class Sitemap:

    def __init__(self, base_url):

        self.base_url = base_url
        self.pages = []


    def append(self, page):

        if page == 'index.html':
            p = ''
        else:
            p = page 
        self.pages.append(self.base_url + '/' + p)


    def write(self, output_path):

        print('Generating sitemap --> %s' % output_path)
        n = 0
        with open(output_path + 'sitemap.txt', 'w') as myfile:
            for page in self.pages:                    
                myfile.write(page + '\n')
                n += 1
        print (colours.OK + ' --> ' + colours.END + 'Generated sitemap with %s items' % n)


    def clear(self):
        self.pages = []
