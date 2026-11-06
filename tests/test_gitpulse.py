import shutil
import subprocess
from datetime import date, datetime, timezone

import pytest

from gitpulse import gitlog, stats
from gitpulse.gitlog import SEP, Commit

SAMPLE_LOG = (
    f"aaa{SEP}2026-11-03T09:15:00+00:00{SEP}Me@Example.com{SEP}add parser\n"
    "10\t2\tsrc/parser.py\n"
    "3\t0\tREADME.md\n"
    "\n"
    f"bbb{SEP}2026-11-04T22:40:00-08:00{SEP}me@example.com{SEP}fix: handle {SEP} in subjects? no, tabs\tand such\n"
    "-\t-\tlogo.png\n"
    "1\t1\tsrc/parser.py\n"
)


def c(day, hour=12, repo="r", email="me@example.com", files=None):
    return Commit(
        sha="x",
        when=datetime(2026, 11, day, hour, tzinfo=timezone.utc),
        email=email,
        subject="s",
        repo=repo,
        files=files or {},
    )


# --- parsing -------------------------------------------------------------------


def test_parse_log():
    commits = gitlog.parse_log(SAMPLE_LOG, "demo")
    assert len(commits) == 2
    first, second = commits
    assert first.sha == "aaa"
    assert first.email == "me@example.com"  # lowercased
    assert first.repo == "demo"
    assert first.files == {"src/parser.py": (10, 2), "README.md": (3, 0)}
    assert first.added == 13 and first.deleted == 2
    assert second.files["logo.png"] == (0, 0)  # binary
    assert second.when.hour == 22


# --- stats ---------------------------------------------------------------------


def test_streaks_consecutive():
    commits = [c(1), c(2), c(3), c(5)]
    assert stats.streaks(commits, today=date(2026, 11, 5)) == (1, 3)


def test_streak_includes_yesterday():
    commits = [c(3), c(4)]
    assert stats.streaks(commits, today=date(2026, 11, 5)) == (2, 2)


def test_streak_broken():
    commits = [c(1), c(2)]
    assert stats.streaks(commits, today=date(2026, 11, 10)) == (0, 2)


def test_streaks_empty():
    assert stats.streaks([]) == (0, 0)


def test_by_weekday_and_hour():
    commits = [c(2, 9), c(2, 9), c(7, 23)]  # 2026-11-02 is a Monday, 11-07 a Saturday
    wd = stats.by_weekday(commits)
    assert wd[0] == 2 and wd[5] == 1
    hours = stats.by_hour(commits)
    assert hours[9] == 2 and hours[23] == 1


def test_weekly_totals():
    commits = [c(2), c(3), c(5), c(6)]  # all in the week of Mon 2026-11-02
    totals = stats.weekly_totals(commits, weeks=3, today=date(2026, 11, 6))
    assert totals == [0, 0, 4]
    totals = stats.weekly_totals(commits, weeks=3, today=date(2026, 11, 13))
    assert totals == [0, 4, 0]


def test_by_extension():
    commits = [
        c(1, files={"a.py": (1, 0), "b.PY": (1, 0)}),
        c(2, files={"Makefile": (1, 0), "a.py": (0, 1)}),
    ]
    ext = stats.by_extension(commits)
    assert ext[".py"] == 3
    assert ext["(none)"] == 1


def test_summary():
    commits = [c(1, repo="a", files={"x": (5, 1)}), c(1, repo="b"), c(3, repo="a")]
    s = stats.summary(commits, today=date(2026, 11, 3))
    assert s["commits"] == 3
    assert s["active_days"] == 2
    assert s["repos"] == 2
    assert s["lines_added"] == 5 and s["lines_deleted"] == 1
    assert s["busiest_day"] == (date(2026, 11, 1), 2)
    assert s["current_streak"] == 1


# --- against a real repo ---------------------------------------------------------


@pytest.mark.skipif(shutil.which("git") is None, reason="git not installed")
def test_read_commits_from_real_repo(tmp_path):
    repo = tmp_path / "proj"
    repo.mkdir()
    env = {
        "GIT_AUTHOR_NAME": "T",
        "GIT_AUTHOR_EMAIL": "t@example.com",
        "GIT_COMMITTER_NAME": "T",
        "GIT_COMMITTER_EMAIL": "t@example.com",
    }

    def git(*a):
        subprocess.run(["git", "-C", str(repo), *a], check=True, capture_output=True, env={**env, "PATH": __import__("os").environ["PATH"]})

    git("init", "-q")
    (repo / "a.txt").write_text("one\ntwo\n")
    git("add", "a.txt")
    git("commit", "-q", "-m", "first")
    (repo / "a.txt").write_text("one\n")
    git("commit", "-q", "-am", "second")

    commits = gitlog.read_commits(repo, author="t@example.com")
    assert [x.subject for x in commits] == ["second", "first"]
    assert commits[1].files["a.txt"] == (2, 0)
    assert commits[0].files["a.txt"] == (0, 1)
    assert gitlog.find_repos(tmp_path) == [repo]
    assert gitlog.read_commits(repo, author="nobody@example.com") == []


def test_find_repos_missing_path(tmp_path):
    assert gitlog.find_repos(tmp_path / "nope") == []
