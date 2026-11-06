# gitpulse

A quick picture of your own commit activity across the git repos on your
machine: how many commits, how many active days, your current streak,
which weekdays and hours you actually work, which repos and file types get
the most attention.

I wanted the "contribution graph" feeling for work that never hits GitHub
(local experiments, repos on other hosts), and I wanted it in the terminal.

```
$ gitpulse ~/code --weeks 8
gitpulse  ·  me@example.com  ·  since 90 days ago  ·  6 repo(s) scanned

commits:        87  across 6 repo(s), 41 active day(s)
lines:          +4120 / -1733
streak:         3 day(s) now, 9 longest
busiest day:    2026-10-14 (9 commits)

last 8 weeks (commits per week, oldest first)
   - 7  ████████                       6
   - 6  ████████████████               12
   ...
   this  ██████████████████████████████ 22

by weekday
  Mon  ████████████████████           14
  Tue  ██████████████████████████████ 21
  ...
```

## Who it's for

Me, mostly, to see whether I'm actually putting time into side projects.
Useful for anyone who keeps several repos locally and is curious about their
own habits.

## Built with

- Python 3.9+, standard library only. It shells out to `git`, so git must be
  on your PATH.
- `pytest` for the tests.

## Install

```sh
git clone https://github.com/ksliu0307us-ua/gitpulse.git
cd gitpulse
pip install -e .
```

Or run it without installing: `python -m gitpulse.cli ...`.

## Usage

```sh
gitpulse                       # the repo you're in (or repos under it)
gitpulse ~/code ~/work         # scan folders for repos, up to 2 levels deep
gitpulse --since "1 year ago"  # anything git --since understands
gitpulse --weeks 26            # longer weekly chart
gitpulse --hours               # add a by-hour-of-day chart
gitpulse --author alice        # someone else (matches name or email)
gitpulse --all-authors         # the whole team
gitpulse --json                # machine-readable output
gitpulse --depth 4             # look deeper for nested repos
```

By default only commits made with your `git config user.email` are counted,
across all branches, merges excluded.

## What it does *not* do

It never contacts GitHub or any network. It reads `git log` locally and
prints aggregates; it doesn't store anything. If you point it at a shared
repo with `--all-authors`, the per-author filtering is simply off; it still
only prints totals, never names or emails.

## Running the tests

```sh
pip install pytest
pytest
```

One test creates a throwaway git repo in a temp folder and is skipped if
git isn't installed.

## Roadmap

See [ROADMAP.md](ROADMAP.md). Issues and PRs welcome.

## License

MIT. See [LICENSE](LICENSE).
