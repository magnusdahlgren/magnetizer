"""Tests for magnetizer/manifest.py — load, save, and change detection"""

import json
import time
import pytest
from pathlib import Path
from magnetizer.manifest import get_changed_post_ids, load_manifest, save_manifest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_content(tmp_path, filenames):
    content = tmp_path / "content"
    content.mkdir(exist_ok=True)
    for name in filenames:
        (content / name).write_bytes(b"x")
    return content


# ---------------------------------------------------------------------------
# load_manifest
# ---------------------------------------------------------------------------

class TestLoadManifest:

    def test_returns_empty_dict_when_file_absent(self, tmp_path):
        assert load_manifest(tmp_path / "manifest.json") == {}

    def test_loads_existing_manifest(self, tmp_path):
        data = {"1.md": {"mtime": 1748123456.0}}
        p = tmp_path / "manifest.json"
        p.write_text(json.dumps(data))
        assert load_manifest(p) == data

    def test_loads_manifest_with_multiple_entries(self, tmp_path):
        data = {
            "1.md": {"mtime": 1748123456.0},
            "1-image-01.jpg": {"mtime": 1748123457.0},
            "2.md": {"mtime": 1748123789.0},
        }
        p = tmp_path / "manifest.json"
        p.write_text(json.dumps(data))
        result = load_manifest(p)
        assert result == data


# ---------------------------------------------------------------------------
# save_manifest
# ---------------------------------------------------------------------------

class TestSaveManifest:

    def test_creates_manifest_file(self, tmp_path):
        content = make_content(tmp_path, ["1.md"])
        p = tmp_path / "manifest.json"
        save_manifest(content, p)
        assert p.exists()

    def test_manifest_is_valid_json(self, tmp_path):
        content = make_content(tmp_path, ["1.md"])
        p = tmp_path / "manifest.json"
        save_manifest(content, p)
        data = json.loads(p.read_text())
        assert isinstance(data, dict)

    def test_manifest_contains_each_content_file(self, tmp_path):
        content = make_content(tmp_path, ["1.md", "1-image-01.jpg", "2.md"])
        p = tmp_path / "manifest.json"
        save_manifest(content, p)
        data = json.loads(p.read_text())
        assert set(data.keys()) == {"1.md", "1-image-01.jpg", "2.md"}

    def test_manifest_entries_have_mtime(self, tmp_path):
        content = make_content(tmp_path, ["1.md"])
        p = tmp_path / "manifest.json"
        save_manifest(content, p)
        data = json.loads(p.read_text())
        assert "mtime" in data["1.md"]
        assert isinstance(data["1.md"]["mtime"], float)

    def test_mtime_matches_actual_file_mtime(self, tmp_path):
        content = make_content(tmp_path, ["1.md"])
        p = tmp_path / "manifest.json"
        save_manifest(content, p)
        actual_mtime = (content / "1.md").stat().st_mtime
        data = json.loads(p.read_text())
        assert data["1.md"]["mtime"] == actual_mtime

    def test_overwrites_existing_manifest(self, tmp_path):
        content = make_content(tmp_path, ["1.md"])
        p = tmp_path / "manifest.json"
        p.write_text(json.dumps({"old.md": {"mtime": 0.0}}))
        save_manifest(content, p)
        data = json.loads(p.read_text())
        assert "old.md" not in data
        assert "1.md" in data


# ---------------------------------------------------------------------------
# get_changed_post_ids
# ---------------------------------------------------------------------------

class TestGetChangedPostIds:

    def test_all_posts_changed_when_manifest_empty(self, tmp_path):
        content = make_content(tmp_path, ["1.md", "2.md"])
        changed = get_changed_post_ids(content, {})
        assert changed == {1, 2}

    def test_no_changes_when_mtimes_match(self, tmp_path):
        content = make_content(tmp_path, ["1.md"])
        mtime = (content / "1.md").stat().st_mtime
        manifest = {"1.md": {"mtime": mtime}}
        assert get_changed_post_ids(content, manifest) == set()

    def test_detects_modified_md_file(self, tmp_path):
        content = make_content(tmp_path, ["1.md"])
        manifest = {"1.md": {"mtime": 0.0}}  # stale mtime
        assert 1 in get_changed_post_ids(content, manifest)

    def test_detects_new_md_file_not_in_manifest(self, tmp_path):
        content = make_content(tmp_path, ["1.md", "2.md"])
        mtime = (content / "1.md").stat().st_mtime
        manifest = {"1.md": {"mtime": mtime}}  # 2.md absent
        assert 2 in get_changed_post_ids(content, manifest)

    def test_detects_deleted_md_file(self, tmp_path):
        content = make_content(tmp_path, ["1.md"])
        manifest = {
            "1.md": {"mtime": (content / "1.md").stat().st_mtime},
            "2.md": {"mtime": 1748123456.0},  # 2.md was deleted
        }
        assert 2 in get_changed_post_ids(content, manifest)

    def test_detects_changed_image_returns_its_post_id(self, tmp_path):
        content = make_content(tmp_path, ["1.md", "1-image-01.jpg"])
        md_mtime = (content / "1.md").stat().st_mtime
        manifest = {
            "1.md": {"mtime": md_mtime},
            "1-image-01.jpg": {"mtime": 0.0},  # stale
        }
        assert 1 in get_changed_post_ids(content, manifest)

    def test_detects_new_image_returns_its_post_id(self, tmp_path):
        content = make_content(tmp_path, ["1.md", "1-image-01.jpg"])
        md_mtime = (content / "1.md").stat().st_mtime
        manifest = {"1.md": {"mtime": md_mtime}}  # image not in manifest
        assert 1 in get_changed_post_ids(content, manifest)

    def test_detects_deleted_image_returns_its_post_id(self, tmp_path):
        content = make_content(tmp_path, ["1.md"])
        md_mtime = (content / "1.md").stat().st_mtime
        manifest = {
            "1.md": {"mtime": md_mtime},
            "1-image-01.jpg": {"mtime": 1748123456.0},  # image was deleted
        }
        assert 1 in get_changed_post_ids(content, manifest)

    def test_unchanged_post_not_included(self, tmp_path):
        content = make_content(tmp_path, ["1.md", "2.md"])
        mtime1 = (content / "1.md").stat().st_mtime
        mtime2 = (content / "2.md").stat().st_mtime
        manifest = {
            "1.md": {"mtime": mtime1},
            "2.md": {"mtime": 0.0},  # only post 2 changed
        }
        changed = get_changed_post_ids(content, manifest)
        assert 1 not in changed
        assert 2 in changed

    def test_returns_set_of_integers(self, tmp_path):
        content = make_content(tmp_path, ["1.md"])
        result = get_changed_post_ids(content, {})
        assert isinstance(result, set)
        assert all(isinstance(x, int) for x in result)
