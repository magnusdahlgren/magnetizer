from webpage import *

def main():

    website = Website()

    Webpage.write_webpages_from_directory(website, '../content')

if __name__ == "__main__":
    main()