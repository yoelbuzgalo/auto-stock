from __future__ import annotations

from dataclasses import dataclass
import tkinter as tk
from tkinter import ttk

from auto_stock.domain.market import Candle
from auto_stock.services.indicators import StandardIndicatorSet, build_standard_indicators
from auto_stock.ui.gui.theme import PALETTE

CHART_MODES = ("Default", "Candlesticks", "Indicators", "All")
CHART_MODE_DESCRIPTIONS = {
    "Default": "Smoothed close line for quick trend reading.",
    "Candlesticks": "True OHLC candles with wicks and directional bodies.",
    "Indicators": "Close trend with SMA 20, EMA 12, EMA 26, and RSI 14.",
    "All": "Close line, full candles, SMA 20, EMA 12, EMA 26, RSI 14, and volume together.",
}
DEFAULT_CHART_MODE = "Default"


@dataclass(frozen=True, slots=True)
class PanelBounds:
    left: int
    top: int
    width: int
    height: int

    @property
    def right(self) -> int:
        return self.left + self.width

    @property
    def bottom(self) -> int:
        return self.top + self.height


class HistoryChart(ttk.Frame):
    def __init__(self, master: tk.Misc, *, initial_mode: str = DEFAULT_CHART_MODE) -> None:
        super().__init__(master, style="Surface.TFrame")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self._series: list[Candle] = []
        self._state_message = "Load market history to see the chart."
        self._mode = self._normalize_mode(initial_mode)

        self.canvas = tk.Canvas(
            self,
            background=PALETTE["surface"],
            borderwidth=0,
            highlightthickness=0,
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.canvas.bind("<Configure>", self._on_resize)

    def set_loading(self, message: str = "Loading history...") -> None:
        self._series = []
        self._state_message = message
        self._redraw()

    def set_error(self, message: str) -> None:
        self._series = []
        self._state_message = message
        self._redraw()

    def set_series(self, candles: list[Candle]) -> None:
        self._series = candles
        self._redraw()

    def set_mode(self, mode: str) -> None:
        normalized = self._normalize_mode(mode)
        if normalized == self._mode:
            return
        self._mode = normalized
        self._redraw()

    def _on_resize(self, _event: tk.Event[tk.Misc]) -> None:
        self._redraw()

    def _redraw(self) -> None:
        self.canvas.delete("all")
        width = max(self.canvas.winfo_width(), 520)
        height = max(self.canvas.winfo_height(), 320)

        if not self._series:
            self.canvas.create_text(
                width / 2,
                height / 2,
                text=self._state_message,
                fill=PALETTE["muted"],
                font=("Segoe UI", 11),
                width=width - 80,
            )
            return

        mode = self._mode
        show_candles = mode in {"Candlesticks", "All"}
        show_close_line = mode in {"Default", "Indicators", "All"}
        show_indicators = mode in {"Indicators", "All"}
        show_volume = mode == "All"
        show_rsi = mode in {"Indicators", "All"}

        pad_left = 56
        pad_right = 18
        pad_top = 18
        pad_bottom = 34
        available_width = width - pad_left - pad_right
        available_height = height - pad_top - pad_bottom
        panel_gap = 14

        price_panel, volume_panel, rsi_panel = self._build_panel_layout(
            left=pad_left,
            top=pad_top,
            width=available_width,
            height=available_height,
            panel_gap=panel_gap,
            show_volume=show_volume,
            show_rsi=show_rsi,
        )

        indicators = build_standard_indicators(self._series)
        min_price, max_price = self._price_bounds(indicators, include_indicators=show_indicators)
        self._draw_panel_background(price_panel, title=self._mode)
        self._draw_price_grid(price_panel, min_price=min_price, max_price=max_price)

        if show_candles:
            self._draw_candles(price_panel, min_price=min_price, max_price=max_price)
        if show_close_line:
            self._draw_price_line(
                price_panel,
                values=[candle.close for candle in self._series],
                min_value=min_price,
                max_value=max_price,
                color=PALETTE["chart_line"],
                width=3 if mode != "All" else 2,
                dash=(5, 4) if mode == "All" else None,
            )
        if show_indicators:
            self._draw_price_line(
                price_panel,
                values=indicators.sma_20,
                min_value=min_price,
                max_value=max_price,
                color=PALETTE["indicator_slow"],
                width=2,
                dash=(7, 3),
            )
            self._draw_price_line(
                price_panel,
                values=indicators.ema_12,
                min_value=min_price,
                max_value=max_price,
                color=PALETTE["indicator_fast"],
                width=2,
            )
            self._draw_price_line(
                price_panel,
                values=indicators.ema_26,
                min_value=min_price,
                max_value=max_price,
                color=PALETTE["indicator_mid"],
                width=2,
            )

        if volume_panel is not None:
            self._draw_panel_background(volume_panel, title="Volume", fill=PALETTE["surface_alt"])
            self._draw_volume_bars(volume_panel)

        if rsi_panel is not None:
            self._draw_panel_background(rsi_panel, title="RSI 14", fill=PALETTE["surface_alt"])
            self._draw_rsi_panel(rsi_panel, indicators.rsi_14)

        self._draw_mode_summary(width, pad_top)
        self._draw_legend(
            x=price_panel.right - 188,
            y=price_panel.top + 8,
            show_candles=show_candles,
            show_close_line=show_close_line,
            show_indicators=show_indicators,
            show_rsi=show_rsi,
            show_volume=show_volume,
        )
        self._draw_time_labels(width=width, pad_left=pad_left, pad_right=pad_right, baseline=height - 10)

    def _build_panel_layout(
        self,
        *,
        left: int,
        top: int,
        width: int,
        height: int,
        panel_gap: int,
        show_volume: bool,
        show_rsi: bool,
    ) -> tuple[PanelBounds, PanelBounds | None, PanelBounds | None]:
        if show_volume and show_rsi:
            price_height = int(height * 0.58)
            volume_height = int(height * 0.16)
            rsi_height = height - price_height - volume_height - (panel_gap * 2)
            price_panel = PanelBounds(left=left, top=top, width=width, height=price_height)
            volume_panel = PanelBounds(left=left, top=price_panel.bottom + panel_gap, width=width, height=volume_height)
            rsi_panel = PanelBounds(left=left, top=volume_panel.bottom + panel_gap, width=width, height=rsi_height)
            return price_panel, volume_panel, rsi_panel

        if show_rsi:
            price_height = int(height * 0.72)
            rsi_height = height - price_height - panel_gap
            price_panel = PanelBounds(left=left, top=top, width=width, height=price_height)
            rsi_panel = PanelBounds(left=left, top=price_panel.bottom + panel_gap, width=width, height=rsi_height)
            return price_panel, None, rsi_panel

        price_panel = PanelBounds(left=left, top=top, width=width, height=height)
        return price_panel, None, None

    def _draw_panel_background(self, panel: PanelBounds, *, title: str, fill: str | None = None) -> None:
        self.canvas.create_rectangle(
            panel.left,
            panel.top,
            panel.right,
            panel.bottom,
            outline=PALETTE["border"],
            fill=fill or PALETTE["surface"],
        )
        self.canvas.create_text(
            panel.left + 10,
            panel.top + 10,
            anchor="w",
            text=title,
            fill=PALETTE["muted"],
            font=("Segoe UI Semibold", 9),
        )

    def _draw_price_grid(self, panel: PanelBounds, *, min_price: float, max_price: float) -> None:
        chart_top = panel.top + 26
        chart_height = max(60, panel.height - 36)
        for step in range(5):
            y = chart_top + (chart_height * step / 4)
            price = max_price - ((max_price - min_price) * step / 4)
            self.canvas.create_line(panel.left, y, panel.right, y, fill=PALETTE["chart_grid"])
            self.canvas.create_text(
                8,
                y,
                anchor="w",
                text=f"{price:.2f}",
                fill=PALETTE["muted"],
                font=("Segoe UI", 8),
            )

    def _draw_candles(self, panel: PanelBounds, *, min_price: float, max_price: float) -> None:
        chart_top = panel.top + 26
        chart_height = max(60, panel.height - 36)
        count = len(self._series)
        step = panel.width / max(count, 1)
        candle_width = max(1.5, min(12.0, step * 0.68))
        for index, candle in enumerate(self._series):
            x = panel.left + (index + 0.5) * step
            y_high = self._value_to_y(candle.high, chart_top, chart_height, min_price, max_price)
            y_low = self._value_to_y(candle.low, chart_top, chart_height, min_price, max_price)
            y_open = self._value_to_y(candle.open, chart_top, chart_height, min_price, max_price)
            y_close = self._value_to_y(candle.close, chart_top, chart_height, min_price, max_price)
            color = PALETTE["bull"] if candle.close >= candle.open else PALETTE["bear"]
            self.canvas.create_line(x, y_high, x, y_low, fill=color, width=1)
            top = min(y_open, y_close)
            bottom = max(y_open, y_close)
            self.canvas.create_rectangle(
                x - candle_width / 2,
                top,
                x + candle_width / 2,
                bottom if bottom > top else bottom + 1,
                outline=color,
                fill=color,
            )

    def _draw_price_line(
        self,
        panel: PanelBounds,
        *,
        values: list[float] | list[float | None],
        min_value: float,
        max_value: float,
        color: str,
        width: int,
        dash: tuple[int, int] | None = None,
    ) -> None:
        chart_top = panel.top + 26
        chart_height = max(60, panel.height - 36)
        count = len(values)
        if count <= 1:
            return

        step = panel.width / max(count - 1, 1)
        points: list[float] = []
        for index, value in enumerate(values):
            if value is None:
                self._flush_line(points, color=color, width=width, dash=dash)
                points = []
                continue
            x = panel.left + index * step
            y = self._value_to_y(float(value), chart_top, chart_height, min_value, max_value)
            points.extend([x, y])
        self._flush_line(points, color=color, width=width, dash=dash)

    def _draw_volume_bars(self, panel: PanelBounds) -> None:
        chart_top = panel.top + 24
        chart_height = max(24, panel.height - 30)
        max_volume = max(candle.volume for candle in self._series)
        if max_volume <= 0:
            max_volume = 1

        self.canvas.create_line(panel.left, panel.bottom - 6, panel.right, panel.bottom - 6, fill=PALETTE["chart_grid"])
        self.canvas.create_text(
            8,
            chart_top + 4,
            anchor="w",
            text=f"{max_volume:,}",
            fill=PALETTE["muted"],
            font=("Segoe UI", 8),
        )

        count = len(self._series)
        step = panel.width / max(count, 1)
        bar_width = max(1.0, min(8.0, step * 0.65))
        for index, candle in enumerate(self._series):
            x = panel.left + (index + 0.5) * step
            height_scale = candle.volume / max_volume
            bar_top = panel.bottom - 6 - (chart_height * height_scale)
            color = PALETTE["bull"] if candle.close >= candle.open else PALETTE["bear"]
            self.canvas.create_rectangle(
                x - bar_width / 2,
                bar_top,
                x + bar_width / 2,
                panel.bottom - 6,
                outline="",
                fill=color if height_scale > 0.55 else PALETTE["volume"],
            )

    def _draw_rsi_panel(self, panel: PanelBounds, values: list[float | None]) -> None:
        chart_top = panel.top + 24
        chart_height = max(36, panel.height - 30)
        zone_70 = self._value_to_y(70.0, chart_top, chart_height, 0.0, 100.0)
        zone_30 = self._value_to_y(30.0, chart_top, chart_height, 0.0, 100.0)

        self.canvas.create_rectangle(
            panel.left,
            chart_top,
            panel.right,
            zone_70,
            outline="",
            fill=PALETTE["indicator_zone_high"],
        )
        self.canvas.create_rectangle(
            panel.left,
            zone_30,
            panel.right,
            chart_top + chart_height,
            outline="",
            fill=PALETTE["indicator_zone_low"],
        )

        for value, label, color in (
            (70.0, "70", PALETTE["danger"]),
            (50.0, "50", PALETTE["muted"]),
            (30.0, "30", PALETTE["success"]),
        ):
            y = self._value_to_y(value, chart_top, chart_height, 0.0, 100.0)
            self.canvas.create_line(panel.left, y, panel.right, y, fill=PALETTE["chart_grid_strong"], dash=(2, 4))
            self.canvas.create_text(8, y, anchor="w", text=label, fill=color, font=("Segoe UI", 8))

        self._draw_price_line(
            panel,
            values=values,
            min_value=0.0,
            max_value=100.0,
            color=PALETTE["indicator_rsi"],
            width=2,
        )

    def _draw_mode_summary(self, width: int, pad_top: int) -> None:
        description = CHART_MODE_DESCRIPTIONS[self._mode]
        self.canvas.create_text(
            width - 16,
            pad_top - 2,
            anchor="ne",
            text=description,
            fill=PALETTE["muted"],
            font=("Segoe UI", 8),
        )

    def _draw_legend(
        self,
        *,
        x: int,
        y: int,
        show_candles: bool,
        show_close_line: bool,
        show_indicators: bool,
        show_rsi: bool,
        show_volume: bool,
    ) -> None:
        legend_height = 22
        items: list[tuple[str, str, tuple[int, int] | None, str]] = []
        if show_candles:
            items.append(("Candles", PALETTE["bull"], None, "candle"))
        if show_close_line:
            items.append(("Close", PALETTE["chart_line"], (5, 4) if self._mode == "All" else None, "line"))
        if show_indicators:
            items.append(("SMA 20", PALETTE["indicator_slow"], (7, 3), "line"))
            items.append(("EMA 12", PALETTE["indicator_fast"], None, "line"))
            items.append(("EMA 26", PALETTE["indicator_mid"], None, "line"))
        if show_rsi:
            items.append(("RSI 14", PALETTE["indicator_rsi"], None, "line"))
        if show_volume:
            items.append(("Volume", PALETTE["volume"], None, "box"))

        for index, (label, color, dash, kind) in enumerate(items):
            y_offset = y + (index * legend_height)
            if kind == "candle":
                self.canvas.create_line(x + 6, y_offset + 3, x + 6, y_offset + 15, fill=color, width=1)
                self.canvas.create_rectangle(x + 2, y_offset + 6, x + 10, y_offset + 12, outline=color, fill=color)
            elif kind == "box":
                self.canvas.create_rectangle(x + 1, y_offset + 5, x + 11, y_offset + 15, outline="", fill=color)
            else:
                self.canvas.create_line(
                    x,
                    y_offset + 10,
                    x + 12,
                    y_offset + 10,
                    fill=color,
                    width=2,
                    dash=dash,
                )
            self.canvas.create_text(
                x + 18,
                y_offset + 10,
                anchor="w",
                text=label,
                fill=PALETTE["muted"],
                font=("Segoe UI", 8),
            )

    def _draw_time_labels(self, *, width: int, pad_left: int, pad_right: int, baseline: int) -> None:
        first_label = self._series[0].timestamp.strftime("%b %d")
        last_label = self._series[-1].timestamp.strftime("%b %d")
        self.canvas.create_text(pad_left, baseline, anchor="w", text=first_label, fill=PALETTE["muted"], font=("Segoe UI", 8))
        self.canvas.create_text(width - pad_right, baseline, anchor="e", text=last_label, fill=PALETTE["muted"], font=("Segoe UI", 8))

    def _price_bounds(self, indicators: StandardIndicatorSet, *, include_indicators: bool) -> tuple[float, float]:
        lows = [candle.low for candle in self._series]
        highs = [candle.high for candle in self._series]
        min_price = min(lows)
        max_price = max(highs)

        if include_indicators:
            for value in indicators.sma_20 + indicators.ema_12 + indicators.ema_26:
                if value is None:
                    continue
                min_price = min(min_price, value)
                max_price = max(max_price, value)

        if max_price == min_price:
            max_price += 1.0
        return min_price, max_price

    def _value_to_y(self, value: float, top: int, height: int, min_value: float, max_value: float) -> float:
        scale = (value - min_value) / (max_value - min_value)
        return top + height - (scale * height)

    def _flush_line(
        self,
        points: list[float],
        *,
        color: str,
        width: int,
        dash: tuple[int, int] | None,
    ) -> None:
        if len(points) < 4:
            return
        self.canvas.create_line(
            *points,
            fill=color,
            width=width,
            dash=dash,
            smooth=True,
            splinesteps=18,
        )

    @staticmethod
    def _normalize_mode(mode: str) -> str:
        normalized = mode.strip()
        for alias, resolved in (("line", "Default"), ("default", "Default")):
            if normalized.lower() == alias:
                return resolved
        for candidate in CHART_MODES:
            if candidate.lower() == normalized.lower():
                return candidate
        return DEFAULT_CHART_MODE
