import re
from dataclasses import dataclass, field
from datetime import date as _date
import markdown as _markdown


@dataclass
class Post:
    id: int | str
    date: str
    date_uk: str
    title: str | None
    url: str
    body_html: str
    images: list[str]
    excerpt_html: str | None = None


def _parse_frontmatter(text):
    parts = text.split('---')
    if len(parts) < 3:
        return {}, text.strip()
    fm = {}
    for line in parts[1].strip().splitlines():
        key, sep, value = line.partition(':')
        if sep:
            fm[key.strip()] = value.strip()
    body = '---'.join(parts[2:]).strip()
    return fm, body


def _format_date_uk(date_str):
    d = _date.fromisoformat(date_str)
    return d.strftime('%-d %B %Y')


def parse_post(md_text, post_id, image_filenames):
    fm, body = _parse_frontmatter(md_text)

    date_str = fm.get('date', '')
    title = fm.get('title') or None

    more_parts = body.split('<!-- more -->', 1)
    body_html = _markdown.markdown(more_parts[0] + more_parts[1]) if len(more_parts) == 2 else _markdown.markdown(body) if body else ''
    excerpt_html = _markdown.markdown(more_parts[0].strip()) if len(more_parts) == 2 else None

    images = sorted(
        image_filenames,
        key=lambda f: int(re.search(r'-image-(\d+)', f).group(1)),
    )

    return Post(
        id=post_id,
        date=date_str,
        date_uk=_format_date_uk(date_str),
        title=title,
        url=f"{post_id}.html",
        body_html=body_html,
        images=images,
        excerpt_html=excerpt_html,
    )
