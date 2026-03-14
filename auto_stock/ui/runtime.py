from __future__ import annotations

import importlib


_GUI_UNAVAILABLE_MESSAGE = (
    "Tkinter is not available in this Python build. "
    "Use the CLI commands or install Python with Tk support for the desktop app."
)


def gui_runtime_available() -> bool:
    try:
        importlib.import_module("tkinter")
    except ModuleNotFoundError:
        return False
    return True


def gui_runtime_message() -> str:
    return _GUI_UNAVAILABLE_MESSAGE
