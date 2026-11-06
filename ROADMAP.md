# Roadmap

Roughly in order. Open an issue if you want one sooner.

## Soon

- [ ] Calendar heatmap: a GitHub-style grid of the last N weeks in the terminal
- [ ] `--compare "6 months ago"`: this period vs. the previous one, with deltas
- [ ] Colour output when stdout is a TTY, plain when piped
- [ ] Remember scan paths in a config file (`~/.config/gitpulse.toml`) so plain `gitpulse` works from anywhere
- [ ] Honour `--since` relative to the author date timezone consistently (currently git's interpretation)
- [ ] Show the longest gap without commits, not just the longest streak

## Next

- [ ] Per-repo detail view: `gitpulse --repo myproj` with its own charts
- [ ] Top files by churn (most edited paths) and biggest single commits
- [ ] Commit-message stats: average length, share of "fix"/"wip"/conventional-commit prefixes
- [ ] Time-of-week heatmap (weekday × hour)
- [ ] Export: CSV of commits per day, and an SVG of the weekly chart for a README
- [ ] Multiple emails for one person (`--author` accepting several values)

## Later / maybe

- [ ] A small HTML report (`gitpulse --html report.html`) with the same numbers
- [ ] Cache parsed logs per repo and only re-read new commits
- [ ] Optional GitHub API source so remote-only repos count too
- [ ] Publish to PyPI

## Housekeeping

- [ ] Tests for the CLI and report rendering (snapshot a small report)
- [ ] GitHub Actions running `pytest` on Linux, macOS and Windows (git path/encoding quirks)
- [ ] Type hints and a `mypy` pass
- [ ] CHANGELOG.md starting at 0.2.0
