# File Automation Bot

> **DEMO PROJECT** — This is a portfolio demonstration, NOT production-ready software.
> See [LICENSE](LICENSE) for full disclaimer.

A file automation tool that watches a directory, processes incoming files by type, generates summary reports, and sends webhook notifications.

## Features

- **Watch a directory** for new files (using watchdog)
- **Process by type**: CSV, JSON, TXT files each get specialized handling
- **Auto-organize**: Move processed files to `processed/`, invalid files to `errors/`
- **Summary reports**: Generate daily summary of all processed files
- **Webhook notifications**: Send alerts to any HTTP endpoint (Slack, Teams, custom)
- **Configurable** via simple YAML config
- **Sample files** included for immediate testing
- **Unit tests** with pytest

## Quick Start

```bash
# Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the bot (watches ./watch_dir by default)
python run_bot.py
```

Drop a CSV, JSON, or TXT file into the `watch_dir/` folder and watch it get processed automatically.

## Demo Files

Sample files are provided in `sample_files/` — copy them into `watch_dir/` to test:

| File | Type | Description |
|------|------|-------------|
| `sample_orders.csv` | CSV | 5 rows of order data |
| `sample_config.json` | JSON | A report config with nested objects |
| `sample_notes.txt` | TXT | A weekly status report |

```bash
# Copy sample files to watch_dir to see them processed
cp sample_files/* watch_dir/
```

## How It Works

1. Bot watches `watch_dir/` for new files
2. Detects file type by extension:
   - **CSV**: Counts rows, extracts column names, calculates basic stats
   - **JSON**: Validates structure, counts keys, extracts top-level fields
   - **TXT**: Counts words, lines, characters
3. Moves processed files to `watch_dir/processed/`
4. Invalid/unrecognized files go to `watch_dir/errors/`
5. Sends a webhook notification (if configured) with the processing result
6. Appends a summary entry to `watch_dir/summary.log`

## Configuration

Edit `config.yaml`:

```yaml
watch_dir: ./watch_dir
processed_dir: ./watch_dir/processed
errors_dir: ./watch_dir/errors
webhook_url: ""  # Leave empty to skip notifications
```

## Running Tests

```bash
pytest -v
```

## Tech Stack

- Python 3.10+
- watchdog (filesystem monitoring)
- requests (webhook notifications)
- PyYAML (config)
- rich (CLI output)
- pytest

## Disclaimer

This software is provided for **demonstration and portfolio purposes only**.
It is NOT designed, tested, or intended for production use. Using this software
in a production environment is strictly prohibited and at the user's sole risk.
See [LICENSE](LICENSE) for full terms.

## License

See [LICENSE](LICENSE) — Demonstration Software License.

## Author

Nathan — Python Developer | Backend · Automation · Data  
GitHub: [@nathanchankp](https://github.com/nathanchankp)
