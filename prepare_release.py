import re
import subprocess
import sys
from pathlib import Path

def update_file_version(filepath, pattern, new_version):
    text = Path(filepath).read_text()
    updated, count = re.subn(pattern, f'\\g<1>{new_version}\\g<2>', text)
    if count == 0:
        print(f"[WARN] No version match found in {filepath}")
    else:
        print(f"[OK] Updated version in {filepath}")
        Path(filepath).write_text(updated)

def git_commit_and_tag(new_version):
    subprocess.run(["git", "add", "setup.py", "pyproject.toml"], check=True)
    subprocess.run(["git", "commit", "-m", f"Release v{new_version}"], check=True)
    subprocess.run(["git", "tag", f"v{new_version}"], check=True)
    subprocess.run(["git", "push"], check=True)
    subprocess.run(["git", "push", "--tags"], check=True)
    print(f"[OK] Tagged and pushed v{new_version}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python prepare_release.py NEW_VERSION")
        sys.exit(1)

    new_version = sys.argv[1]
    print(f"Preparing release for version: {new_version}")

    update_file_version(
        "setup.py",
        r'(version\s*=\s*[\'"])([\d\.]+)([\'"])',
        new_version
    )

    update_file_version(
        "pyproject.toml",
        r'(version\s*=\s*")[\d\.]+(")',
        new_version
    )

    git_commit_and_tag(new_version)

if __name__ == "__main__":
    main()
