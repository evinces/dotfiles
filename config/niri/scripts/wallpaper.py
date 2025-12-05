#!/usr/bin/env python3
"""
wallpaper.py - A wallpaper & color theme management script

This script manages wallpapers and system-wide color themes for a Wayland environment
(specifically tailored for Niri, but components like swaybg are generic).

Features:
- Sets wallpapers using 'swaybg'.
- Generates color schemes using 'wallust'.
- Reloads configuration for 'waybar', 'mako', and 'niri'.
- Generates cached image variants (blurred, square) using ImageMagick.
- Supports automatic wallpaper cycling.
- Manages a wallpaper repository (clone/pull).
"""

import os
import sys
import shutil
import subprocess
import argparse
import random
import time
import signal
import threading
from pathlib import Path


# --- Configuration ---


HOME = Path.home()
WALLPAPER_DIR = HOME / "Pictures/wallpaper"
XDG_CACHE = Path(os.environ.get("XDG_CACHE_HOME", HOME / ".cache"))
CACHE_DIR = XDG_CACHE / "wallpaper"
GENERATED_DIR = CACHE_DIR / "generated"
SCRIPT_NAME = Path(sys.argv[0]).name
PID_FILE = CACHE_DIR / "automation_pid"


# --- Styling ---


class Fmt:
    """ANSI escape codes for terminal output styling."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    PURPLE = "\033[35m"
    CYAN = "\033[36m"
    PROP = "\033[3;33m"  # Italic Yellow for properties/highlights


def log_info(msg):
    """Prints a formatted info message to stdout."""
    print(f"[{Fmt.DIM}{SCRIPT_NAME}{Fmt.RESET}|{Fmt.BLUE}INFO{Fmt.RESET}] {msg}")


def log_error(msg):
    """Prints a formatted error message to stderr."""
    print(
        f"[{Fmt.DIM}{SCRIPT_NAME}{Fmt.RESET}|{Fmt.RED}ERROR{Fmt.RESET}] {msg}",
        file=sys.stderr,
    )


def notify(summary, body=""):
    """Sends a system notification using notify-send if available."""
    if shutil.which("notify-send"):
        subprocess.run(["notify-send", summary, body])


# --- Helpers ---


def run_cmd(cmd, background=False, quiet=False):
    """
    Executes shell commands with optional logging and background execution.

    Args:
        cmd (list): The command and arguments as a list of strings.
        background (bool): If True, runs the command as a background process (Popen).
        quiet (bool): If True, suppresses stdout/stderr and logging.

    Returns:
        bool or subprocess.Popen: True on success, False on failure, or Popen object if background=True.
    """
    cmd_str = " ".join(str(x) for x in cmd)
    if not quiet:
        log_info(f"Running: {Fmt.PROP}{cmd_str}{Fmt.RESET}")
    if background:
        return subprocess.Popen(
            cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL if quiet else None)
        return True
    except subprocess.CalledProcessError:
        log_error(f"Command failed: {cmd_str}")
        return False
    except FileNotFoundError:
        log_error(f"Application not found: {cmd[0]}")
        return False


def get_current_wallpaper():
    """
    Retrieves the path of the currently set wallpaper from the cache file.
    Falls back to a default path if the cache does not exist.
    """
    current_file = CACHE_DIR / "current_wallpaper"
    if current_file.exists():
        return current_file.read_text().strip()
    return str(WALLPAPER_DIR / "anime/a_tree_trunk_with_a_branch.png")


# --- Core Logic ---


def launch_swaybg(wallpaper_path):
    """
    Sets the wallpaper using 'swaybg'. Kills existing instances first.
    """
    if not shutil.which("swaybg"):
        log_error(f"application not found: {Fmt.PROP}swaybg{Fmt.RESET}")
        return False
    log_info(f"Killing any running instances of {Fmt.PROP}swaybg{Fmt.RESET}")
    subprocess.run(["pkill", "swaybg"], stderr=subprocess.DEVNULL)
    log_info(
        f"Running command: {Fmt.PROP}swaybg -m fill -i {wallpaper_path}{Fmt.RESET}"
    )
    subprocess.Popen(["swaybg", "-m", "fill", "-i", str(wallpaper_path)])
    log_info("Wallpaper set!")
    return True


def update_themes(wallpaper_path):
    """
    Updates system themes based on the wallpaper colors.

    Triggers:
    1. Wallust (generates color schemes)
    2. Waybar (restarts service)
    3. Mako (reloads config)
    4. Niri (generates config)
    """
    if not shutil.which("wallust"):
        log_error(f"application not found: {Fmt.PROP}wallust{Fmt.RESET}")
        return

    log_info(
        f"Generating wallust color scheme: {Fmt.PROP}wallust run {wallpaper_path}{Fmt.RESET}"
    )
    if not run_cmd(["wallust", "run", str(wallpaper_path)]):
        log_error("wallust failed, aborting...")
        return

    log_info(f"Reloading {Fmt.PROP}waybar{Fmt.RESET}...")
    run_cmd(["systemctl", "--user", "restart", "waybar.service"], quiet=True)
    log_info(f"Restarting {Fmt.PROP}mako{Fmt.RESET}...")
    run_cmd(["makoctl", "reload"], quiet=True)


def transform_wallpaper(wallpaper_path, effect, *magick_args):
    """
    Generates transformed versions of the wallpaper (e.g., blurred, square) using ImageMagick.
    Checks the cache first to avoid redundant processing.

    Args:
        wallpaper_path (str): Path to the source wallpaper.
        effect (str): Name of the effect (used for filenames).
        *magick_args: Variable arguments passed to the 'magick' command.
    """
    wallpaper_path = Path(wallpaper_path)
    generic_file = CACHE_DIR / f"{effect}-wallpaper.png"
    cache_file = GENERATED_DIR / f"{effect}-{wallpaper_path.name}.png"

    if cache_file.exists():
        log_info(f"Found cached {effect} version: {Fmt.PROP}{cache_file}{Fmt.RESET}")
        shutil.copy(cache_file, generic_file)
        return

    log_info(f"Generating new {Fmt.PROP}{effect}{Fmt.RESET} version")
    if not shutil.which("magick"):
        log_error(f"application not found: {Fmt.PROP}imagemagick{Fmt.RESET}")
        return

    if run_cmd(
        ["magick", str(wallpaper_path)] + list(magick_args) + [str(generic_file)]
    ):
        shutil.copy(generic_file, cache_file)


def set_wallpaper(wallpaper_path):
    """
    Orchestrates the wallpaper setting process:
    1. Updates themes (parallel).
    2. Generates square and blurred versions (parallel).
    3. Launches swaybg.
    4. Caches the current wallpaper path.

    Returns:
        bool: True if successful, False otherwise.
    """
    wallpaper_path = Path(wallpaper_path)
    if not wallpaper_path.exists():
        log_error(f"File not found: {Fmt.PROP}{wallpaper_path}{Fmt.RESET}")
        return False

    log_info(f"Setting wallpaper: {Fmt.PROP}{wallpaper_path}{Fmt.RESET}")

    threads = []

    # 1. Theme updates
    t_theme = threading.Thread(target=update_themes, args=(wallpaper_path,))
    threads.append(t_theme)
    t_theme.start()

    # 2. Square transform
    t_square = threading.Thread(
        target=transform_wallpaper,
        args=(
            wallpaper_path,
            "square",
            "-gravity",
            "Center",
            "-extent",
            "1:1",
            "-resize",
            "25%",
        ),
    )
    threads.append(t_square)
    t_square.start()

    # 3. Blur transform
    t_blur = threading.Thread(
        target=transform_wallpaper,
        args=(wallpaper_path, "blurred", "-blur", "50x30", "-resize", "75%"),
    )
    threads.append(t_blur)
    t_blur.start()

    # 4. Launch Swaybg
    if not launch_swaybg(wallpaper_path):
        return False

    # 5. Cache current wallpaper filename
    log_info(f"Caching wallpaper filename: {Fmt.PROP}{wallpaper_path}{Fmt.RESET}")
    (CACHE_DIR / "current_wallpaper").write_text(str(wallpaper_path))

    # Wait for tasks to finish
    for t in threads:
        t.join()

    return True


def shuffle_wallpaper(category=None):
    """
    Picks a random wallpaper from the configured directory (or subdirectory).
    """
    target_dir = WALLPAPER_DIR / category if category else WALLPAPER_DIR

    if not target_dir.exists():
        log_error(f"Category not found: {Fmt.PROP}{category}{Fmt.RESET}")
        return False

    rainbow_random = f"{Fmt.ITALIC}{Fmt.RED}r{Fmt.YELLOW}a{Fmt.GREEN}n{Fmt.CYAN}d{Fmt.BLUE}o{Fmt.PURPLE}m{Fmt.RESET}"
    if category is None:
        log_info(f"Picking a {rainbow_random} wallpaper...")
    else:
        log_info(
            f"Picking {rainbow_random} wallpaper from {Fmt.PROP}{category}{Fmt.RESET}..."
        )

    # Find all jpg/png files recursively
    extensions = {".jpg", ".jpeg", ".png"}
    images = [
        f
        for f in target_dir.rglob("*")
        if f.is_file() and f.suffix.lower() in extensions
    ]

    if not images:
        log_error(f"No images found in {Fmt.PROP}{target_dir}{Fmt.RESET}")
        return False

    chosen = random.choice(images)
    return set_wallpaper(chosen)


# --- Automation ---


def manage_automation(interval, category=None):
    """
    Starts or stops the background wallpaper automation process.

    Args:
        interval (int): Seconds between wallpaper changes. If 0, stops automation.
        category (str, optional): Specific subdirectory to cycle wallpapers from.
    """
    if PID_FILE.exists():
        try:
            old_pid = int(PID_FILE.read_text().strip())
            os.kill(old_pid, signal.SIGTERM)
            log_info(
                f"Existing wallpaper automation stopped {Fmt.PROP}(pid: {old_pid}){Fmt.RESET}"
            )
        except (ProcessLookupError, ValueError):
            log_info("Cleaning abandoned automation file")
        PID_FILE.unlink(missing_ok=True)

    if interval > 0:
        log_info(
            f"Starting new wallpaper automation, refresh rate: {Fmt.PROP}{interval} sec{Fmt.RESET}"
        )

        args = [sys.executable, sys.argv[0], "_loop", str(interval)]
        if category:
            args.append(category)

        proc = subprocess.Popen(
            args,
            start_new_session=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        PID_FILE.write_text(str(proc.pid))
        log_info(
            f"New wallpaper automation started {Fmt.PROP}(pid: {proc.pid}){Fmt.RESET}"
        )
        notify(f"Wallpaper will change every {interval} seconds")
    else:
        notify("Wallpaper automation stopped")


def automation_loop(interval, category=None):
    """
    Hidden loop function called by the subprocess for automation.
    Repeatedly calls shuffle_wallpaper at the specified interval.
    """
    while True:
        if not shuffle_wallpaper(category):
            notify("Automation stopped.", "Error setting wallpaper")
            PID_FILE.unlink(missing_ok=True)
            sys.exit(1)
        time.sleep(interval)


# --- CLI Handling ---


def main():
    """Main CLI entry point."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    WALLPAPER_DIR.mkdir(parents=True, exist_ok=True)

    # Pre-check: If arg 1 is a file, skip argparse and just set it
    if len(sys.argv) > 1:
        potential_file = Path(sys.argv[1])
        if potential_file.is_file():
            set_wallpaper(potential_file)
            run_cmd(["fastfetch", "--logo-recache"])
            sys.exit(0)

    parser = argparse.ArgumentParser(description="Wallpaper Management Script")
    subparsers = parser.add_subparsers(dest="command")

    # Shuffle: Pick a random wallpaper
    p_shuf = subparsers.add_parser("shuffle", aliases=["s", "-s"])
    p_shuf.add_argument("category", nargs="?", help="Category subdirectory")

    # Auto: Cycle wallpapers automatically
    p_auto = subparsers.add_parser("auto", aliases=["a", "-a"])
    p_auto.add_argument("interval", type=int, help="Interval in seconds")
    p_auto.add_argument("category", nargs="?", help="Category subdirectory")

    # Update (Git): Pull or clone the wallpaper repository
    subparsers.add_parser("update", aliases=["u", "-u"])

    # Color/Theme Refresh: Re-apply colors from current wallpaper
    subparsers.add_parser("color", aliases=["c", "-c"])

    # Restore: Just re-launch swaybg with current wallpaper (no theme regen)
    subparsers.add_parser("restore", aliases=["r", "-r"])

    # Cache management
    subparsers.add_parser("clear-cache")
    p_fill = subparsers.add_parser("fill-cache")
    p_fill.add_argument("interval", nargs="?", type=float, default=2.0)

    # Internal Loop (Hidden): Used by the 'auto' command
    p_loop = subparsers.add_parser("_loop")
    p_loop.add_argument("interval", type=int)
    p_loop.add_argument("category", nargs="?")

    args = parser.parse_args()

    if args.command is None:
        # Default: Print current wallpaper path
        print(get_current_wallpaper())

    elif args.command in ["shuffle", "s"]:
        if shuffle_wallpaper(args.category):
            run_cmd(["fastfetch", "--logo-recache"])

    elif args.command in ["auto", "a"]:
        manage_automation(args.interval, args.category)

    elif args.command in ["update", "u"]:
        if (WALLPAPER_DIR / ".git").exists():
            log_info("Pulling wallpaper repo...")
            run_cmd(["git", "-C", str(WALLPAPER_DIR), "pull"])
        else:
            repo = "dharmx/walls"
            log_info(f"Cloning {Fmt.PROP}{repo}{Fmt.RESET}...")
            run_cmd(
                ["git", "clone", f"https://github.com/{repo}.git", str(WALLPAPER_DIR)]
            )

    elif args.command in ["color", "c"]:
        update_themes(get_current_wallpaper())
        run_cmd(["fastfetch", "--logo-recache"])

    elif args.command in ["restore", "r"]:
        launch_swaybg(get_current_wallpaper())

    elif args.command == "clear-cache":
        if CACHE_DIR.exists():
            shutil.rmtree(CACHE_DIR)
            CACHE_DIR.mkdir()
            log_info("Wallpaper cache cleared")

    elif args.command == "fill-cache":
        # Iterate all wallpapers to generate cache (pre-generation)
        exts = {".jpg", ".jpeg", ".png"}
        images = [
            f
            for f in WALLPAPER_DIR.rglob("*")
            if f.is_file() and f.suffix.lower() in exts
        ]
        for img in images:
            os.system("clear")
            if not set_wallpaper(img):
                break
            run_cmd(["fastfetch", "--logo-recache"])
            time.sleep(args.interval)

    elif args.command == "_loop":
        automation_loop(args.interval, args.category)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        sys.exit(0)
