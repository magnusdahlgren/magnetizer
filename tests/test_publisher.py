"""Tests for magnetizer/publisher.py — publish()"""

import pytest
from unittest.mock import MagicMock, call, patch
from magnetizer.publisher import publish


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_mock(has_staged_changes=True, has_unpushed_commits=False):
    """Return a side_effect function for subprocess.run."""
    def side_effect(cmd, **kwargs):
        m = MagicMock()
        m.returncode = 0
        if cmd == ["git", "diff", "--cached", "--quiet"]:
            m.returncode = 1 if has_staged_changes else 0
        elif cmd == ["git", "rev-list", "origin/main..HEAD", "--count"]:
            m.stdout = "1\n" if has_unpushed_commits else "0\n"
        return m
    return side_effect


# ---------------------------------------------------------------------------
# git add
# ---------------------------------------------------------------------------

class TestGitAdd:

    def test_git_add_dot_is_called(self, tmp_path):
        with patch("magnetizer.publisher.subprocess.run", side_effect=make_mock()) as mock_run:
            publish(tmp_path, "2026-05-24 14:32:00")
        cmds = [c.args[0] for c in mock_run.call_args_list]
        assert ["git", "add", "."] in cmds

    def test_git_add_runs_in_dist_dir(self, tmp_path):
        with patch("magnetizer.publisher.subprocess.run", side_effect=make_mock()) as mock_run:
            publish(tmp_path, "2026-05-24 14:32:00")
        add_call = next(c for c in mock_run.call_args_list if c.args[0] == ["git", "add", "."])
        assert add_call.kwargs.get("cwd") == tmp_path

    def test_git_add_called_before_commit(self, tmp_path):
        with patch("magnetizer.publisher.subprocess.run", side_effect=make_mock()) as mock_run:
            publish(tmp_path, "2026-05-24 14:32:00")
        cmds = [c.args[0] for c in mock_run.call_args_list]
        assert cmds.index(["git", "add", "."]) < cmds.index(next(c for c in cmds if c and c[0:2] == ["git", "commit"]))


# ---------------------------------------------------------------------------
# When there are changes — commit + push
# ---------------------------------------------------------------------------

class TestPublishWithChanges:

    def test_git_commit_is_called(self, tmp_path):
        with patch("magnetizer.publisher.subprocess.run", side_effect=make_mock(has_staged_changes=True)) as mock_run:
            publish(tmp_path, "2026-05-24 14:32:00")
        cmds = [c.args[0] for c in mock_run.call_args_list]
        assert any(c[:2] == ["git", "commit"] for c in cmds)

    def test_git_commit_message_format(self, tmp_path):
        with patch("magnetizer.publisher.subprocess.run", side_effect=make_mock(has_staged_changes=True)) as mock_run:
            publish(tmp_path, "2026-05-24 14:32:00")
        cmds = [c.args[0] for c in mock_run.call_args_list]
        commit_cmd = next(c for c in cmds if len(c) > 1 and c[1] == "commit")
        assert "Build 2026-05-24 14:32:00" in commit_cmd

    def test_git_push_origin_main_is_called(self, tmp_path):
        with patch("magnetizer.publisher.subprocess.run", side_effect=make_mock(has_staged_changes=True)) as mock_run:
            publish(tmp_path, "2026-05-24 14:32:00")
        cmds = [c.args[0] for c in mock_run.call_args_list]
        assert ["git", "push", "origin", "main"] in cmds

    def test_git_push_runs_in_dist_dir(self, tmp_path):
        with patch("magnetizer.publisher.subprocess.run", side_effect=make_mock(has_staged_changes=True)) as mock_run:
            publish(tmp_path, "2026-05-24 14:32:00")
        push_call = next(c for c in mock_run.call_args_list if c.args[0] == ["git", "push", "origin", "main"])
        assert push_call.kwargs.get("cwd") == tmp_path

    def test_push_called_after_commit(self, tmp_path):
        with patch("magnetizer.publisher.subprocess.run", side_effect=make_mock(has_staged_changes=True)) as mock_run:
            publish(tmp_path, "2026-05-24 14:32:00")
        cmds = [c.args[0] for c in mock_run.call_args_list]
        commit_pos = next(i for i, c in enumerate(cmds) if len(c) > 1 and c[1] == "commit")
        push_pos = cmds.index(["git", "push", "origin", "main"])
        assert commit_pos < push_pos


# ---------------------------------------------------------------------------
# When there are no changes
# ---------------------------------------------------------------------------

class TestPublishNoChanges:

    def test_prints_nothing_to_publish_message(self, tmp_path, capsys):
        with patch("magnetizer.publisher.subprocess.run", side_effect=make_mock(has_staged_changes=False)):
            publish(tmp_path, "2026-05-24 14:32:00")
        assert "Nothing to publish" in capsys.readouterr().out

    def test_no_commit_when_no_changes(self, tmp_path):
        with patch("magnetizer.publisher.subprocess.run", side_effect=make_mock(has_staged_changes=False)) as mock_run:
            publish(tmp_path, "2026-05-24 14:32:00")
        cmds = [c.args[0] for c in mock_run.call_args_list]
        assert not any(len(c) > 1 and c[1] == "commit" for c in cmds)

    def test_no_push_when_no_changes(self, tmp_path):
        with patch("magnetizer.publisher.subprocess.run", side_effect=make_mock(has_staged_changes=False)) as mock_run:
            publish(tmp_path, "2026-05-24 14:32:00")
        cmds = [c.args[0] for c in mock_run.call_args_list]
        assert ["git", "push", "origin", "main"] not in cmds


# ---------------------------------------------------------------------------
# When there are unpushed commits but no new staged changes
# ---------------------------------------------------------------------------

class TestPublishWithUnpushedCommits:

    def test_push_called_when_unpushed_commits_exist(self, tmp_path):
        with patch("magnetizer.publisher.subprocess.run", side_effect=make_mock(has_staged_changes=False, has_unpushed_commits=True)) as mock_run:
            publish(tmp_path, "2026-05-24 14:32:00")
        cmds = [c.args[0] for c in mock_run.call_args_list]
        assert ["git", "push", "origin", "main"] in cmds

    def test_no_commit_when_only_unpushed_commits(self, tmp_path):
        with patch("magnetizer.publisher.subprocess.run", side_effect=make_mock(has_staged_changes=False, has_unpushed_commits=True)) as mock_run:
            publish(tmp_path, "2026-05-24 14:32:00")
        cmds = [c.args[0] for c in mock_run.call_args_list]
        assert not any(len(c) > 1 and c[1] == "commit" for c in cmds)

    def test_nothing_to_publish_not_printed_when_unpushed_commits(self, tmp_path, capsys):
        with patch("magnetizer.publisher.subprocess.run", side_effect=make_mock(has_staged_changes=False, has_unpushed_commits=True)):
            publish(tmp_path, "2026-05-24 14:32:00")
        assert "Nothing to publish" not in capsys.readouterr().out
