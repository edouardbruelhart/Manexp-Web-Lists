"""Tests for main.py"""

from unittest.mock import Mock

import manexp_web_lists.main as main_module


def test_main_calls_fetch_taxa(monkeypatch):
    mock_fetch = Mock()

    monkeypatch.setattr(main_module, "fetch_taxa", mock_fetch)

    main_module.main()

    mock_fetch.assert_called_once()


def test_main_catches_exception_and_prints(monkeypatch, capsys):
    def raise_error():
        raise RuntimeError("boom")

    monkeypatch.setattr(main_module, "fetch_taxa", raise_error)

    main_module.main()

    captured = capsys.readouterr()
    assert "An error occurred in the main process: boom" in captured.out


def test_main_does_not_raise(monkeypatch):
    def raise_error():
        raise ValueError("fail")

    monkeypatch.setattr(main_module, "fetch_taxa", raise_error)

    # This should NOT raise
    main_module.main()
