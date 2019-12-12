from datetime import *
import html
from item import *
from webpage import *

class Atom:

    def __init__(self, website):
        
        self.website = website

        filenames = Webpage.filenames_from_directory(self.website.config.value('source_path'))
        self.feed_data = self.feed(filenames)

    def feed(self, filenames):

        item = Item(self.website)

        f = '<?xml version="1.0" encoding="utf-8"?>'
        f += '<feed xmlns="http://www.w3.org/2005/Atom">'
        f += '<title>%s - %s</title>' % (html.escape(self.website.config.value('website_name'), False), html.escape(self.website.config.value('website_tagline'), False))
        f += '<author><name>%s</name></author>' % html.escape(self.website.config.value('website_author'))
        f += '<generator uri="https://github.com/magnusdahlgren/magnetizer">Magnetizer</generator>'
        f += '<id>%s/</id>' % self.website.config.value('website_base_url')
        f += '<updated>**UPDATED**</updated>'

        first_item = True

        for filename in filenames:

            if filename.split('-', 1)[0].isdigit():
                if item.from_md_filename(filename):
                    f += item.feed_entry()
                    if first_item:
                        f = f.replace('**UPDATED**', item.date.isoformat() + 'T00:00:02Z')
                        first_item = False


        f += '</feed>'

        return f


    def write(self):

        print('Generating atom feed --> %s' % self.website.config.value('output_path'))

        with open(self.website.config.value('output_path') + 'atom.xml', 'w') as myfile:
            myfile.write(self.feed_data)
            print(colours.OK + ' --> ' + colours.END + 'atom.xml')
