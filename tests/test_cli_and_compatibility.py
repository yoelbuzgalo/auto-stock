from __future__ import annotations

import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from auto_stock.bootstrap import build_app_services
from auto_stock.infra.config import AppConfig
from auto_stock.ui.cli import run_cli
from modules.broker.account_models import Account, Position
from modules.data_sources.market_models import Quote
from modules.services.persistence import JsonFilePersistence
from tests.helpers import workspace_temp_dir


class CliAndCompatibilityTests(unittest.TestCase):
    def test_doctor_command_runs(self) -> None:
        with workspace_temp_dir() as temp_dir:
            config = AppConfig.from_env(
                env={
                    "AUTO_STOCK_STORAGE_DIR": str(temp_dir),
                    "AUTO_STOCK_STATE_FILE": str(temp_dir / "state.json"),
                    "AUTO_STOCK_LOG_FILE": str(temp_dir / "auto_stock.log"),
                }
            )
            services = build_app_services(config)
            output = io.StringIO()
            with redirect_stdout(output):
                exit_code = run_cli(services, ["doctor"])
            self.assertEqual(exit_code, 0)
            self.assertIn("Provider:", output.getvalue())

    def test_no_args_falls_back_to_cli_when_gui_runtime_missing(self) -> None:
        with workspace_temp_dir() as temp_dir:
            config = AppConfig.from_env(
                env={
                    "AUTO_STOCK_STORAGE_DIR": str(temp_dir),
                    "AUTO_STOCK_STATE_FILE": str(temp_dir / "state.json"),
                    "AUTO_STOCK_LOG_FILE": str(temp_dir / "auto_stock.log"),
                }
            )
            services = build_app_services(config)
            output = io.StringIO()
            with patch("auto_stock.ui.cli.gui_runtime_available", return_value=False):
                with redirect_stdout(output):
                    exit_code = run_cli(services, [])
            self.assertEqual(exit_code, 0)
            self.assertIn("GUI unavailable:", output.getvalue())
            self.assertIn("doctor", output.getvalue())

    def test_gui_command_errors_when_gui_runtime_missing(self) -> None:
        with workspace_temp_dir() as temp_dir:
            config = AppConfig.from_env(
                env={
                    "AUTO_STOCK_STORAGE_DIR": str(temp_dir),
                    "AUTO_STOCK_STATE_FILE": str(temp_dir / "state.json"),
                    "AUTO_STOCK_LOG_FILE": str(temp_dir / "auto_stock.log"),
                }
            )
            services = build_app_services(config)
            output = io.StringIO()
            with patch("auto_stock.ui.cli.gui_runtime_available", return_value=False):
                with redirect_stdout(output):
                    exit_code = run_cli(services, ["gui"])
            self.assertEqual(exit_code, 1)
            self.assertIn("Tkinter is not available", output.getvalue())

    def test_legacy_persistence_adapter_works(self) -> None:
        with workspace_temp_dir() as temp_dir:
            persistence = JsonFilePersistence(str(temp_dir / "legacy.json"))
            persistence.add_item(("AAPL", 100.0))
            self.assertEqual(persistence.load_items(), [("AAPL", 100.0)])

    def test_legacy_imports_resolve_to_new_models(self) -> None:
        self.assertEqual(Account.__name__, "Account")
        self.assertEqual(Position.__name__, "Position")
        self.assertEqual(Quote.__name__, "Quote")


if __name__ == "__main__":
    unittest.main()
