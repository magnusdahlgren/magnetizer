import re
import shutil
from pathlib import Path


def get_next_post_id(content_dir: Path) -> int:
    ids = []
    for f in content_dir.iterdir():
        m = re.match(r'^(\d+)', f.name)
        if m:
            ids.append(int(m.group(1)))
    return max(ids) + 1 if ids else 1


def build_markdown(date_str: str, title: str | None) -> str:
    if title:
        return f"---\ndate: {date_str}\ntitle: {title}\n---\n"
    return f"---\ndate: {date_str}\n---\n"


def copy_images(images: list, content_dir: Path, post_id: int) -> None:
    counter = 1
    for img in images:
        src = Path(img)
        if not src.is_file():
            print(f"Image {src.name} could not be found!")
            continue
        dest = content_dir / f"{post_id}-image-{counter:02d}{src.suffix.lower()}"
        shutil.copy2(src, dest)
        counter += 1
