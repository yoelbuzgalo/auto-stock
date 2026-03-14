from __future__ import annotations

import tkinter as tk
from tkinter import ttk

PALETTE = {
    "background": "#F4EFE7",
    "surface": "#FFFFFF",
    "surface_alt": "#F8F5EE",
    "border": "#D8D0C1",
    "text": "#24333D",
    "muted": "#5A6972",
    "accent": "#0F766E",
    "accent_dark": "#0A5F59",
    "accent_soft": "#D7EFEA",
    "danger": "#B64926",
    "success": "#1F6F43",
    "chart_grid": "#E7DFD1",
    "chart_grid_strong": "#D2C7B6",
    "bull": "#16724E",
    "bear": "#B94B3C",
    "chart_line": "#125E73",
    "indicator_fast": "#2A6FDB",
    "indicator_mid": "#D9485F",
    "indicator_slow": "#D97706",
    "indicator_rsi": "#7D5A2F",
    "indicator_zone_high": "#F7E3DB",
    "indicator_zone_low": "#E3F0E7",
    "volume": "#A9C8C4",
}


def configure_theme(root: tk.Tk) -> ttk.Style:
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    root.configure(background=PALETTE["background"])
    root.option_add("*Font", "{Segoe UI} 10")

    style.configure("App.TFrame", background=PALETTE["background"])
    style.configure("Surface.TFrame", background=PALETTE["surface"])
    style.configure("AltSurface.TFrame", background=PALETTE["surface_alt"])
    style.configure("Header.TLabel", background=PALETTE["background"], foreground=PALETTE["text"], font=("Georgia", 20, "bold"))
    style.configure("Subheader.TLabel", background=PALETTE["background"], foreground=PALETTE["muted"], font=("Segoe UI", 10))
    style.configure("Body.TLabel", background=PALETTE["surface"], foreground=PALETTE["text"])
    style.configure("Muted.TLabel", background=PALETTE["surface"], foreground=PALETTE["muted"])
    style.configure("Status.TLabel", background=PALETTE["background"], foreground=PALETTE["muted"])
    style.configure("Card.TLabelframe", background=PALETTE["surface"], bordercolor=PALETTE["border"], borderwidth=1, relief="solid")
    style.configure("Card.TLabelframe.Label", background=PALETTE["surface"], foreground=PALETTE["text"], font=("Segoe UI Semibold", 10))
    style.configure("CardTitle.TLabel", background=PALETTE["surface"], foreground=PALETTE["text"], font=("Segoe UI Semibold", 11))
    style.configure("Value.TLabel", background=PALETTE["surface"], foreground=PALETTE["text"], font=("Segoe UI Semibold", 12))
    style.configure("Accent.TButton", background=PALETTE["accent"], foreground="#FFFFFF", borderwidth=0, padding=(12, 8))
    style.map(
        "Accent.TButton",
        background=[("active", PALETTE["accent_dark"]), ("pressed", PALETTE["accent_dark"])],
        foreground=[("disabled", "#EEF6F4")],
    )
    style.configure("Treeview", rowheight=24, fieldbackground=PALETTE["surface"], background=PALETTE["surface"], foreground=PALETTE["text"])
    style.configure("Treeview.Heading", background=PALETTE["surface_alt"], foreground=PALETTE["text"], relief="flat")
    style.map("Treeview", background=[("selected", PALETTE["accent_soft"])], foreground=[("selected", PALETTE["text"])])
    style.configure("TNotebook", background=PALETTE["background"], borderwidth=0)
    style.configure("TNotebook.Tab", padding=(14, 8), background=PALETTE["surface_alt"], foreground=PALETTE["muted"])
    style.map(
        "TNotebook.Tab",
        background=[("selected", PALETTE["surface"])],
        foreground=[("selected", PALETTE["text"])],
    )
    return style
