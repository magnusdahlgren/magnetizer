import subprocess


def _run_git(cmd, *, cwd):
    try:
        return subprocess.run(
            cmd,
            cwd=cwd,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        msg = (e.stderr or "").strip()
        raise RuntimeError(f"Git command failed: {' '.join(cmd)}\n{msg}") from e


def publish(dist_dir, timestamp):
    _run_git(["git", "add", "."], cwd=dist_dir)

    diff = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=dist_dir, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True,
    )
    if diff.returncode == 0:
        has_staged = False
    elif diff.returncode == 1:
        has_staged = True
    else:
        raise RuntimeError(f"Git command failed: git diff --cached --quiet\n{(diff.stderr or '').strip()}")

    if has_staged:
        _run_git(["git", "commit", "-m", f"Build {timestamp}"], cwd=dist_dir)
        _run_git(["git", "push", "origin", "main"], cwd=dist_dir)
        return

    ahead = subprocess.run(
        ["git", "rev-list", "origin/main..HEAD", "--count"],
        cwd=dist_dir, capture_output=True, text=True,
    )
    if ahead.returncode != 0:
        raise RuntimeError(f"Git command failed: git rev-list origin/main..HEAD --count\n{(ahead.stderr or '').strip()}")
    if ahead.stdout.strip() != "0":
        _run_git(["git", "push", "origin", "main"], cwd=dist_dir)
        return

    print("Nothing to publish — no changes since last build.")
