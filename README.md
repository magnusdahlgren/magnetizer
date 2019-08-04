# Magnetizer
Magnetizer is a simple tool to render static blog pages using html templates and Markdown. It was created by me, [Magnus Dahlgren](https://magnusd.cc) to cater for my personal web needs but I've released it as open source for Github-technical reasons.

## How it works

1. Create your web content as `.md` markdown files in the `content` directory
2. Store images and other resources in the `resources` directory
3. Run Mangetizer
4. Each `.md` file is rendered as a html page
5. Also, a paginated list view of the posts is generated
6. The rendered html files and resources can be found in the `public` directory, ready to be uploaded on the web hosting service of your choice.

You can customise the look and feel of your website by editing the templates in the `templates` directory.

## Getting started

A Magnetizer project contains the following directory structure, populated with files for an example site for convenience:

    .
    ├── config.py               # Configuration file
    ├── content                 # Source markdown files. This is where you create your content.
    │   ├── 001-first-post.md   # Rendered as first-post.html to output.
    │   ├── 002-second-post.md  # Rendered as second-post.html to output.
    │   └── ...        
    ├── public                  # This is where the site will be rendered.
    │   └── (empty)        
    ├── resources               # Source images, downloads etc, which will be copied as-is to output.
    │   └── example.jpg        
    └── templates               # Html templates
        ├── _header.html
        ├── _footer.html
        ├── _welcome.html
        └── _page.html

### Configure your project

Configure Magnetizer by editing the file `config.py`:

``` Python
CONFIG_SITE_NAME      = 'My Magnetizer Site'
CONFIG_SITE_TAGLINE   = 'An example site'
CONFIG_POSTS_PER_PAGE = 4

CONFIG_SOURCE_PATH    = '../content/'
CONFIG_RESOURCE_PATH  = '../resources/'
CONFIG_OUTPUT_PATH    = '../public/'
```

The following configuration parameters are available:

| Parameter | Description                                                                                   |
| ----------|-----------------------------------------------------------------------------------------------|
| `CONFIG_SITE_NAME`      | The name of the website. Used for meta titles.                                  |
| `CONFIG_SITE_TAGLINE`   | A tagline, included in the page title on the homepage                           |
| `CONFIG_POSTS_PER_PAGE` | How many posts to show per page                                                 |
| `CONFIG_SOURCE_PATH`    | The directory containing the source files. Normally won't need to be changed.   |
| `CONFIG_RESOURCE_PATH`  | Where to look for images etc. These files will be included as-is when generating the site. Normally won't need to be changed. |
| `CONFIG_OUTPUT_PATH`    | Where the resulting files will be written. Normally won't need to be changed.   |

### Write some content

Create a new post in the `content` folder using [Markdown](https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet) formatting. If you are using the example project above, name the post `010-My-first-post.md`.

```
# This is my first post

I'm writing it in Markdown.
```

### File naming convention

Source `.md` files must be named on the format `nnn-filename.md` where `nnn` is a unique, 3-digit incremental number, for example `001-my-first-post.md`. The number and the dash will be removed from the output filename (so our example becomes `my-first-post.html`).

**⚠️ NOTE:** Files in the `source` directory that don't follow this naming convention will be ignored.

On listings pages, posts are sorted in reverse order, based on the source file name.

### Images

Images and other resources should be placed in the `resources` folder, to make sure they are copied across to the output. To include an image in a post, make sure to provide the correct path:

``` Markdown
![alt text](resources/image.png)
```

### Run Magnetizer

Using a file console, navigate to the `magnetizer/bin` directory and run the following command

``` Shell
$ python magnetizer
```

The output will be rendered in the `public` directory with the following structure:

    .
    ├── resources
    │   └── example.jpg        
    ├── index.html
    ├── page-2.html
    ├── page-3.html
    ├── first-post.html
    ├── second-post.html
    └── ...


### Publish your website

To publish the resulting website, simply upload all the contents from the `public` directory (not the directory itself!) to your hosting provider. How you do this will depend on where you host your site.

## Customising your website

### Templates

Magnetizer templates are stored in the `templates` directory. Edit these to customise how the site looks.

| Template File   | Usage                         |
| --------------- | ----------------------------- |
| `_page.html`    | Main template for all pages.  |
| `_welcome.html` | Optional welcome message.     |
| `_about.html`   | Optional info about the blog. |

#### Template tags

Magnetizer templates use html comment tags to indicate where dynamic content will be inserted.

| Tag | Usage | 
| --- | ----- |
| `<!-- MAGNETIZE_WELCOME -->`  | Display welcome message from `_welcome.html`. Only rendered for `index.html`    | 
| `<!-- MAGNETIZE_ABOUT -->`    | Info about the blog from `_about.html`. Only rendered on individual post pages. |
| `<!-- MAGNETIZER_CONTENT -->` | The rendered content of a page. Either a blog post listing or an individual post. |
| `<!-- MAGNETIZER_TITLE -->`   | Page meta title. |
| `<!-- MAGNETIZER_DATE -->`    | The date a post was published. See [Post dates](#post-dates)

Typically, `_page.html` will be a mix of html and calls to other templates, e.g.

``` html
<html>

    <head>
        <title><!-- MAGNETIZER_TITLE --></title>
    </head>

    <body>

        <header>...</header>

        <!-- MAGNETIZER_WELCOME -->
        <!-- MAGNETIZER_CONTENT -->
        <!-- MAGNETIZER_ABOUT -->

        <footer>...</footer>

    </body>

</html>
```



## Special features

### Page titles

Page titles are generated automatically for each page and are available in the `<!-- MAGNETIZER_TITLE -->` tag.

| Page                | Title                                   |
| --------------------|-----------------------------------------|
| Homepage            | `CONFIG_SITE_NAME - CONFIG_SITE_TAGLINE`|
| Paginated post list | `CONFIG_SITE_NAME - Page %n`            |
| Post                | `First line of post - CONFIG_SITE_NAME` |

### Post dates

A post's publication date can be included in the `.md` file as a html comment tag with UK date format (d/m/YYYY). The date can then be displayed by including `<!-- MAGNETIZER_DATE -->` in the post template.

Dates are not mandatory. If a date is not provided for a post, `<!-- MAGNETIZER_DATE -->` will simply be empty.

Example:

``` Markdown
<!-- 6/2/2019 -->
```
(Will be displayed in the rendered post as 6 February 2019)

**⚠️ NOTE:** Post dates do not affect the sorting of posts.

### Post order

Posts are sorted in reverse order, based on their source file names, e.g.

```
034-my-latest-post.md
002-my-second-post.md
001-my-first-post.md
```

## Known issues
**⚠️ NOTE:** Magnetizer is in early development and some of the described features may not yet exist.

## History

Magnetizer was started on 4 August 2019.