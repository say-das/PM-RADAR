from datetime import date

import pytest

from scripts.deliver.email_sender import find_latest_report

TODAY = date(2026, 11, 17)


def _make(tmp_path, *names):
    for n in names:
        (tmp_path / n).write_text("x")


def test_picks_newest_by_filename_not_mtime(tmp_path):
    _make(tmp_path, "2026-11-16.md", "2026-07-13.md")
    # make the stale file the most recently modified
    (tmp_path / "2026-07-13.md").write_text("newer mtime")
    assert find_latest_report(tmp_path, today=TODAY).name == "2026-11-16.md"


def test_refuses_stale_report(tmp_path):
    _make(tmp_path, "2026-07-13.md")
    with pytest.raises(ValueError, match="refusing to send"):
        find_latest_report(tmp_path, today=TODAY)


def test_refuses_future_dated_report(tmp_path):
    _make(tmp_path, "2026-12-01.md")
    with pytest.raises(ValueError):
        find_latest_report(tmp_path, today=TODAY)


def test_errors_when_no_reports(tmp_path):
    with pytest.raises(ValueError, match="No dated reports"):
        find_latest_report(tmp_path, today=TODAY)


def test_ignores_non_dated_files(tmp_path):
    _make(tmp_path, "notes.md", "2026-11-17.md")
    assert find_latest_report(tmp_path, today=TODAY).name == "2026-11-17.md"
