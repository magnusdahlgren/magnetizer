import json
import re
from pathlib import Path


def load_manifest(path):
    p = Path(path)
    if not p.is_file():
        return {}
    return json.loads(p.read_text())


def save_manifest(content_dir, path, resources_dir=None):
    data = {}
    for f in Path(content_dir).iterdir():
        if not f.name.startswith('.'):
            data[f.name] = {"mtime": f.stat().st_mtime}
    if resources_dir is not None:
        resources_dir = Path(resources_dir)
        if resources_dir.exists():
            for f in resources_dir.iterdir():
                if not f.name.startswith('.'):
                    data[f"resources/{f.name}"] = {"mtime": f.stat().st_mtime}
    Path(path).write_text(json.dumps(data, indent=2))


def _post_id_from_filename(name):
    m = re.match(r'^(\d+)', name)
    return int(m.group(1)) if m else None


def get_changed_resource_filenames(resources_dir, manifest):
    resources_dir = Path(resources_dir)
    current_files = {}
    if resources_dir.exists():
        for f in resources_dir.iterdir():
            if not f.name.startswith('.'):
                current_files[f.name] = f.stat().st_mtime

    changed = set()
    for name, mtime in current_files.items():
        key = f"resources/{name}"
        if key not in manifest or manifest[key]["mtime"] != mtime:
            changed.add(name)
    for key in manifest:
        if key.startswith("resources/"):
            name = key[len("resources/"):]
            if name not in current_files:
                changed.add(name)
    return changed


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
