from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from auto_stock.bootstrap import build_app_services
from auto_stock.ui.runtime import gui_runtime_available, gui_runtime_message


def main() -> int:
    services = build_app_services()
    status = services.health.get_status()
    quote = services.market.get_quote("AAPL")

    print("Auto Stock self-check")
    print()
    print(f"Provider: {status.provider.provider_name} ({'ok' if status.provider.available else 'issue'})")
    print(f"Broker: {status.broker.broker_name} ({'ok' if status.broker.available else 'issue'})")
    configured_notifications = sum(1 for channel in status.notifications if channel.configured)
    print(f"Notifications: {configured_notifications}/{len(status.notifications)} configured")
    print(f"State file: {status.storage_path}")
    print(f"GUI runtime: {'ok' if gui_runtime_available() else gui_runtime_message()}")
    print(f"Sample quote: {quote.symbol} last={quote.last:.2f} source={quote.source}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
