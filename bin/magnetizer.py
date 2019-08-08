from webpage import *

def main():

    website = Website()
    website.move_out()

    Webpage.write_webpages_from_directory(website, website.config_source_path)
    Webpage.write_index_page_from_directory(website, website.config_source_path)

    website.copy_resources()

if __name__ == "__main__":
    main()