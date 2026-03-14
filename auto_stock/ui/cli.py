from __future__ import annotations

import argparse
from collections.abc import Sequence

from auto_stock.bootstrap import AppServices
from auto_stock.infra.errors import AutoStockError
from auto_stock.ui.runtime import gui_runtime_available, gui_runtime_message


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="auto-stock",
        description="Auto Stock desktop and CLI workspace.",
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("gui", help="Launch the desktop application.")
    subparsers.add_parser("doctor", help="Show provider, broker, and storage status.")

    quote_parser = subparsers.add_parser("quote", help="Fetch the latest quote for a symbol.")
    quote_parser.add_argument("symbol")

    history_parser = subparsers.add_parser("history", help="Fetch recent candles for a symbol.")
    history_parser.add_argument("symbol")
    history_parser.add_argument("--timeframe", default="1Day")
    history_parser.add_argument("--limit", type=int, default=10)

    watchlist_parser = subparsers.add_parser("watchlist", help="Manage the watchlist.")
    watchlist_subparsers = watchlist_parser.add_subparsers(dest="watchlist_command", required=True)
    watchlist_add = watchlist_subparsers.add_parser("add", help="Track a symbol.")
    watchlist_add.add_argument("symbol")
    watchlist_add.add_argument("--target-price", type=float)
    watchlist_add.add_argument("--note", default="")
    watchlist_subparsers.add_parser("list", help="List tracked symbols.")
    watchlist_remove = watchlist_subparsers.add_parser("remove", help="Stop tracking a symbol.")
    watchlist_remove.add_argument("symbol")

    orders_parser = subparsers.add_parser("orders", help="Manage local order plans.")
    orders_subparsers = orders_parser.add_subparsers(dest="orders_command", required=True)
    orders_add = orders_subparsers.add_parser("add", help="Create a local planned order.")
    orders_add.add_argument("symbol")
    orders_add.add_argument("--side", default="BUY", choices=["BUY", "SELL"])
    orders_add.add_argument("--quantity", type=float, default=1.0)
    orders_add.add_argument("--target-price", type=float)
    orders_add.add_argument("--note", default="")
    orders_subparsers.add_parser("list", help="List local planned orders.")
    orders_remove = orders_subparsers.add_parser("remove", help="Remove a planned order.")
    orders_remove.add_argument("order_id")

    broker_parser = subparsers.add_parser("broker", help="Load broker account data.")
    broker_parser.add_argument("--account")

    notify_parser = subparsers.add_parser("notify", help="Inspect or send notifications.")
    notify_subparsers = notify_parser.add_subparsers(dest="notify_command", required=True)
    notify_subparsers.add_parser("status", help="Show notification channel readiness.")
    notify_send = notify_subparsers.add_parser("send", help="Send a test notification.")
    delivery_group = notify_send.add_mutually_exclusive_group(required=True)
    delivery_group.add_argument("--channel", help="Send to a single configured channel name.")
    delivery_group.add_argument("--all", action="store_true", help="Send to every configured channel.")
    notify_send.add_argument("message", help="Message body to deliver.")

    return parser


