from magnetizer.content import Image, Post

TEMPLATE = (
    "<!DOCTYPE html><html><head><title>MAGNETIZER_TITLE</title></head>"
    "<body>MAGNETIZER_CONTENT</body></html>"
)
MINIMAL_MD = "---\ndate: 2026-05-24\n---\n\nHello world\n"
_DEFAULT_CONFIG = "site_title: Test Blog\nsite_url: https://example.github.io\nposts_per_page: 2\n"


def make_project(tmp_path, posts=None, config=_DEFAULT_CONFIG):
    (tmp_path / "content").mkdir()
    (tmp_path / "dist").mkdir()
    (tmp_path / "templates").mkdir()
    (tmp_path / "resources").mkdir()
    (tmp_path / "resources" / "style.css").write_text("body {}")
    (tmp_path / "templates" / "index.html").write_text(TEMPLATE)
    (tmp_path / "config.yaml").write_text(config)
    if posts:
        for post_id, md_text in posts.items():
            (tmp_path / "content" / f"{post_id}.md").write_text(md_text)
    return tmp_path


def make_post(
    id=1,
    date="2026-05-24",
    date_uk="24 May 2026",
    title="My Post",
    body_html="<p>Hello</p>",
    images=None,
):
    image_objects = [
        img if isinstance(img, Image) else Image(filename=img, alt="")
        for img in (images or [])
    ]
    return Post(
        id=id,
        date=date,
        date_uk=date_uk,
        title=title,
        url=f"{id}.html",
        body_html=body_html,
        images=image_objects,
    )


def make_content(tmp_path, files):
    content = tmp_path / "content"
    content.mkdir(exist_ok=True)
    for name, body in files.items():
        (content / name).write_bytes(body if isinstance(body, bytes) else body.encode())
    return content
