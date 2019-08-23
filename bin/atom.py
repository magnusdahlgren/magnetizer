from datetime import *
from article import *
from webpage import *

"""
<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">

  <title>Example Feed</title>
  <link href="http://example.org/"/>
  <updated>2003-12-13T18:30:02Z</updated>
  <author>
    <name>John Doe</name>
  </author>
  <generator uri="/myblog.php" version="1.0">
        Example Toolkit
  </generator>
  <id>urn:uuid:60a76c80-d399-11d9-b93C-0003939e0af6</id>

  <entry>
    <title>Atom-Powered Robots Run Amok</title>
    <link href="http://example.org/2003/12/13/atom03"/>
    <id>urn:uuid:1225c695-cfb8-4ebb-aaaa-80da344efa6a</id>
    <updated>2003-12-13T18:30:02Z</updated>
    <summary>Some text.</summary>
  </entry>

</feed>
"""

class Atom:

    def __init__(self, website):
        
        self.website = website

        filenames = Webpage.filenames_from_directory(self.website.config.value('source_path'))
        self.feed_data = self.feed(filenames)

    def feed(self, filenames):

        article = Article(self.website)

        f = '<?xml version="1.0" encoding="utf-8"?>'
        f += '<feed xmlns="http://www.w3.org/2005/Atom">'
        f += '<title>%s</title>' % self.website.config.value('website_name')
        f += '<author><name>%s</name></author>' % self.website.config.value('website_author')
        f += '<generator uri="https://github.com/magnusdahlgren/magnetizer">Magnetizer</generator>'
        f += '<id>%s</id>' % self.website.config.value('website_base_url')

        for filename in filenames:

            if filename.split('-', 1)[0].isdigit():
                if article.from_md_filename(filename):
                    f += article.feed_entry()

        f += '</feed>'

        return f


    def write(self):

        print('Generating atom feed --> %s' % self.website.config.value('output_path'))

        with open(self.website.config.value('output_path') + 'atom.xml', 'w') as myfile:
            myfile.write(self.feed_data)
            print('  W  %s' % 'atom.xml')
