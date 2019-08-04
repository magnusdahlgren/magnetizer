from webpage import *

def main():

    template = Template('_page.html')

    webpage = Webpage(template)
    webpage.read('my-post.md')
    webpage.write()

if __name__ == "__main__":
    main()