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
| `site_title` | Used in page `<title>` tags | `My Blog` |
| `posts_per_page` | Posts shown per index page | `12` |
| `image_max_dimension` | Long-edge pixel limit when resizing images | `1600` |
| `image_quality` | JPEG quality for resized images (0–95) | `75` |
| `micro_post_max_length` | Max plain-text characters for a post to be treated as a microblog post | `180` |

Example:

```yaml
site_title: My Blog
posts_per_page: 12
image_max_dimension: 1600
image_quality: 75
micro_post_max_length: 180
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

The `title` field is optional.

A post with no title, no images, and a plain-text body of `micro_post_max_length` characters or fewer is treated as a microblog post and rendered with an additional `micro-post` CSS class.

## Building the site

Run `build.py` from your project directory.

| Command | What it does |
|---|---|
| `build.py` | Build anything that has changed since the last build |
| `build.py --flush` | Delete all output and rebuild everything from scratch |
| `build.py --resources` | Replace `dist/resources/` with the current `resources/` |
| `build.py --push` | Build, then push `dist/` to GitHub Pages |
| `build.py --verbose` | Build and print a detailed log of every file changed |
| `build.py 1.md` | Preview a single post or special page (does not update index pages) |

Use `--flush` after editing templates. Use `--resources` after editing CSS or JS.

Every full build also generates `dist/sitemap.xml` (all post, index, about, and archive pages with `lastmod` dates) and `dist/robots.txt` (pointing to the sitemap). These are not generated on single-file preview builds.

## Templates

Magnetizer uses a single template file: `templates/index.html`. It must contain two placeholders:

| Placeholder | Replaced with |
|---|---|
| `MAGNETIZER_TITLE` | The page title |
| `MAGNETIZER_CONTENT` | The generated page content |

## Content files

All files live flat in `content/` — no subdirectories.

- Markdown files: `{post-id}.md` (e.g. `42.md`)
- Image files: `{post-id}-image-{nn}.jpg/jpeg/png` (e.g. `42-image-01.jpg`)
- `about.md` — optional static about page (supports images as `about-image-{nn}.jpg/jpeg/png`)
- `cookies.md` — optional static cookies/privacy page

Posts are displayed in reverse order by post ID — a higher ID means a newer post.

## Archive page

The archive page (`dist/archive.html`) lists all dated posts grouped by month. It opens with an `<h1>Archive</h1>` heading, followed by a stats block with the total number of posts and photos (individual images) across the whole site:

```html
<h1>Archive</h1>
<dl class="archive-stats">
  <dt class="posts">Posts:</dt>
  <dd>45</dd>
  <dt class="photos">Photos:</dt>
  <dd>64</dd>
</dl>
```

The `class` attributes on `<dt>` allow CSS to replace the text labels with icons (e.g. Font Awesome).

## Publishing

Set up `dist/` as a clone of your GitHub Pages repository before using `--push`. Magnetizer stages, commits, and pushes all changes automatically.

If the push is rejected because the remote has changes you don't have locally (e.g. a `CNAME` file added by GitHub), run `git pull --rebase origin main` inside `dist/` first.
