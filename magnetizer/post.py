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


def build_markdown(date_str: str, title: str | None, image_count: int = 0) -> str:
    lines = ["---", f"date: {date_str}"]
    if title:
        lines.append(f"title: {title}")
    if image_count > 0:
        lines.append("images:")
        for i in range(1, image_count + 1):
            lines.append(f"  - Image {i}")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def copy_images(images: list, content_dir: Path, post_id: int) -> int:
    counter = 1
    for img in images:
        src = Path(img)
        if not src.is_file():
            print(f"Image {src.name} could not be found!")
            continue
        dest = content_dir / f"{post_id}-image-{counter:02d}{src.suffix.lower()}"
        shutil.copy2(src, dest)
        counter += 1
    return counter - 1
