from dataclasses import dataclass


@dataclass(frozen=True)
class WindowConfig:
    title: str = "Financial Analytics Dashboard"
    geometry: str = "1200x680"
    appearance_mode: str = "Dark"
    color_theme: str = "blue"
    debounce_resize_ms: int = 120


@dataclass(frozen=True)
class WorkerConfig:
    max_workers: int = 1
    max_queue_size: int = 20
    queue_poll: int = 20


@dataclass(frozen=True)
class LayoutConfig:
    column_weight_main_0: int = 4
    column_weight_main_1: int = 2
    column_weight_main_2: int = 2
    row_weight_main_0: int = 1
    row_weight_main_1: int = 1

    padding_main_x: int = 10
    padding_main_y: int = 10


@dataclass(frozen=True)
class ChartConfig:
    panel_width: int = 300
    panel_height: int = 400

    padding_panel_x: int = 4
    padding_panel_y: int = 4
    padding_inner_x: int = 6
    padding_inner_y: int = 4

    canvas_dpi: int = 100
    fig_w: float = 10
    fig_h: float = 10
    linewidth: float = 1.6
    labelsize: int = 7
    interval_days: int = 6


@dataclass(frozen=True)
class FearConfig:
    panel_width: int = 300
    panel_height: int = 155

    padding_panel_x: int = 4
    padding_panel_y: int = 5
    padding_inner_x: int = 10
    padding_inner_y: int = 8

    fallback_vix_value: float = 20.0


@dataclass(frozen=True)
class SentimentConfig:
    panel_width: int = 300
    panel_height: int = 205

    padding_panel_x: int = 4
    padding_panel_y: int = 5
    padding_inner_x: int = 8
    padding_inner_y: int = 5
    padding_outer_y: int = 5

    news_row_height: int = 36
    news_article_limit: int = 5
    news_char_limit: int = 35

    padding_news_list_x: int = 4
    padding_news_list_y: int = 3
    padding_news_badge_x: int = 6


@dataclass(frozen=True)
class OrderConfig:
    panel_width: int = 420
    panel_height: int = 610

    padding_panel_x: int = 4
    padding_panel_y: int = 4
    padding_inner_x: int = 8
    padding_inner_y: int = 5
    padding_outer_y: int = 5

    ledger_row_height: int = 42
    ledger_row_width: int = 5
    padding_ledger_list_x: int = 4
    details_padding_x: int = 8

    json_path: str = "data/orders.json"


@dataclass(frozen=True)
class AIConfig:
    panel_width: int = 285
    panel_height: int = 430

    padding_header_x: int = 8
    padding_header_y_top: int = 8
    padding_header_y_bottom: int = 4

    padding_chat_x: int = 8
    padding_chat_y: int = 6

    padding_dock_x: int = 8
    padding_dock_y_bottom: int = 8

    padding_input_x_right: int = 6
    padding_grid_x_right: int = 4

    send_btn_width: int = 54

    ollama_url: str = "http://localhost:11434/api/generate"
    default_model: str = "deepseek-r1:8b"


@dataclass(frozen=True)
class FontConfig:
    family: str = "Helvetica"

    size_large: int = 20
    size_medium: int = 14
    size_normal: int = 12
    size_sub: int = 11
    size_body: int = 10
    size_small: int = 9
    size_mini: int = 8


@dataclass(frozen=True)
class ColorConfig:
    red: str = "#ff0000"
    green: str = "#5FAE68"
    white: str = "#ffffff"
    black: str = "#000000"

    dark_gray: str = "#2b2b2b"
    charcoal: str = "#1E1E1E"
    mid_gray: str = "#444444"
    light_gray: str = "#aaaaaa"
    muted_gray: str = "#555555"
    soft_white: str = "#DCDCDC"

    deep_blue: str = "#1f538d"
    crimson: str = "#a80000"
    sky_blue: str = "#A3D8FF"
    night_gray: str = "#3A3A3A"


@dataclass(frozen=True)
class PatternConfig:
    price_pattern: str = r"\d{4}\-{1}\d{2}\-\d{2}\s{2}(\d+\.\d+)"
    ticker_pattern: str = r"Ticker\s+([A-Z]{4})"


@dataclass(frozen=True)
class AppConfig:
    default_ticker: str = "AAPL"

    window: WindowConfig = WindowConfig()
    worker: WorkerConfig = WorkerConfig()
    layout: LayoutConfig = LayoutConfig()
    chart: ChartConfig = ChartConfig()
    fear: FearConfig = FearConfig()
    sentiment: SentimentConfig = SentimentConfig()
    order: OrderConfig = OrderConfig()
    ai: AIConfig = AIConfig()
    font: FontConfig = FontConfig()
    color: ColorConfig = ColorConfig()
    patterns: PatternConfig = PatternConfig()


CONFIG = AppConfig()