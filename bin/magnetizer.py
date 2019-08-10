from webpage import *

def main():

    website = Website('../config/magnetizer.cfg')
    website.wipe()

    Webpage.write_webpages_from_directory(website, website.config.value('source_path'))
    Webpage.write_index_page_from_directory(website, website.config.value('source_path'))

    website.copy_resources()

if __name__ == "__main__":
    main()