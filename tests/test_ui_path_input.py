"""Tests for the recent-paths history logic behind path_input_with_history."""

from pathlib import Path

from skillnir.ui.components.path_input import MAX_RECENT, merge_recent_paths


class TestMergeRecentPaths:
    def test_adds_to_front_of_empty_list(self):
        assert merge_recent_paths([], "/tmp/proj") == ["/tmp/proj"]

    def test_most_recent_first(self):
        result = merge_recent_paths(["/a"], "/b")
        assert result == ["/b", "/a"]

    def test_dedupes_and_moves_existing_to_front(self):
        result = merge_recent_paths(["/a", "/b", "/c"], "/c")
        assert result == ["/c", "/a", "/b"]
        assert len(result) == len(set(result))

    def test_empty_or_whitespace_is_ignored(self):
        assert merge_recent_paths(["/a"], "") == ["/a"]
        assert merge_recent_paths(["/a"], "   ") == ["/a"]

    def test_whitespace_is_stripped(self):
        assert merge_recent_paths([], "  /tmp/proj  ") == ["/tmp/proj"]

    def test_caps_at_max_items(self):
        existing = [f"/p{i}" for i in range(MAX_RECENT)]
        result = merge_recent_paths(existing, "/new")
        assert len(result) == MAX_RECENT
        assert result[0] == "/new"
        assert f"/p{MAX_RECENT - 1}" not in result

    def test_respects_custom_max_items(self):
        result = merge_recent_paths(["/a", "/b", "/c"], "/d", max_items=2)
        assert result == ["/d", "/a"]

    def test_expands_home_so_same_dir_is_not_stored_twice(self):
        home = str(Path.home())
        result = merge_recent_paths([home], "~")
        assert result == [home]

    def test_does_not_mutate_input_list(self):
        original = ["/a", "/b"]
        merge_recent_paths(original, "/c")
        assert original == ["/a", "/b"]
