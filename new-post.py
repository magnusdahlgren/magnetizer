#!/usr/bin/env python3
import argparse
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from magnetizer.post import build_markdown, copy_images, get_next_post_id

IMAGE_EXTS = {".jpg", ".jpeg", ".png"}


def main():
    parser = argparse.ArgumentParser(
        prog="new-post.py",
        description="Create a new post in the current directory.",
    )
    parser.add_argument("args", nargs="*", metavar="IMAGES/TITLE")
    parsed = parser.parse_args()

    content_dir = Path.cwd() / "content"
    if not content_dir.is_dir():
        print("Error: no content/ directory found in the current directory.", file=sys.stderr)
        sys.exit(1)

    images = [a for a in parsed.args if Path(a).suffix.lower() in IMAGE_EXTS]
    non_images = [a for a in parsed.args if Path(a).suffix.lower() not in IMAGE_EXTS]
    title = non_images[0] if non_images else None

    post_id = get_next_post_id(content_dir)
    (content_dir / f"{post_id}.md").write_text(build_markdown(date.today().isoformat(), title))
    copy_images(images, content_dir, post_id)
    print(f"Post {post_id} successfully created.")


if __name__ == "__main__":
    main()
