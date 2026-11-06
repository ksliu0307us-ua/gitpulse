import argparse
import json
import sys
from datetime import date

from . import gitlog, stats

BAR = "█"


def bar(n, biggest, width=30):
    if biggest == 0:
        return ""
    return BAR * max(1 if n else 0, round(n / biggest * width))


def print_report(commits, weeks, show_hours):
    if not commits:
        print("no commits matched. check --author, --since, or the paths.")
        return

    s = stats.summary(commits)
    print(f"commits:        {s['commits']}  across {s['repos']} repo(s), {s['active_days']} active day(s)")
    print(f"lines:          +{s['lines_added']} / -{s['lines_deleted']}")
    print(f"streak:         {s['current_streak']} day(s) now, {s['longest_streak']} longest")
    if s["busiest_day"]:
        d, n = s["busiest_day"]
        print(f"busiest day:    {d} ({n} commits)")

    print(f"\nlast {weeks} weeks (commits per week, oldest first)")
    totals = stats.weekly_totals(commits, weeks)
    top = max(totals)
    for i, n in enumerate(totals):
        label = "this" if i == weeks - 1 else f"-{weeks - 1 - i:>2}"
        print(f"  {label:>5}  {bar(n, top):<30} {n}")

    print("\nby weekday")
    wd = stats.by_weekday(commits)
    top = max(wd)
    for name, n in zip(stats.WEEKDAYS, wd):
        print(f"  {name}  {bar(n, top):<30} {n}")

    if show_hours:
        print("\nby hour of day")
        hours = stats.by_hour(commits)
        top = max(hours)
        for h, n in enumerate(hours):
            if n:
                print(f"  {h:02d}:00  {bar(n, top):<30} {n}")

    print("\nby repo")
    for repo, n in stats.by_repo(commits).most_common():
        print(f"  {n:>5}  {repo}")

    print("\nfile types touched")
    for ext, n in stats.by_extension(commits).most_common(8):
        print(f"  {n:>5}  {ext}")


def to_json(commits, weeks):
    s = stats.summary(commits)
    if s["busiest_day"]:
        d, n = s["busiest_day"]
        s["busiest_day"] = {"date": d.isoformat(), "commits": n}
    return {
        "summary": s,
        "weekly": stats.weekly_totals(commits, weeks),
        "by_weekday": dict(zip(stats.WEEKDAYS, stats.by_weekday(commits))),
        "by_hour": stats.by_hour(commits),
        "by_repo": dict(stats.by_repo(commits)),
        "by_extension": dict(stats.by_extension(commits).most_common(20)),
    }


def build_parser():
    p = argparse.ArgumentParser(
        prog="gitpulse",
        description="a quick picture of your commit activity across local repos",
    )
    p.add_argument("paths", nargs="*", default=["."], help="repos, or folders containing repos (default: .)")
    p.add_argument("--author", help="email or name to match (default: your git user.email)")
    p.add_argument("--all-authors", action="store_true", help="don't filter by author")
    p.add_argument("--since", default="90 days ago", help='git --since value (default: "90 days ago")')
    p.add_argument("--weeks", type=int, default=12, help="weeks to show in the weekly chart")
    p.add_argument("--depth", type=int, default=2, help="how deep to look for repos under a folder")
    p.add_argument("--hours", action="store_true", help="also show commits by hour of day")
    p.add_argument("--json", action="store_true", help="print JSON instead of a report")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)

    author = None
    if not args.all_authors:
        author = args.author or gitlog.my_email()
        if not author:
            print("couldn't read git user.email; pass --author or --all-authors", file=sys.stderr)
            return 1

    repos = []
    for p in args.paths:
        repos.extend(gitlog.find_repos(p, args.depth))
    if not repos:
        print(f"no git repositories found under: {', '.join(args.paths)}", file=sys.stderr)
        return 1

    commits = []
    try:
        for r in repos:
            commits.extend(gitlog.read_commits(r, since=args.since, author=author))
    except gitlog.GitError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(to_json(commits, args.weeks), indent=2))
    else:
        who = "everyone" if author is None else author
        print(f"gitpulse  ·  {who}  ·  since {args.since}  ·  {len(repos)} repo(s) scanned\n")
        print_report(commits, args.weeks, args.hours)
    return 0


if __name__ == "__main__":
    sys.exit(main())
