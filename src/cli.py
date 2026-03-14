from __future__ import annotations

from collections.abc import Sequence

from auto_stock.bootstrap import build_app_services
from auto_stock.ui.cli import run_cli


def run_cli_app(_persistence=None, argv: Sequence[str] | None = None) -> int:
    return run_cli(build_app_services(), argv)
