import re
from dataclasses import dataclass
from datetime import date as _date
import markdown as _markdown


_ALLOWED_FRONTMATTER_KEYS = frozenset({'date', 'title', 'images'})


@dataclass
class Image:
    filename: str
    alt: str = ""


@dataclass
class Post:
    id: int | str
    date: str | None
    date_uk: str | None
    title: str | None
    url: str
    body_html: str
    images: list
    excerpt_html: str | None = None


def _parse_frontmatter(text):
    parts = text.split('---')
    if len(parts) < 3:
        return {}, text.strip()
    fm = {}
    lines = parts[1].splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        key, sep, value = line.partition(':')
        if sep:
            key = key.strip()
            value = value.strip()
            if not value:
                items = []
                i += 1
                while i < len(lines) and lines[i].strip().startswith('- '):
                    items.append(lines[i].strip()[2:])
                    i += 1
                fm[key] = items
                continue
            else:
                fm[key] = value
        i += 1
    body = '---'.join(parts[2:]).strip()
    return fm, body


def _format_date_uk(date_str):
    d = _date.fromisoformat(date_str)
    return f"{d.day} {d.strftime('%B %Y')}"


def parse_post(md_text, post_id, image_filenames):
    fm, body = _parse_frontmatter(md_text)

    for key in fm:
        if key not in _ALLOWED_FRONTMATTER_KEYS:
            print(f"Warning: Post {post_id} has unknown frontmatter key: '{key}'")

    date_str = fm.get('date') or None
    title = fm.get('title') or None
    alt_texts = fm.get('images') or []

    more_parts = body.split('<!-- more -->', 1)
    body_html = _markdown.markdown(more_parts[0] + '\n\n' + more_parts[1]) if len(more_parts) == 2 else _markdown.markdown(body) if body else ''
    excerpt_html = _markdown.markdown(more_parts[0].strip()) if len(more_parts) == 2 else None

    sorted_filenames = sorted(
        image_filenames,
        key=lambda f: int(re.search(r'-image-(\d+)', f).group(1)),
    )

    images = [
        Image(filename=f, alt=str(alt_texts[i]) if i < len(alt_texts) else "")
        for i, f in enumerate(sorted_filenames)
    ]

    return Post(
        id=post_id,
        date=date_str,
        date_uk=_format_date_uk(date_str) if date_str else None,
        title=title,
        url=f"{post_id}.html",
        body_html=body_html,
        images=images,
        excerpt_html=excerpt_html,
    )
