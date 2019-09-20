# Magnetizer
Magnetizer is a simple tool to render static blog pages using html templates and Markdown. It was created by me, [Magnus Dahlgren](https://magnusd.cc) to cater for my personal web needs but I've released it as open source for Github-technical reasons.

⚠️ **Note:** Magnetizer does exactly what I need it to do. It may not do what you need it to do. 💁‍

## How it works

1. Create your web content as `.md` markdown files in the `content` directory
2. Store images and other resources in the `resources` directory
3. Run Mangetizer
4. Each `.md` file is rendered as a html page
5. Also, a list view of the articles is generated
6. The rendered html files and resources can be found in the `public` directory, ready to be uploaded on the web hosting service of your choice.

You can customise the look and feel of your website by editing the templates in the `templates` directory.

## Getting started

A Magnetizer project contains the following directory structure, populated with files for an example site for convenience:

    .
    ├── config.py                                # Configuration file
    ├── content                                  # Source markdown files. This is where you create your content.
    │   ├── 001-for-magnus-by-magnus.md          # Example, will be rendered as for-magnus-by-magnus.html to output.
    │   ├── 002-the-simple-website-generator.md
    │   └── ...        
    ├── public                                   # This is where the site will be rendered.
    │   └── (empty)        
    ├── resources                                # Source images, downloads etc, which will be copied as-is to output.
    │   └── example.jpg        
    └── templates                                # Customisable html templates
        ├── _page.html
        ├── _article.html
        ├── _article_footer.html.html
        └── _index_header.html
        
        		

### Configure your project

Configure Magnetizer by editing the file `magnetizer.cfg`:

``` 
source_path     = ../content/
template_path   = ../templates/
resources_path  = ../resources/
output_path     = ../public/

webpage_template_filename         = _page.html
article_template_filename         = _article.html
article_footer_template_filename  = _article_footer.html
index_header_template_filename    = _index_header.html

website_name    = The Magnetizer Example Site
website_tagline = Somewhere to Start

approved_filetypes = [ .gif, .jpg, .png, .pdf, .txt ]
```

The following configuration parameters are available:

| Parameter | Description                                                                            |
| ----------|----------------------------------------------------------------------------------------|
| `website_name`    | The name of the website. Used for meta titles.                                 |
| `website_tagline` | A tagline, included in the page title on the homepage                          |
| `website_base_url` | The address where the site is published, e.g. `https://example.com`. No trailing `/`. |
| `website_author`  | The name of the author of the website (used in feeds). e.g. `Magnus Dahlgren`  |
| `website_twitter` | The Twitter handle of the author (used in Twitter cards). e.g. `@magnusdahlgren` |
| `source_path`     | The directory containing the source files. Please update to an absolute path.  |
| `resources_path`  | Where to look for images etc. These files will be included as-is when generating the site. Please update to an absolute path. |
| `output_path`    | Where the resulting files will be written. Please update to an absolute path.   |
| `approved_filetypes` | Controls which filetypes in `resources` and `output` will be assumed part of the website.  |
| `webpage_template_filename`        | The page template. This parameter usually doesn't need changing              |
| `article_template_filename`        | Template used for each article. This parameter usually doesn't need changing |
| `article_footer_template_filename` | Template used for each article. This parameter usually doesn't need changing |
| `index_header_template_filename`   | Template for the header on the index page. This parameter usually doesn't need changing |

⚠️ **Note:** All these configuration parameters are mandatory. Do not remove any of them from the configuration file. 👮‍♂️

### Write some content

Create a new article in the `content` folder using [Markdown](https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet) formatting. If you are using the example project above, name the article `010-My-first-article.md`.

```
# This is my first article

I'm writing it in Markdown.
```

⚠️ **Note:** Every article must start with a h1 heading (`# some text`). Articles not starting with a heading will be ignored.

### File naming convention

| Type of article | Filename | Example | 
| ----- | ----- | ----- |
| Normal article <br> (will show on listings page) | `nnn-filename.md` <br> whenre `nnn-` is a 3-digit incremental number | `001-my-first-article.md` <br> (rendered as `my-first-article.html`) |
| Special article <br> (will not show on listings page) | `filename.md` | `about.md` <br> (rendered as `about.html`) |

**⚠️ NOTE:** Make sure to name your files in a way that ensures the rendered filenames will be unique. `001-article.md` and `002-article.md` will both be rendered as `article.html`, meaning one will overwrite the other. 🤦

On listings pages, article are sorted in reverse order, based on the source file name.

### Images

Images and other resources should be placed in the `resources` folder, to make sure they are copied across to the output. To include an image in a article, make sure to provide the correct path:

``` Markdown
![alt text](resources/image.png)
```

### Run Magnetizer

Using a file console, navigate to the `magnetizer/bin` directory and run the following command

``` Shell
$ python magnetizer
```

Alternatively, run Magnetizer with a custom `.cfg` file (recommended):

``` Shell
$ python magnetizer.py -config "~/mysite/config/magnetizer.cfg"
```

The output will be rendered in the `public` directory with the following structure:

    .
    ├── example.jpg        
    ├── index.html
    ├── first-article.html
    ├── second-article.html
    └── ...


### Publish your website

To publish the resulting website, simply upload all the contents from the `public` directory to your hosting provider. How you do this will depend on where you host your site.

## Customising your website

### Templates

Magnetizer templates are stored in the `templates` directory. Edit these to customise how the site looks.

| Template File   | Usage                         |
| --------------- | ----------------------------- |
| `_page.html`    | Main template for all pages.  |
| `_article.html` | Template for each article, both on article pages and on the index page |
| `_article_footer.html` | Footer included on each article page (not the index page). Should normally contain a link back to the homepage |
| `_index_header.html`   | Header included on the index page only |

#### Template tags

Magnetizer templates use html comment tags to indicate where dynamic content will be inserted.

| Tag | Usage | 
| --- | ----- |
| `<!-- MAGNETIZER_CONTENT -->`| This is where the rendered content will show, either on the index page or for individual article pages    | 
| `<!-- MAGNETIZER_META -->`   | The page meta data, e.g. title, will show here. This tag must be included somewhere between `<head>` and `</head>`. |
| `<!-- MAGNETIZER_PAGE_CLASS -->` | Will be `magnetizer-index` on listing page and `magnetizer-article` on article page. Example use: `<body class='<!-- MAGNETIZER_PAGE_CLASS -->'>` |
| `<!-- MAGNETIZER_INDEX_HEADER -->` | On the index page, this is where `_index_header.html` will show |
| `<!-- MAGNETIZER_ARTICLE_FOOTER -->` | On article pages, this is where `_article_footer.html` will show  |
| `<!-- MAGNETIZER_DATE -->`    | The date an article was published. See [Article dates](#article-dates) |
| `<!-- MAGNETIZER_CC -->` | Where to show the Creative Commons license, if there is one | 

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

### CSS

Most css structure is entirely up to you and depends on how you structure your templates. However, the following special css classes exist to allow styling of machine genarated html.

| Class | Use  | 
| ----- | -----|
| body.magnetizer-index   | Set on listings pages             |
| body.magnetizer-article | Set on article pages              |
| p.magntetizer-license   | Creative Commons license          |
| a.magnetizer-more       | 'Read more' link on listings page |

**⚠️ NOTE:** On listings pages, headings are _downgraded_ one step, so that `<h1>` becomes `<h2>`, etc. You may want to style `.magnetizer-index h2` as `.magnetizer-article h1`, and so on.

## Special features

### Displaying article extracts on the index page

By inserting the `<!-- BREAK -->` tag in the Markdown, you can control how much of the article will show on the index page. When the break tag is used, a link 'Read more' will show on the index page for the abbreviated article.

### Page titles

Page titles are generated automatically for each page and are available in the `<!-- MAGNETIZER_TITLE -->` tag.

| Page                | Title                                   |
| --------------------|-----------------------------------------|
| Homepage            | `CONFIG_SITE_NAME - CONFIG_SITE_TAGLINE`|
| Paginated article list | `CONFIG_SITE_NAME - Page %n`            |
| Article             | `First line of article - CONFIG_SITE_NAME` |

### Article dates

An article's publication date must be included in the `.md` file as a html comment tag with UK date format (d/m/YYYY). The date can then be displayed by including `<!-- MAGNETIZER_DATE -->` in the article template.

**⚠️ NOTE:** Dates are mandatory. Articles without dates will be ignored.

Example:

``` Markdown
<!-- 6/2/2019 -->
```
(Will be displayed as 6 February 2019)

**⚠️ NOTE:** Article dates do not affect the sorting of articles.

### Creative commons

Include `<!-- CREATIVE COMMONS -->` anywhere in an article `.md` file to show a Creative Commons license.

### Article order

Article are sorted in reverse order, based on their source file names, e.g.

```
034-my-latest-article.md
002-my-second-article.md
001-my-first-article.md
```

## Known issues

* Magnetizer does not yet paginate the index page. It is therefore only suitable for a small number of articles at this point.

## History

**4 August 2019** - Started development of Magnetizer.

**10 August 2019** - First release, including all the features I believe I need for my blog.
