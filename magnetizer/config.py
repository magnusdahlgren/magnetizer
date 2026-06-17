from copy import deepcopy
from pathlib import Path

import yaml

DEFAULTS = {
    "site_name": "My Blog",
    "site_url": "",
    "image_max_dimension": 1600,
    "image_quality": 75,
    "posts_per_page": 12,
    "micro_post_max_length": 180,
    "index_meta_description": None,
    "index_title": None,
    "categories": {},
}


def load_config(path):
    config = deepcopy(DEFAULTS)
    p = Path(path)
    if p.is_file():
        data = yaml.safe_load(p.read_text()) or {}
        if "site_name" not in data and "site_title" in data:
            data["site_name"] = data["site_title"]
        for key in DEFAULTS:
            if key in data:
                config[key] = data[key]
    return config
