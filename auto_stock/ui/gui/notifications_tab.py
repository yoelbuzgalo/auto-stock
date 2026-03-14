from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from auto_stock.domain.notifications import NotificationDeliveryResult

_ALL_CHANNELS = "All configured"


class NotificationsTab(ttk.Frame):
    def __init__(self, master: tk.Misc, *, services, run_async, set_status) -> None:
        super().__init__(master, style="App.TFrame", padding=16)
        self.services = services
        self.run_async = run_async
        self.set_status = set_status

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.channel_var = tk.StringVar(value=_ALL_CHANNELS)
        self.feedback_var = tk.StringVar(
            value="Connect Discord or Twilio channels, then send test notifications from here."
        )

        self._build_controls()
        self._build_table()
        self.refresh_statuses()

    def refresh_statuses(self) -> None:
        statuses = self.services.notifications.list_statuses()
        self.channel_combo.configure(values=(_ALL_CHANNELS, *self.services.notifications.list_channel_names()))
        for row_id in self.tree.get_children():
            self.tree.delete(row_id)

        configured_count = 0
        for status in statuses:
            ready_label = "Ready" if status.configured else "Setup needed"
            if status.configured:
                configured_count += 1
            self.tree.insert(
                "",
                "end",
                iid=status.name,
                values=(status.name, status.kind.value, ready_label, status.detail),
            )

        if configured_count:
            self.feedback_var.set(f"{configured_count} channel(s) ready. Select one or send to all configured channels.")
        else:
            self.feedback_var.set("No notification channels are configured yet. Add credentials in .env to enable them.")
        self.set_status("Notification status refreshed.")

    def send_test(self) -> None:
        message = self.message_text.get("1.0", "end").strip()
        channel_name = self.channel_var.get().strip() or _ALL_CHANNELS
        self.feedback_var.set("Sending notification...")
        self.set_status("Sending notification...")

        def work() -> tuple[NotificationDeliveryResult, ...]:
            if channel_name == _ALL_CHANNELS:
                return self.services.notifications.send_all(message)
            return (self.services.notifications.send(channel_name, message),)

        self.run_async(work, self._on_send_success, self._on_send_error)

    def _on_send_success(self, results: tuple[NotificationDeliveryResult, ...]) -> None:
        if not results:
            self.feedback_var.set("No configured channels were available for sending.")
            self.set_status("No configured notification channels available.")
            return

        summary = ", ".join(result.channel_name for result in results)
        self.feedback_var.set(f"Sent notification through {summary}.")
        self.set_status("Notification sent.")
        self.refresh_statuses()

    def _on_send_error(self, exc: Exception) -> None:
        self.feedback_var.set(str(exc))
        self.set_status("Notification delivery failed.")

    def _build_controls(self) -> None:
        frame = ttk.LabelFrame(self, text="Notification Delivery", style="Card.TLabelframe", padding=14)
        frame.grid(row=0, column=0, sticky="ew")
        frame.columnconfigure(3, weight=1)

        ttk.Label(frame, text="Channel", style="Body.TLabel").grid(row=0, column=0, sticky="w")
        self.channel_combo = ttk.Combobox(frame, textvariable=self.channel_var, state="readonly", width=20)
        self.channel_combo.grid(row=0, column=1, sticky="w", padx=(8, 12))

        ttk.Label(frame, text="Test Message", style="Body.TLabel").grid(row=0, column=2, sticky="nw")
        self.message_text = tk.Text(
            frame,
            height=4,
            width=52,
            background="#FFFFFF",
            foreground="#24333D",
            borderwidth=1,
            highlightthickness=0,
            relief="solid",
            wrap="word",
        )
        self.message_text.grid(row=0, column=3, sticky="ew", padx=(8, 12))
        self.message_text.insert("1.0", "Auto Stock desktop test notification.")

        actions = ttk.Frame(frame, style="Surface.TFrame")
        actions.grid(row=0, column=4, sticky="ne")
        ttk.Button(actions, text="Refresh Channels", command=self.refresh_statuses).grid(row=0, column=0, sticky="ew")
        ttk.Button(actions, text="Send Test", style="Accent.TButton", command=self.send_test).grid(
            row=1,
            column=0,
            sticky="ew",
            pady=(8, 0),
        )

        ttk.Label(frame, textvariable=self.feedback_var, style="Muted.TLabel").grid(
            row=1,
            column=0,
            columnspan=5,
            sticky="w",
            pady=(10, 0),
        )

    def _build_table(self) -> None:
        frame = ttk.LabelFrame(self, text="Channel Health", style="Card.TLabelframe", padding=12)
        frame.grid(row=1, column=0, sticky="nsew", pady=(14, 0))
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        columns = ("name", "kind", "ready", "detail")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", selectmode="browse")
        headings = {
            "name": "Channel",
            "kind": "Type",
            "ready": "Status",
            "detail": "Detail",
        }
        widths = {
            "name": 150,
            "kind": 120,
            "ready": 120,
            "detail": 520,
        }
        for column in columns:
            self.tree.heading(column, text=headings[column])
            self.tree.column(column, width=widths[column], anchor="w")
        self.tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)
