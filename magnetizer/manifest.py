import json
import re
from pathlib import Path


def load_manifest(path):
    p = Path(path)
    if not p.is_file():
        return {}
    return json.loads(p.read_text())


def save_manifest(content_dir, path):
    data = {}
    for f in Path(content_dir).iterdir():
        if not f.name.startswith('.'):
            data[f.name] = {"mtime": f.stat().st_mtime}
    Path(path).write_text(json.dumps(data, indent=2))


def _post_id_from_filename(name):
    m = re.match(r'^(\d+)', name)
    return int(m.group(1)) if m else None


def get_changed_post_ids(content_dir, manifest):
    content_dir = Path(content_dir)
    current_files = {
        f.name: f.stat().st_mtime
        for f in content_dir.iterdir()
        if not f.name.startswith('.')
    }

    changed = set()

    for name, mtime in current_files.items():
        if name not in manifest or manifest[name]["mtime"] != mtime:
            post_id = _post_id_from_filename(name)
            if post_id is not None:
                changed.add(post_id)

    for name in manifest:
        if name not in current_files:
            post_id = _post_id_from_filename(name)
            if post_id is not None:
                changed.add(post_id)

    return changed
