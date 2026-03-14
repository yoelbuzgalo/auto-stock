"""Auto Stock application package."""

from auto_stock.app import main
from auto_stock.bootstrap import AppServices, build_app_services

__all__ = ["AppServices", "build_app_services", "main"]
