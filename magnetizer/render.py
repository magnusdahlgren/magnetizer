from datetime import date as _date
from html import escape as _escape


def _resized_filename(original):
    stem, dot, ext = original.rpartition('.')
    return f"{stem}-resized.{ext}"


def index_page_url(page_num):
    return "index.html" if page_num == 1 else f"index-{page_num}.html"


def render_article(post, on_index_page):
    article_class = "multiple-posts" if on_index_page else "single-post"
    if post.is_micro:
        article_class += " micro-post"
    if not post.title:
        aria = f' aria-label="Post {post.id} ({post.date_uk})"' if post.date_uk else f' aria-label="Post {post.id}"'
    else:
        aria = ''
    parts = [f'<article id="post-{post.id}" class="{article_class}"{aria}>']

    if post.images:
        parts.append('<div class="post-images">')
        for image in post.images:
            resized = _resized_filename(image.filename)
            alt = f' alt="{_escape(image.alt, quote=True)}"'
            if on_index_page:
                parts.append(f'<figure><a href="{post.url}"><img src="{resized}"{alt}></a></figure>')
            else:
                parts.append(f'<figure><img src="{resized}"{alt}></figure>')
        parts.append('</div>')

    if post.title:
        if on_index_page:
            parts.append(f'<h1><a href="{post.url}">{_escape(post.title)}</a></h1>')
        else:
            parts.append(f'<h1>{_escape(post.title)}</h1>')

    if on_index_page and post.excerpt_html is not None:
        parts.append(f'<div class="post-body">{post.excerpt_html}<a href="{post.url}" class="read-more">Read more →</a></div>')
    else:
        parts.append(f'<div class="post-body">{post.body_html}</div>')

    if post.date:
        if on_index_page:
            date_content = f'<a href="{post.url}">{post.date_uk}</a>'
        else:
            date_content = post.date_uk
        parts.append(
            f'<footer><time datetime="{post.date}">{date_content}</time></footer>'
        )

    parts.append('</article>')
    return '\n'.join(parts)


def render_post_page_content(post, index_page_url, newer_url=None, older_url=None, back_url=None):
    article = render_article(post, on_index_page=False)
    back_url = back_url or f"{index_page_url}#post-{post.id}"

    parts = [f'<main>\n{article}\n</main>']

    if newer_url or older_url:
        nav_items = []
        if newer_url:
            nav_items.append(f'<li class="newer"><a href="{newer_url}">← Newer post</a></li>')
        if older_url:
            nav_items.append(f'<li class="older"><a href="{older_url}">Older post →</a></li>')
        parts.append(f'<nav><ul>{"".join(nav_items)}</ul></nav>')

    parts.append(f'<nav><a href="{back_url}">⌂ Back to homepage</a></nav>')
    return '\n'.join(parts)


def render_index_page_content(posts, page_num, total_pages):
    articles = '\n'.join(render_article(p, on_index_page=True) for p in posts)
    content = f'<main>\n{articles}\n</main>'

    if total_pages > 1:
        nav_items = []
        if page_num > 1:
            prev_url = index_page_url(page_num - 1)
            nav_items.append(f'<li class="newer"><a href="{prev_url}">← Newer posts</a></li>')
        if page_num < total_pages:
            next_url = index_page_url(page_num + 1)
            nav_items.append(f'<li class="older"><a href="{next_url}">Older posts →</a></li>')
        content += f'\n<nav><ul>{"".join(nav_items)}</ul></nav>'

    return content


def render_page_title(site_title, post_title, page_num):
    if page_num is not None:
        if page_num == 1:
            return site_title
        return f"{site_title} - Page {page_num}"
    if post_title:
        return f"{post_title} - {site_title}"
    return site_title


def render_template(template_html, title, content):
    return template_html.replace('MAGNETIZER_TITLE', title).replace('MAGNETIZER_CONTENT', content)


def render_archive_page_content(posts):
    dated_posts = [p for p in posts if p.date]

    months = {}
    for post in dated_posts:
        d = _date.fromisoformat(post.date)
        key = (d.year, d.month)
        months.setdefault(key, []).append(post)

    parts = ['<main>']
    for year, month in sorted(months.keys(), reverse=True):
        label = _date(year, month, 1).strftime('%B %Y')
        parts.append('<section>')
        parts.append(f'<h2>{label}</h2>')
        parts.append('<ul>')
        for post in months[(year, month)]:
            day = str(_date.fromisoformat(post.date).day)
            text = f'{day} - {_escape(post.title)}' if post.title else day
            parts.append(f'<li><a href="{post.url}">{text}</a></li>')
        parts.append('</ul>')
        parts.append('</section>')
    parts.append('</main>')
    parts.append('<nav><a href="index.html">⌂ Back to homepage</a></nav>')

    return '\n'.join(parts)
