from webpage import *

def main():

    template = Template('_page.html')

    webpage = Webpage(template)
    webpage.read('123-this-is-my-file.md')
    webpage.write()

if __name__ == "__main__":
    main()