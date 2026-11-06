"""Turn a list of commits into numbers worth looking at."""

from collections import Counter
from datetime import date, timedelta
from pathlib import PurePosixPath

WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def by_day(commits):
    return Counter(c.when.date() for c in commits)


def by_weekday(commits):
    counts = Counter(c.when.weekday() for c in commits)
    return [counts.get(i, 0) for i in range(7)]


def by_hour(commits):
    counts = Counter(c.when.hour for c in commits)
    return [counts.get(h, 0) for h in range(24)]


def by_repo(commits):
    return Counter(c.repo for c in commits)


def by_extension(commits):
    counts = Counter()
    for c in commits:
        for path in c.files:
            ext = PurePosixPath(path).suffix.lower() or "(none)"
            counts[ext] += 1
    return counts


def streaks(commits, today=None):
    """(current streak, longest streak) in consecutive days with a commit."""
    days = sorted(set(c.when.date() for c in commits))
    if not days:
        return 0, 0

    longest = run = 1
    for prev, cur in zip(days, days[1:]):
        run = run + 1 if cur - prev == timedelta(days=1) else 1
        longest = max(longest, run)

    today = today or date.today()
    last = days[-1]
    if today - last > timedelta(days=1):
        current = 0
    else:
        current = 1
        i = len(days) - 1
        while i > 0 and days[i] - days[i - 1] == timedelta(days=1):
            current += 1
            i -= 1
    return current, longest


def weekly_totals(commits, weeks, today=None):
    """Commits per calendar week for the last `weeks` weeks, oldest first."""
    today = today or date.today()
    start_of_this_week = today - timedelta(days=today.weekday())
    buckets = [0] * weeks
    for c in commits:
        d = c.when.date()
        delta = (start_of_this_week - (d - timedelta(days=d.weekday()))).days // 7
        if 0 <= delta < weeks:
            buckets[weeks - 1 - delta] += 1
    return buckets


def summary(commits, today=None):
    days = by_day(commits)
    current, longest = streaks(commits, today)
    return {
        "commits": len(commits),
        "active_days": len(days),
        "repos": len(by_repo(commits)),
        "lines_added": sum(c.added for c in commits),
        "lines_deleted": sum(c.deleted for c in commits),
        "busiest_day": max(days.items(), key=lambda kv: kv[1]) if days else None,
        "current_streak": current,
        "longest_streak": longest,
    }
