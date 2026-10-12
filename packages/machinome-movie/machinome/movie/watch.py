"""`python -m machinome.movie watch`: a movie evaluated again each time a
file of its project changes (the player-page change).

A change is found by comparing every file's status, polled at an interval:
its size, its modification time and its inode, and which files there are.
Directories named `_build` (the tools' products), `.git` (Git's store) and
`__pycache__` (what evaluation's own imports write) are passed over at any
depth. Each evaluation is the `evaluate` command run in a process of its
own: importing a project's modules again in one process keeps the modules,
and the classes they declared, from before, so a fresh process is what
evaluates exactly what `evaluate` would. Standard library only.
"""

import os
import subprocess
import sys
import time

PASSED_OVER = frozenset({'_build', '.git', '__pycache__'})


def listing(project):
    """Every file under `project` by its path relative to it ('/'-separated),
    with its (size, modification time in nanoseconds, inode)."""
    root = os.path.abspath(project)
    found = {}
    for directory, directories, files in os.walk(root):
        directories[:] = sorted(d for d in directories if d not in PASSED_OVER)
        for name in files:
            path = os.path.join(directory, name)
            try:
                status = os.stat(path)
            except FileNotFoundError:
                continue
            found[os.path.relpath(path, root).replace(os.sep, '/')] = (
                status.st_size, status.st_mtime_ns, status.st_ino)
    return found


class Watch:
    """The loop: `start()` evaluates once and takes the listing; each `step()`
    sleeps one interval, takes the listing again and evaluates once when it
    differs, returning whether it did. `evaluate`, `files` and `sleep` are
    injected, so a test drives it without a clock or a project."""

    def __init__(self, *, evaluate, files, sleep=time.sleep, interval=0.5):
        self.evaluate, self.files, self.sleep, self.interval = evaluate, files, sleep, interval
        self.seen = None

    def start(self):
        self.seen = self.files()
        self.evaluate()

    def step(self):
        self.sleep(self.interval)
        now = self.files()
        if now == self.seen:
            return False
        self.seen = now
        self.evaluate()
        return True

    def run(self):
        self.start()
        while True:
            self.step()


def evaluation(project, movie, out=None):
    """The `evaluate` command, run by this interpreter in a process of its
    own, printing the document's path or the refusal as it does."""
    command = [sys.executable, '-m', 'machinome.movie', 'evaluate', project, movie]
    if out:
        command += ['--out', out]

    def evaluate():
        sys.stdout.flush()
        subprocess.run(command, check=False)
    return evaluate


def watch(project, movie, *, out=None, interval=0.5):
    """Evaluates the movie, then again on every change, until interrupted."""
    Watch(evaluate=evaluation(project, movie, out), files=lambda: listing(project), interval=interval).run()
