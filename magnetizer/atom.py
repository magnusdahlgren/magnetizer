"""A module to generate an atom feed from avaialble Magnetizer files
"""

import html
from item import Item, colours
from webpage import Webpage

class Atom:
    """The Atom class represents the atom feed.
    """
    
    def __init__(self, website):

        self.website = website

        filenames = Webpage.filenames_from_directory(self.website.config.value('source_path'))
        self.feed_data = self.feed(filenames)

    def feed(self, filenames):
        """ Generate Atom feed

        Parameters:
        filenames - a list of filenames
        """

        item = Item(self.website)

        website_name = html.escape(self.website.config.value('website_name'), False)
        website_tagline = html.escape(self.website.config.value('website_tagline'), False)
        website_author = html.escape(self.website.config.value('website_author'))

        feed_data = '<?xml version="1.0" encoding="utf-8"?>'
        feed_data += '<feed xmlns="http://www.w3.org/2005/Atom">'
        feed_data += '<title>%s - %s</title>' % (website_name, website_tagline)
        feed_data += '<author><name>%s</name></author>' % website_author
        feed_data += '<generator uri="https://github.com/magnusdahlgren/magnetizer">'
        feed_data += 'Magnetizer</generator>'
        feed_data += '<id>%s/</id>' % self.website.config.value('website_base_url')
        feed_data += '<updated>****</updated>'

        first_item = True

        for filename in filenames:

            if filename.split('-', 1)[0].isdigit():
                if item.from_md_filename(filename):
                    feed_data += item.feed_entry()
                    if first_item:
                        feed_data = feed_data.replace('****', item.date.isoformat() + 'T00:00:02Z')
                        first_item = False


        feed_data += '</feed>'

        return feed_data


    def write(self):
        """ Write the generated feed to file.
        """

        print('Generating atom feed --> %s' % self.website.config.value('output_path'))

        with open(self.website.config.value('output_path') + 'atom.xml', 'w') as myfile:
            myfile.write(self.feed_data)
            print(colours.OK + ' --> ' + colours.END + 'atom.xml')
