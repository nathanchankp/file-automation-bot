# Copyright (c) 2026 Nathan (https://github.com/nathanchankp)
# Licensed under the Demonstration Software License — NOT for production use.
# See LICENSE for full terms.

"""Webhook notifier: send processing results to an HTTP endpoint."""

import logging

import requests

logger = logging.getLogger(__name__)


def send_notification(webhook_url: str, payload: dict) -> bool:
    """Send a POST request to a webhook URL with the processing result.

    Args:
        webhook_url: The HTTP endpoint to notify. Empty string skips notification.
        payload: Dict with processing results to send as JSON.

    Returns:
        True if notification was sent successfully (or skipped), False on failure.
    """
    if not webhook_url:
        logger.debug("No webhook URL configured, skipping notification")
        return True

    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
        logger.info("Notification sent for file: %s", payload.get("file", "unknown"))
        return True
    except requests.RequestException as e:
        logger.error("Webhook notification failed: %s", e)
        return False
