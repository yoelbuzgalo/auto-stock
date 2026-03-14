from __future__ import annotations

from collections.abc import Sequence

from auto_stock.bootstrap import build_app_services
from auto_stock.ui.runtime import gui_runtime_available, gui_runtime_message
from auto_stock.ui.cli import run_cli


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point for the command-line interface (CLI).
    
    Bootstraps the application services and passes control to the CLI runner.
    
    Args:
        argv: Optional sequence of string arguments to parse. Defaults to sys.argv.
        
    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    services = build_app_services()
    return run_cli(services, argv)


def launch_gui_entrypoint() -> int:
    """Entry point for the graphical user interface (GUI)."""
    if not gui_runtime_available():
        print(f"Error: {gui_runtime_message()}")
        return 1

    from auto_stock.ui.gui.app import launch_gui

    services = build_app_services()
    launch_gui(services)
    return 0
