"""Tests for wiki_annotate.utils module."""
import logging
import time
from unittest.mock import patch

import pytest

from wiki_annotate.utils import catchtime, timing, in_container


class TestCatchtime:
    def test_returns_elapsed_time(self):
        with catchtime() as t:
            time.sleep(0.05)
        elapsed = t()
        assert elapsed >= 0.04  # allow some slack
        assert elapsed < 1.0

    def test_callable_in_context(self):
        with catchtime() as t:
            assert callable(t)

    def test_increases_over_time(self):
        with catchtime() as t:
            t1 = t()
            time.sleep(0.02)
            t2 = t()
        assert t2 > t1


class TestTiming:
    def test_preserves_return_value(self):
        @timing
        def add(a, b):
            return a + b

        assert add(1, 2) == 3

    def test_preserves_function_name(self):
        @timing
        def my_func():
            pass

        assert my_func.__name__ == "my_func"

    def test_logs_debug_message(self, caplog):
        @timing
        def slow_fn():
            time.sleep(0.01)
            return 42

        with caplog.at_level(logging.DEBUG):
            result = slow_fn()

        assert result == 42
        assert any("func:'slow_fn' took:" in r.message for r in caplog.records)

    def test_passes_args_and_kwargs(self):
        @timing
        def fn(a, b, c=None):
            return (a, b, c)

        assert fn(1, 2, c=3) == (1, 2, 3)


class TestInContainer:
    @patch("wiki_annotate.utils.os.path.exists", return_value=False)
    @patch("wiki_annotate.utils.os.getenv", return_value=None)
    def test_not_in_container(self, mock_getenv, mock_exists):
        assert in_container() is False

    @patch("wiki_annotate.utils.os.path.exists", return_value=False)
    @patch("wiki_annotate.utils.os.getenv", return_value="docker")
    def test_container_env_var(self, mock_getenv, mock_exists):
        assert in_container() is True

    @patch("wiki_annotate.utils.os.getenv", return_value=None)
    @patch("wiki_annotate.utils.os.path.exists")
    def test_dockerenv_file(self, mock_exists, mock_getenv):
        def exists_side_effect(path):
            return path == "./dockerenv"
        mock_exists.side_effect = exists_side_effect
        assert in_container() is True

    @patch("wiki_annotate.utils.os.getenv", return_value=None)
    @patch("wiki_annotate.utils.os.path.exists", return_value=False)
    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_no_proc_file(self, mock_open, mock_exists, mock_getenv):
        # os.path.exists returns False for everything -> no container
        assert in_container() is False

    @patch("wiki_annotate.utils.os.getenv", return_value=None)
    @patch("wiki_annotate.utils.os.path.exists")
    @patch("builtins.open")
    def test_docker_in_proc(self, mock_open, mock_exists, mock_getenv):
        mock_exists.side_effect = lambda p: p == r'/proc/1/sched'
        mock_open.return_value.__enter__ = lambda s: s
        mock_open.return_value.__exit__ = lambda s, *a: None
        mock_open.return_value.read.return_value = "docker something"
        assert in_container() is True
