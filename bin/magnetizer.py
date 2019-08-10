from webpage import *
from sys import argv

def main():

    if len(argv) == 3 and argv[1] == '-config':
        config_filename = argv[2]
    else:
        config_filename = '../config/magnetizer.cfg'

    print('Using config ' + config_filename + '...')

    website = Website(config_filename)
    website.wipe()

    Webpage.write_webpages_from_directory(website, website.config.value('source_path'))
    Webpage.write_index_page_from_directory(website, website.config.value('source_path'))

    website.copy_resources()

if __name__ == "__main__":
    main()