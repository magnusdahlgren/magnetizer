# Magnetizer

A static site generator for a personal photo blog. Takes Markdown and image files as input and outputs a ready-to-publish HTML site.

## Project structure

Your blog lives in its own directory with the following layout:

```
content/       Markdown and image files
templates/     HTML templates
resources/     CSS, JS, fonts, icons, etc.
dist/          Generated output (publish this to the web)
config.yaml    Site configuration
manifest.json  Build state (created automatically)
```

`dist/` should be a cloned GitHub Pages repository. Magnetizer assumes this is already set up.

## Configuration

`config.yaml` supports the following options:

| Option | Description | Default |
|---|---|---|
| `site_name` | Used in page `<title>` tags | `My Blog` |
| `posts_per_page` | Posts shown per index page | `12` |
| `image_max_dimension` | Long-edge pixel limit when resizing images | `1600` |
| `image_quality` | JPEG quality for resized images (0–95) | `75` |
| `micro_post_max_length` | Max plain-text characters for a post to be treated as a microblog post | `180` |
| `index_meta_description` | `<meta name="description">` content on index pages (via `MAGNETIZER_META_DESCRIPTION` placeholder) | Not set |
| `index_title` | When set, the title of `index.html` becomes `site_name - index_title` | Not set |
| `categories` | Map of category slug to display name, e.g. `{photography: Photography}` | `{}` (no categories) |

Example:

```yaml
site_name: My Blog
posts_per_page: 12
image_max_dimension: 1600
image_quality: 75
micro_post_max_length: 180
categories:
  photography: Photography
  travel: Travel
```

## Creating a post

Run `new-post.py` from your project directory:

```
new-post.py                                     Empty post
new-post.py photo.jpg                           Post with one image
new-post.py "Post title"                        Post with a title
new-post.py photo1.jpg photo2.jpg "Post title"  Post with images and a title
```

This creates a numbered `.md` file in `content/` and copies any images alongside it. Open the `.md` file in your editor to add content.

Post files use a simple frontmatter format:

```markdown
---
date: 2026-05-24
title: My post title
---

Post body goes here. Standard Markdown is supported.
```

The `title` field is optional. Set `draft: true` to mark a post as a draft — it will still be generated as an HTML page, but will be excluded from index pages, category pages, the feed, the sitemap, the archive, and next/previous navigation. Draft posts are only reachable via their direct URL. If `draft` is absent or `false`, the post is published normally.

Set `favourite: true` to mark a post as a favourite — it will receive an additional `favourite` CSS class in the archive.

Set `category` to a slug from the `categories` map in `config.yaml` to assign the post to a category — matching is case-insensitive. This adds a link to the category's page in the post's footer, and includes the post on that category's page (`{slug}.html`). If `categories` is configured, the build prints a warning for posts with no category or with a category not found in `categories`.

A post with no title, no images, and a plain-text body of `micro_post_max_length` characters or fewer is treated as a microblog post and rendered with an additional `micro-post` CSS class.

The post `title` is rendered as the page's `<h1>` on an individual post page, or `<h2>` when shown alongside other posts (index and category pages). Use `###` (`<h3>`) or lower for any headings inside the post body — the build prints a warning if a post contains a `#` or `##` heading, since those levels are already used by the title.

## Building the site

Run `build.py` from your project directory.

| Command | What it does |
|---|---|
| `build.py` | Build anything that has changed since the last build, including resource files |
| `build.py --flush` | Delete all output and rebuild everything from scratch |
| `build.py --resources` | Force-replace all of `dist/resources/` with the current `resources/` |
| `build.py --push` | Build, then push `dist/` to GitHub Pages |
| `build.py --verbose` | Build and print a detailed post log plus summarised pages/resources sections |
| `build.py 1.md` | Preview a single post or special page (does not update index pages) |

Use `--flush` after editing templates. Resource file changes (CSS, JS) are picked up automatically on the next build. A `.` is printed for each file generated so you can see progress — in normal mode the dots are erased when the build finishes; in `--verbose` mode they remain. Warnings (missing title, alt text, etc.) are always shown inline next to the affected post.

Every full build also generates `dist/sitemap.xml` (all published posts, index, category, about, and archive pages with `lastmod` dates) and `dist/robots.txt` (pointing to the sitemap). These are not generated on single-file preview builds.

## Templates

Magnetizer uses a single template file: `templates/index.html`. It must contain two required placeholders, plus optional ones:

| Placeholder | Required | Replaced with |
|---|---|---|
| `MAGNETIZER_TITLE` | Yes | The page title |
| `MAGNETIZER_CONTENT` | Yes | The generated page content |
| `MAGNETIZER_BUILD_ID` | No | A Unix timestamp, useful for cache-busting: `style.css?v=MAGNETIZER_BUILD_ID` |
| `MAGNETIZER_CANONICAL_URL` | No | The canonical URL of the page. For `index.html` this is the root URL (e.g. `https://example.github.io/`); for all other pages it is `{site_url}/{filename}`. Use in a `<link rel="canonical">` tag to prevent duplicate-page issues with search engines. |
| `MAGNETIZER_META_DESCRIPTION` | No | On index pages: replaced with `<meta name="description" content="...">` using `index_meta_description` from config. Removed (empty string) when not configured or on non-index pages. |

Example `templates/index.html`:

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <title>MAGNETIZER_TITLE</title>
    <link rel="canonical" href="MAGNETIZER_CANONICAL_URL">
    <link rel="stylesheet" href="resources/style.css?v=MAGNETIZER_BUILD_ID">
  </head>
  <body>
    <header><a href="/">My site</a></header>
    MAGNETIZER_CONTENT
  </body>
</html>
```

## Content files

All files live flat in `content/` — no subdirectories.

- Markdown files: `{post-id}.md` (e.g. `42.md`)
- Image files: `{post-id}-image-{nn}.jpg/jpeg/png` (e.g. `42-image-01.jpg`)
- `about.md` — optional static about page (supports images as `about-image-{nn}.jpg/jpeg/png`)
- `cookies.md` — optional static cookies/privacy page

Posts are displayed in reverse order by post ID — a higher ID means a newer post.

## Archive page

The archive page (`dist/archive.html`) lists all dated posts grouped by month. It opens with an `<h1>Archive</h1>` heading, followed by a stats block showing the number of posts with photos and the total post count:

```html
<main>
  <h1>Archive</h1>
  <dl class="archive-stats">
    <dt class="photos">Photos:</dt>
    <dd>34</dd>
    <dt class="posts">Posts:</dt>
    <dd>56</dd>
  </dl>
  ...
</main>
```

The `class` attributes on `<dt>` allow CSS to replace the text labels with icons (e.g. Font Awesome).

If `categories` is configured and at least one category has a matching post, a categories list is inserted between the `<h1>` and the stats block, followed by a `<h2>Posts</h2>` heading:

```html
<main>
  <h1>Archive</h1>
  <h2>Categories</h2>
  <ul>
    <li><a href="photography.html">Photography</a></li>
    <li><a href="travel.html">Travel</a></li>
  </ul>
  <h2>Posts</h2>
  <dl class="archive-stats">...</dl>
  ...
</main>
```

Categories appear in the order defined in `config.yaml`, and only if they have at least one matching post.

## Publishing

Set up `dist/` as a clone of your GitHub Pages repository before using `--push`. Magnetizer stages, commits, and pushes all changes automatically.

If the push is rejected because the remote has changes you don't have locally (e.g. a `CNAME` file added by GitHub), run `git pull --rebase origin main` inside `dist/` first.
