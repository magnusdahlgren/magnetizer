from webpage import *
from atom import *
from sys import argv

def main():

    if len(argv) == 3 and argv[1] == '-config':
        config_filename = argv[2]
    else:
        config_filename = '../config/magnetizer.cfg'

    print('Using config ' + config_filename + '...')

    website = Website(config_filename)
    website.wipe()

    Webpage.write_article_pages_from_directory(website, website.config.value('source_path'))
    Webpage.write_index_page_from_directory(website, website.config.value('source_path'))

    website.copy_resources()

    atom = Atom(website)
    atom.write()

if __name__ == "__main__":
    main()