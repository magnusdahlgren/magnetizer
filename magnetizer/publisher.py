import subprocess


def publish(dist_dir, timestamp):
    subprocess.run(["git", "add", "."], cwd=dist_dir, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    has_staged = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=dist_dir).returncode != 0
    if has_staged:
        subprocess.run(["git", "commit", "-m", f"Build {timestamp}"], cwd=dist_dir, check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["git", "push", "origin", "main"], cwd=dist_dir, check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return

    result = subprocess.run(
        ["git", "rev-list", "origin/main..HEAD", "--count"],
        cwd=dist_dir, capture_output=True, text=True,
    )
    if result.stdout.strip() != "0":
        subprocess.run(["git", "push", "origin", "main"], cwd=dist_dir, check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return

    print("Nothing to publish — no changes since last build.")