def run_cli(services: AppServices, argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    try:
        if args.command is None:
            if gui_runtime_available():
                from auto_stock.ui.gui.app import launch_gui

                launch_gui(services)
                return 0

            print(f"GUI unavailable: {gui_runtime_message()}")
            print()
            _run_doctor(services)
            print()
            parser.print_help()
            return 0
        if args.command == "gui":
            if not gui_runtime_available():
                print(f"Error: {gui_runtime_message()}")
                return 1

            from auto_stock.ui.gui.app import launch_gui

            launch_gui(services)
            return 0
        if args.command == "doctor":
            return _run_doctor(services)
        if args.command == "quote":
            return _run_quote(services, args.symbol)
        if args.command == "history":
            return _run_history(services, args.symbol, args.timeframe, args.limit)
        if args.command == "watchlist":
            return _run_watchlist(services, args)
        if args.command == "orders":
            return _run_orders(services, args)
        if args.command == "broker":
            return _run_broker(services, args.account)
        if args.command == "notify":
            return _run_notify(services, args)
    except AutoStockError as exc:
        print(f"Error: {exc}")
        return 1

    parser.print_help()
    return 0


def _run_doctor(services: AppServices) -> int:
    status = services.health.get_status()
    print(f"Provider: {status.provider.provider_name} ({'ok' if status.provider.available else 'issue'})")
    print(f"  {status.provider.detail}")
    print(f"Broker: {status.broker.broker_name} ({'ok' if status.broker.available else 'issue'})")
    print(f"  {status.broker.detail}")
    print("Notifications:")
    for channel in status.notifications:
        configured = "ok" if channel.configured else "setup needed"
        print(f"  {channel.name} ({channel.kind.value}) [{configured}]")
        print(f"    {channel.detail}")
    print(f"State file: {status.storage_path}")
    print(f"Log file: {status.log_file}")
    print(f"Watchlist items: {status.watchlist_count}")
    print(f"Planned orders: {status.planned_order_count}")
    return 0


def _run_quote(services: AppServices, symbol: str) -> int:
    quote = services.market.get_quote(symbol)
    print(f"{quote.symbol}  last={quote.last:.2f}  bid={quote.bid:.2f}  ask={quote.ask:.2f}")
    print(f"source={quote.source} volume={quote.volume} as_of={quote.timestamp.isoformat()}")
    return 0


def _run_history(services: AppServices, symbol: str, timeframe: str, limit: int) -> int:
    candles = services.market.get_history(symbol, timeframe=timeframe)
    for candle in candles[-max(1, limit) :]:
        print(
            f"{candle.timestamp.isoformat()} "
            f"open={candle.open:.2f} high={candle.high:.2f} "
            f"low={candle.low:.2f} close={candle.close:.2f} volume={candle.volume}"
        )
    return 0


def _run_watchlist(services: AppServices, args: argparse.Namespace) -> int:
    if args.watchlist_command == "add":
        item = services.watchlist.add_item(args.symbol, target_price=args.target_price, note=args.note)
        print(f"Tracking {item.symbol}")
        return 0
    if args.watchlist_command == "remove":
        removed = services.watchlist.remove_item(args.symbol)
        print("Removed." if removed else "No matching symbol found.")
        return 0

    items = services.watchlist.list_items()
    if not items:
        print("Watchlist is empty.")
        return 0
    for item in items:
        target = f"{item.target_price:.2f}" if item.target_price is not None else "-"
        note = item.note or "-"
        print(f"{item.symbol:8} target={target:>8} note={note}")
    return 0


def _run_orders(services: AppServices, args: argparse.Namespace) -> int:
    if args.orders_command == "add":
        order = services.order_plans.add_order(
            args.symbol,
            side=args.side,
            quantity=args.quantity,
            target_price=args.target_price,
            note=args.note,
        )
        print(f"Saved order plan {order.order_id} for {order.symbol}")
        return 0
    if args.orders_command == "remove":
        removed = services.order_plans.remove_order(args.order_id)
        print("Removed." if removed else "No matching order plan found.")
        return 0

    orders = services.order_plans.list_orders()
    if not orders:
        print("No planned orders.")
        return 0
    for order in orders:
        target = f"{order.target_price:.2f}" if order.target_price is not None else "-"
        note = order.note or "-"
        print(
            f"{order.order_id:10} {order.symbol:8} {order.side.value:4} "
            f"qty={order.quantity:>6.2f} target={target:>8} note={note}"
        )
    return 0


def _run_broker(services: AppServices, account: str | None) -> int:
    snapshot = services.broker.get_snapshot(account)
    if snapshot.account is None:
        print("No account data returned.")
        return 0
    print(
        f"Account {snapshot.account.account_id} "
        f"cash={snapshot.account.cash_balance:.2f} "
        f"buying_power={snapshot.account.buying_power:.2f} "
        f"equity={snapshot.account.equity:.2f}"
    )
    print(f"Positions: {len(snapshot.positions)}")
    print(f"Orders: {len(snapshot.orders)}")
    return 0


def _run_notify(services: AppServices, args: argparse.Namespace) -> int:
    if args.notify_command == "status":
        for status in services.notifications.list_statuses():
            readiness = "ready" if status.configured else "setup needed"
            print(f"{status.name:16} {status.kind.value:10} {readiness:13} {status.detail}")
        return 0

    if args.all:
        results = services.notifications.send_all(args.message)
        if not results:
            print("No configured notification channels are available.")
            return 1
        for result in results:
            print(f"{result.channel_name}: {result.detail}")
        return 0

    result = services.notifications.send(args.channel, args.message)
    print(f"{result.channel_name}: {result.detail}")
    return 0
