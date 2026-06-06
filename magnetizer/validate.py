import re
import sys
from pathlib import Path


_MD_PATTERN = re.compile(r'^([1-9]\d*)\.md$')
_IMAGE_PATTERN = re.compile(r'^([1-9]\d*)-image-(\d{2})\.(jpg|jpeg|png)$')
_ABOUT_IMAGE_PATTERN = re.compile(r'^about-image-(\d{2})\.(jpg|jpeg|png)$')


def _error(msg):
    print(f"Error: {msg}", file=sys.stderr)
    sys.exit(1)


def validate_config(config):
    if not config.get("site_url"):
        _error("'site_url' is required in config.yaml — set it to the absolute base URL of your site, e.g. https://example.github.io")


def validate_project(cwd):
    cwd = Path(cwd)
    for name in ("content", "dist", "templates", "resources"):
        if not (cwd / name).is_dir():
            _error(f"required directory '{name}/' not found in {cwd}")
    if not (cwd / "config.yaml").is_file():
        _error(f"required file 'config.yaml' not found in {cwd}")
    if not (cwd / "templates" / "index.html").is_file():
        _error("required template 'templates/index.html' not found — create it with MAGNETIZER_TITLE and MAGNETIZER_CONTENT placeholders")


def validate_content(content_dir):
    content_dir = Path(content_dir)
    files = [f.name for f in content_dir.iterdir() if not f.name.startswith('.')]

    md_ids = set()
    image_ids = set()
    has_about = 'about.md' in files
    has_about_images = any(_ABOUT_IMAGE_PATTERN.match(n) for n in files)

    for name in files:
        if name in ('about.md', 'cookies.md'):
            continue
        if _ABOUT_IMAGE_PATTERN.match(name):
            if not has_about:
                _error(f"image file '{name}' has no matching about.md in content/")
            continue
        if name.endswith('.md'):
            m = _MD_PATTERN.match(name)
            if not m:
                _error(f"invalid markdown filename '{name}' in content/ (expected {{post-id}}.md with no leading zeros)")
            md_ids.add(int(m.group(1)))
        elif re.search(r'-image-', name) or any(name.endswith(ext) for ext in ('.jpg', '.jpeg', '.png', '.gif')):
            m = _IMAGE_PATTERN.match(name)
            if not m:
                _error(f"invalid image filename '{name}' in content/")
            image_ids.add(int(m.group(1)))
        else:
            _error(f"unrecognised file '{name}' in content/")

    if not md_ids:
        _error("no .md files found in content/")

    for img_id in image_ids:
        if img_id not in md_ids:
            orphans = [n for n in files if (m := _IMAGE_PATTERN.match(n)) and int(m.group(1)) == img_id]
            _error(f"image file '{orphans[0]}' has no matching {img_id}.md in content/")
