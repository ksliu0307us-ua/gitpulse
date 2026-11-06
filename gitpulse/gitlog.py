"""Pull commits out of local repositories by running `git log`.

Only the pieces we need are read: when the commit was made, who made it,
and which files changed by how many lines. Nothing leaves the machine.
"""

import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

# A line we can split safely; commit subjects can contain almost anything else.
SEP = "\x1f"
FORMAT = f"%H{SEP}%aI{SEP}%ae{SEP}%s"


class GitError(Exception):
    pass


@dataclass
class Commit:
    sha: str
    when: datetime  # timezone-aware, as the author recorded it
    email: str
    subject: str
    repo: str
    files: dict = field(default_factory=dict)  # path -> (added, deleted)

    @property
    def added(self):
        return sum(a for a, _ in self.files.values())

    @property
    def deleted(self):
        return sum(d for _, d in self.files.values())


def parse_log(text, repo):
    """Parse the output of `git log --format=FORMAT --numstat`."""
    commits = []
    current = None
    for line in text.splitlines():
        if SEP in line:
            sha, when, email, subject = line.split(SEP, 3)
            current = Commit(
                sha=sha,
                when=datetime.fromisoformat(when),
                email=email.lower(),
                subject=subject,
                repo=repo,
            )
            commits.append(current)
        elif current is not None and line.strip():
            parts = line.split("\t", 2)
            if len(parts) == 3:
                a, d, path = parts
                # binary files show up as "-", count them as zero lines
                added = int(a) if a.isdigit() else 0
                deleted = int(d) if d.isdigit() else 0
                current.files[path] = (added, deleted)
    return commits


def is_repo(path):
    return (Path(path) / ".git").exists()


def find_repos(root, depth=2):
    """Repos directly under `root`, or nested up to `depth` folders down."""
    root = Path(root)
    if not root.is_dir():
        return []
    if is_repo(root):
        return [root]
    found = []

    def walk(p, d):
        if d < 0:
            return
        try:
            children = sorted(c for c in p.iterdir() if c.is_dir() and not c.name.startswith("."))
        except PermissionError:
            return
        for c in children:
            if is_repo(c):
                found.append(c)
            else:
                walk(c, d - 1)

    walk(root, depth)
    return found


def read_commits(repo, since=None, author=None):
    cmd = ["git", "-C", str(repo), "log", "--all", "--no-merges", f"--format={FORMAT}", "--numstat"]
    if since:
        cmd.append(f"--since={since}")
    if author:
        cmd.append(f"--author={author}")
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, check=True, encoding="utf-8")
    except FileNotFoundError:
        raise GitError("git is not installed or not on PATH")
    except subprocess.CalledProcessError as e:
        raise GitError(f"git failed in {repo}: {e.stderr.strip()}")
    return parse_log(out.stdout, Path(repo).name)


def my_email():
    try:
        out = subprocess.run(
            ["git", "config", "user.email"], capture_output=True, text=True, check=True
        )
        return out.stdout.strip().lower() or None
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None
