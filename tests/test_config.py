"""Tests for magnetizer/config.py — load_config()"""

import pytest
from pathlib import Path
from magnetizer.config import load_config


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


def write_config(tmp_path, content):
    p = tmp_path / "config.yaml"
    p.write_text(content)
    return p


# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------

class TestDefaults:

    def test_site_name_default(self, tmp_path):
        assert load_config(tmp_path / "config.yaml")["site_name"] == "My Blog"

    def test_index_title_default(self, tmp_path):
        assert load_config(tmp_path / "config.yaml")["index_title"] is None

    def test_image_max_dimension_default(self, tmp_path):
        assert load_config(tmp_path / "config.yaml")["image_max_dimension"] == 1600

    def test_image_quality_default(self, tmp_path):
        assert load_config(tmp_path / "config.yaml")["image_quality"] == 75

    def test_posts_per_page_default(self, tmp_path):
        assert load_config(tmp_path / "config.yaml")["posts_per_page"] == 12

    def test_micro_post_max_length_default(self, tmp_path):
        assert load_config(tmp_path / "config.yaml")["micro_post_max_length"] == 180

    def test_index_meta_description_default(self, tmp_path):
        assert load_config(tmp_path / "config.yaml")["index_meta_description"] is None

    def test_missing_file_returns_all_defaults(self, tmp_path):
        config = load_config(tmp_path / "config.yaml")
        assert config == DEFAULTS


# ---------------------------------------------------------------------------
# Custom values override defaults
# ---------------------------------------------------------------------------

class TestCustomValues:

    def test_site_name_overridden(self, tmp_path):
        p = write_config(tmp_path, "site_name: My Photo Blog\n")
        assert load_config(p)["site_name"] == "My Photo Blog"

    def test_image_max_dimension_overridden(self, tmp_path):
        p = write_config(tmp_path, "image_max_dimension: 1200\n")
        assert load_config(p)["image_max_dimension"] == 1200

    def test_image_quality_overridden(self, tmp_path):
        p = write_config(tmp_path, "image_quality: 70\n")
        assert load_config(p)["image_quality"] == 70

    def test_posts_per_page_overridden(self, tmp_path):
        p = write_config(tmp_path, "posts_per_page: 6\n")
        assert load_config(p)["posts_per_page"] == 6

    def test_micro_post_max_length_overridden(self, tmp_path):
        p = write_config(tmp_path, "micro_post_max_length: 200\n")
        assert load_config(p)["micro_post_max_length"] == 200

    def test_index_meta_description_overridden(self, tmp_path):
        p = write_config(tmp_path, "index_meta_description: A blog about things.\n")
        assert load_config(p)["index_meta_description"] == "A blog about things."

    def test_all_values_overridden(self, tmp_path):
        p = write_config(tmp_path, (
            "site_name: Photos\n"
            "image_max_dimension: 1400\n"
            "image_quality: 68\n"
            "posts_per_page: 8\n"
            "micro_post_max_length: 200\n"
        ))
        config = load_config(p)
        assert config["site_name"] == "Photos"
        assert config["image_max_dimension"] == 1400
        assert config["image_quality"] == 68
        assert config["posts_per_page"] == 8
        assert config["micro_post_max_length"] == 200

    def test_partial_override_keeps_other_defaults(self, tmp_path):
        p = write_config(tmp_path, "site_name: My Photos\n")
        config = load_config(p)
        assert config["site_name"] == "My Photos"
        assert config["image_max_dimension"] == 1600
        assert config["image_quality"] == 75
        assert config["posts_per_page"] == 12

    def test_returns_only_known_keys(self, tmp_path):
        p = write_config(tmp_path, "unknown_key: whatever\n")
        config = load_config(p)
        assert set(config.keys()) == set(DEFAULTS.keys())


# ---------------------------------------------------------------------------
# Categories
# ---------------------------------------------------------------------------

class TestCategories:

    def test_categories_default_is_empty_dict(self, tmp_path):
        assert load_config(tmp_path / "config.yaml")["categories"] == {}

    def test_categories_loaded_from_config(self, tmp_path):
        p = write_config(tmp_path, "categories:\n  photography: Photography\n  travel: Travel\n")
        assert load_config(p)["categories"] == {"photography": "Photography", "travel": "Travel"}

    def test_single_category_loaded(self, tmp_path):
        p = write_config(tmp_path, "categories:\n  thoughts: Thoughts\n")
        assert load_config(p)["categories"] == {"thoughts": "Thoughts"}

    def test_categories_not_included_in_known_keys_check(self, tmp_path):
        p = write_config(tmp_path, "categories:\n  photography: Photography\n")
        config = load_config(p)
        assert "categories" in config

    def test_mutating_returned_categories_does_not_leak_into_next_load(self, tmp_path):
        config = load_config(tmp_path / "config.yaml")
        config["categories"]["photography"] = "Photography"
        fresh = load_config(tmp_path / "config.yaml")
        assert fresh["categories"] == {}
