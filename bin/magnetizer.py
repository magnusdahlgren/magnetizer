from webpage import *

def main():

    webpage = Webpage('../content/my-post.md')
    print(webpage.html)

if __name__ == "__main__":
    main()