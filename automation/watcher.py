# Copyright (c) 2026 Nathan (https://github.com/nathanchankp)
# Licensed under the Demonstration Software License — NOT for production use.
# See LICENSE for full terms.

"""Filesystem watcher: monitor a directory and process new files."""

import logging
import shutil
from datetime import datetime, timezone
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from .processor import process_file
from .notifier import send_notification

logger = logging.getLogger(__name__)


class FileHandler(FileSystemEventHandler):
    """Handles file creation events: processes, moves, and notifies."""

    def __init__(self, watch_dir: Path, processed_dir: Path, errors_dir: Path, webhook_url: str = ""):
        self.watch_dir = watch_dir
        self.processed_dir = processed_dir
        self.errors_dir = errors_dir
        self.webhook_url = webhook_url
        self.summary_log = watch_dir / "summary.log"

    def on_created(self, event):
        if event.is_directory:
            return
        file_path = Path(event.src_path)

        # Skip the summary log itself
        if file_path.name == "summary.log":
            return

        # Wait briefly to ensure file is fully written
        import time
        time.sleep(0.5)

        if not file_path.exists():
            return

        logger.info("New file detected: %s", file_path.name)
        result = process_file(file_path)

        # Move file to appropriate directory
        if "error" in result:
            self._move_file(file_path, self.errors_dir)
        else:
            self._move_file(file_path, self.processed_dir)

        # Log summary
        self._log_summary(result)

        # Send notification
        send_notification(self.webhook_url, result)

    def _move_file(self, file_path: Path, target_dir: Path):
        """Move a file to the target directory."""
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / file_path.name
        # Handle name collisions
        if target.exists():
            stem = file_path.stem
            suffix = file_path.suffix
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            target = target_dir / f"{stem}_{timestamp}{suffix}"
        shutil.move(str(file_path), str(target))
        logger.info("Moved %s -> %s", file_path.name, target)

    def _log_summary(self, result: dict):
        """Append a summary line to the log file."""
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        status = "ERROR" if "error" in result else "OK"
        line = f"[{timestamp}] {status} | {result.get('file', 'unknown')} | {result.get('type', 'unknown')}\n"
        with open(self.summary_log, "a", encoding="utf-8") as f:
            f.write(line)


def create_observer(watch_dir: str, processed_dir: str, errors_dir: str, webhook_url: str = "") -> Observer:
    """Create and configure a watchdog Observer.

    Args:
        watch_dir: Directory to watch for new files.
        processed_dir: Directory to move successfully processed files.
        errors_dir: Directory to move files that failed processing.
        webhook_url: Optional webhook URL for notifications.

    Returns:
        Configured Observer instance (not yet started).
    """
    watch_path = Path(watch_dir).resolve()
    processed_path = Path(processed_dir).resolve()
    errors_path = Path(errors_dir).resolve()

    for p in [watch_path, processed_path, errors_path]:
        p.mkdir(parents=True, exist_ok=True)

    handler = FileHandler(watch_path, processed_path, errors_path, webhook_url)
    observer = Observer()
    observer.schedule(handler, str(watch_path), recursive=False)
    return observer
