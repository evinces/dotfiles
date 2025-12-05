#!/usr/bin/env python3

import argparse
import os
import socket
import subprocess
from pathlib import Path


def get_git_files(repo_path: Path) -> list[str]:
    """Get the list of files tracked by git."""
    try:
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip().split("\n")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Error getting git files: {e}")
        return []


def get_linkignore_patterns() -> list[str]:
    """Get the patterns to ignore from the linkignore file."""
    linkignore = Path.cwd() / "linkignore"
    if not linkignore.is_file():
        return []
    with open(linkignore, "r") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


def create_symlink(source: Path, target: Path, force: bool):
    """Create a symlink from source to target."""
    if target.exists() and not target.is_symlink() and not force:
        print(f"Skipping '{target}': file already exists")
        return

    if not target.parent.exists():
        target.parent.mkdir(parents=True)
        print(f"mkdir -p {target.parent}")

    if target.exists():
        target.unlink()
        print(f"rm {target}")

    target.symlink_to(source)
    print(f"ln -s {source} {target}")


def main():
    """Main function to parse arguments and create links."""
    parser = argparse.ArgumentParser(
        description="Create dotfile symlinks based on environment."
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="overwrite existing files",
    )
    env_group = parser.add_mutually_exclusive_group()
    env_group.add_argument(
        "-d",
        "--desktop",
        action="store_const",
        const="desktop",
        dest="environment",
        help="force desktop mode",
    )
    env_group.add_argument(
        "-l",
        "--laptop",
        action="store_const",
        const="laptop",
        dest="environment",
        help="force laptop mode",
    )
    args = parser.parse_args()

    environment = args.environment
    if not environment:
        hostname = socket.gethostname()
        if "laptop" in hostname:
            environment = "laptop"
        elif "desktop" in hostname:
            environment = "desktop"
        else:
            print(f"Unknown environment on host '{hostname}' aborting...")
            print()
            parser.print_help()
            return

    print(f"Creating symlinks for '{environment}' environment...")

    home = Path.home()
    dotfiles_home = Path(os.environ.get("DOTFILES_HOME", Path.cwd()))
    config_home = Path(os.environ.get("XDG_CONFIG_HOME", home / ".config"))

    git_files = get_git_files(dotfiles_home)
    ignore_patterns = get_linkignore_patterns()
    dotfiles = [f for f in git_files if not any(p in f for p in ignore_patterns)]

    for dotfile_path in dotfiles:
        source_path = dotfiles_home / dotfile_path
        target_path = dotfile_path

        if environment in dotfile_path:
            target_path = dotfile_path.replace(f"-{environment}", "")

        if target_path.startswith("config/"):
            target_path = config_home / target_path.removeprefix("config/")
        elif "/" not in target_path:
            target_path = home / f".{target_path}"
        else:
            continue

        create_symlink(source_path, target_path, args.force)

    print("Done.")


if __name__ == "__main__":
    main()
