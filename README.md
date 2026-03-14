# Auto Stock

Auto Stock is a lightweight stock desktop application and CLI with explicit provider, broker, persistence, and service boundaries. It works out of the box with a demo market-data provider, then scales up to Polygon, Alpaca, or Schwab through environment configuration.

## Quick Start

Use Python 3.11+.

Recommended setup from a fresh clone:

```bash
python manage.py init
```

That creates `.venv`, installs the project in editable mode, creates `.env` from `.env.example` if needed, and runs a self-check.
If the current Python build cannot create a working virtual environment, the script falls back to the active interpreter and still leaves the repo runnable from the project root.

Install in editable mode:

```bash
python -m pip install -e .
```

Copy the sample environment file if you want to override defaults:

```bash
cp .env.example .env
```

Run a quick health check:

```bash
python tools/self_check.py
python manage.py self-check
```

## Run Paths

Direct from the repo:

```bash
python manage.py run
python manage.py doctor
python manage.py test
python run.py doctor
python run.py quote AAPL
python run.py history MSFT --timeframe 1Day --limit 5
python run.py watchlist add NVDA --target-price 850
python run.py orders add AAPL --quantity 2 --target-price 180
python run.py notify status
python run.py notify send --channel discord "Auto Stock test message"
python run.py notify send --all "Portfolio alert test"
```

Installed console scripts:

```bash
auto-stock doctor
auto-stock quote AAPL
auto-stock-gui
```

Module entrypoints:

```bash
python -m auto_stock doctor
python -m auto_stock gui
```

If you run `auto-stock` or `python run.py` with no arguments:

- it opens the GUI when Tkinter is available
- it falls back to a CLI doctor/help view when Tkinter is missing

## Desktop Workflows

The desktop GUI now supports:

- market lookup with switchable `Line`, `Candlesticks`, `Indicators`, and `All` chart modes
- true candlesticks with wicks, plus SMA 10, SMA 20, and volume overlays
- watchlist tracking and local order plans
- broker visibility when Schwab credentials are configured
- notification channel health plus test sends for Discord, Twilio SMS, and Twilio WhatsApp

Use the `Chart View` selector in the Market tab to swap instantly between views without refetching history data.

## Notification Setup

Auto Stock keeps notifications dependency-free by using standard-library HTTP calls:

- Discord: set `DISCORD_WEBHOOK_URL`
- Twilio SMS: set `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_SMS_FROM`, and `TWILIO_SMS_TO`
- Twilio WhatsApp: set `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_WHATSAPP_FROM`, and `TWILIO_WHATSAPP_TO`

Then use either:

```bash
python run.py notify status
python run.py notify send --channel discord "Auto Stock connectivity test"
python run.py notify send --all "Auto Stock connectivity test"
```

Or open the `Notifications` tab in the GUI to review channel health and send a test message.

## GUI Note

The desktop UI uses Tkinter to keep dependencies minimal. If your Python build does not include Tk support, the CLI still works and the GUI command will explain the issue clearly. Tkinter was chosen here because it ships with most standard Python installs, is easy to package with PyInstaller, and keeps the project deployable without pulling in a larger GUI framework.

## Architecture

- `auto_stock/domain`: market, broker, and watchlist models
- `auto_stock/providers`: market data contracts, concrete providers, and cache/retry wrappers
- `auto_stock/broker`: broker contracts and adapters
- `auto_stock/persistence`: resilient JSON state storage
- `auto_stock/services`: focused orchestration layer
- `auto_stock/ui`: CLI and Tkinter GUI
- `auto_stock/notifications`: vendor-specific notification adapters with explicit channel interfaces
- `auto_stock/infra`: config, logging, validation, HTTP, and shared errors
- `modules/*`: compatibility wrappers for the original repository paths

## Testing

```bash
python -m unittest discover -s tests -v
```
