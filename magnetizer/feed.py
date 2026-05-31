def _rfc3339(date_str):
    return f"{date_str}T00:00:00Z"


def render_feed(posts, config):
    site_url = config["site_url"]
    site_title = config["site_title"]
    feed_url = f"{site_url}/feed.xml"
    most_recent_date = _rfc3339(posts[0].date) if posts else ""

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<feed xmlns="http://www.w3.org/2005/Atom">',
        f'  <title>{site_title}</title>',
        f'  <link href="{site_url}" />',
        f'  <link rel="self" href="{feed_url}" />',
        f'  <id>{site_url}</id>',
        f'  <updated>{most_recent_date}</updated>',
    ]

    for post in posts:
        post_url = f"{site_url}/{post.url}"
        title = post.title if post.title else post.date_uk
        lines += [
            '  <entry>',
            f'    <title>{title}</title>',
            f'    <link href="{post_url}" />',
            f'    <id>{post_url}</id>',
            f'    <updated>{_rfc3339(post.date)}</updated>',
            f'    <content type="html"><![CDATA[{post.body_html}]]></content>',
            '  </entry>',
        ]

    lines.append('</feed>')
    return '\n'.join(lines)
