from pathlib import Path

import yaml

DEFAULTS = {
    "site_title": "My Blog",
    "site_url": "",
    "image_max_dimension": 1600,
    "image_quality": 75,
    "posts_per_page": 12,
    "micro_post_max_length": 180,
    "index_meta_description": None,
}


def load_config(path):
    config = dict(DEFAULTS)
    p = Path(path)
    if p.is_file():
        data = yaml.safe_load(p.read_text()) or {}
        for key in DEFAULTS:
            if key in data:
                config[key] = data[key]
    return config
