# Copyright (c) 2026 Nathan (https://github.com/nathanchankp)
# Licensed under the Demonstration Software License — NOT for production use.
# See LICENSE for full terms.

"""Entry point for the File Automation Bot."""

import logging
import signal
import sys
import time
from pathlib import Path

import yaml
from rich.console import Console
from rich.panel import Panel

from automation.watcher import create_observer

console = Console()

DEMO_BANNER = """
================================================================
  FILE AUTOMATION BOT - DEMONSTRATION PROJECT
================================================================
  This is a portfolio demo, NOT production-ready software.

  Watch dir:  ./watch_dir
  Drop a CSV, JSON, or TXT file into watch_dir/ to see it
  processed automatically.

  Sample files are in: sample_files/
  Copy them into watch_dir/ to test.

  This project is for demonstration purposes only.
  Do NOT use in production environments.
================================================================
"""


def load_config(config_path: str = "config.yaml") -> dict:
    """Load YAML configuration."""
    config_path = Path(config_path)
    if not config_path.exists():
        console.print(f"[red]Config file not found: {config_path}[/red]")
        sys.exit(1)
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    config = load_config()

    console.print(Panel.fit(
        "[bold yellow]DEMO PROJECT[/bold yellow] — "
        "This is a demonstration, NOT production software.\n"
        "[dim]See sample_files/ for test files to drop into watch_dir/[/dim]\n",
        border_style="yellow",
    ))
    print(DEMO_BANNER)

    console.print(Panel.fit(
        "[bold green]File Automation Bot[/bold green]\n"
        f"Watching: {config['watch_dir']}\n"
        f"Webhook:  {config.get('webhook_url', '') or 'disabled'}\n"
        "\n[dim]Press Ctrl+C to stop[/dim]",
        border_style="green",
    ))

    observer = create_observer(
        watch_dir=config["watch_dir"],
        processed_dir=config["processed_dir"],
        errors_dir=config["errors_dir"],
        webhook_url=config.get("webhook_url", ""),
    )

    observer.start()

    def stop(signum, frame):
        console.print("\n[yellow]Stopping...[/yellow]")
        observer.stop()

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)

    try:
        while observer.is_alive():
            observer.join(1)
    except KeyboardInterrupt:
        stop(None, None)

    observer.join()
    console.print("[green]Stopped. Goodbye![/green]")


if __name__ == "__main__":
    main()
