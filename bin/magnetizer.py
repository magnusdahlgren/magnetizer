from webpage import *

def main():

    website = Website()

    Webpage.write_webpages_from_directory(website, website.config_source_path)
    Webpage.write_index_page_from_directory(website, website.config_source_path)

if __name__ == "__main__":
    main()