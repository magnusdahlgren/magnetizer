import html as _html

from magnetizer.content import resized_filename as _resized_filename


def _rfc3339(date_str, post_id):
    h = (post_id // 3600) % 24
    m = (post_id // 60) % 60
    s = post_id % 60
    return f"{date_str}T{h:02d}:{m:02d}:{s:02d}Z"


def render_feed(posts, config):
    site_url = config["site_url"].rstrip('/')
    site_title = _html.escape(config["site_title"])
    feed_url = f"{site_url}/feed.xml"
    dated_posts = [p for p in posts if p.date]
    most_recent_date = _rfc3339(dated_posts[0].date, dated_posts[0].id) if dated_posts else ""

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<feed xmlns="http://www.w3.org/2005/Atom">',
        f'  <title>{site_title}</title>',
        f'  <link href="{site_url}" />',
        f'  <link rel="self" href="{feed_url}" />',
        f'  <id>{site_url}/</id>',
        f'  <updated>{most_recent_date}</updated>',
        f'  <author><name>{site_title}</name></author>',
    ]

    for post in dated_posts:
        post_url = f"{site_url}/{post.url}"
        title = _html.escape(post.title if post.title else post.date_uk)
        images_html = ''.join(
            f'<figure><img src="{site_url}/{_resized_filename(img.filename)}"'
            f' alt="{_html.escape(img.alt, quote=True)}"></figure>'
            for img in post.images
        )
        lines += [
            '  <entry>',
            f'    <title>{title}</title>',
            f'    <link href="{post_url}" />',
            f'    <id>{post_url}</id>',
            f'    <updated>{_rfc3339(post.date, post.id)}</updated>',
            f'    <content type="html"><![CDATA[{images_html}{post.body_html}]]></content>',
            '  </entry>',
        ]

    lines.append('</feed>')
    return '\n'.join(lines)
