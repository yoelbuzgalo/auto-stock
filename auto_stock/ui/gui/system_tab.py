from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class SystemTab(ttk.Frame):
    def __init__(self, master: tk.Misc, *, services, set_status) -> None:
        super().__init__(master, style="App.TFrame", padding=16)
        self.services = services
        self.set_status = set_status

        self.columnconfigure(0, weight=1)

        self.values = {
            "provider": tk.StringVar(value="-"),
            "provider_detail": tk.StringVar(value="-"),
            "broker": tk.StringVar(value="-"),
            "broker_detail": tk.StringVar(value="-"),
            "notifications": tk.StringVar(value="-"),
            "state_file": tk.StringVar(value="-"),
            "log_file": tk.StringVar(value="-"),
            "watchlist": tk.StringVar(value="0"),
            "orders": tk.StringVar(value="0"),
        }

        self._build_summary()
        self.refresh()

    def refresh(self) -> None:
        status = self.services.health.get_status()
        self.values["provider"].set(
            f"{status.provider.provider_name} ({'available' if status.provider.available else 'attention'})"
        )
        self.values["provider_detail"].set(status.provider.detail)
        self.values["broker"].set(f"{status.broker.broker_name} ({'available' if status.broker.available else 'attention'})")
        self.values["broker_detail"].set(status.broker.detail)
        notifications = []
        for channel in status.notifications:
            readiness = "ready" if channel.configured else "setup needed"
            notifications.append(f"{channel.name} [{channel.kind.value}] {readiness}: {channel.detail}")
        self.values["notifications"].set("\n".join(notifications) if notifications else "No notification channels.")
        self.values["state_file"].set(str(status.storage_path))
        self.values["log_file"].set(str(status.log_file))
        self.values["watchlist"].set(str(status.watchlist_count))
        self.values["orders"].set(str(status.planned_order_count))
        self.set_status("System status refreshed.")

    def _build_summary(self) -> None:
        frame = ttk.LabelFrame(self, text="System Health", style="Card.TLabelframe", padding=14)
        frame.grid(row=0, column=0, sticky="ew")
        frame.columnconfigure(1, weight=1)

        row = 0
        for label, key in (
            ("Provider", "provider"),
            ("Provider Detail", "provider_detail"),
            ("Broker", "broker"),
            ("Broker Detail", "broker_detail"),
            ("Notifications", "notifications"),
            ("State File", "state_file"),
            ("Log File", "log_file"),
            ("Watchlist Items", "watchlist"),
            ("Planned Orders", "orders"),
        ):
            ttk.Label(frame, text=label, style="Body.TLabel").grid(row=row, column=0, sticky="nw", pady=4)
            ttk.Label(frame, textvariable=self.values[key], style="Value.TLabel", wraplength=760).grid(
                row=row, column=1, sticky="w", pady=4, padx=(12, 0)
            )
            row += 1

        ttk.Button(frame, text="Refresh Status", style="Accent.TButton", command=self.refresh).grid(
            row=row, column=0, columnspan=2, sticky="e", pady=(12, 0)
        )
