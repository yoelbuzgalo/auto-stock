from src.config import CONFIG


DEFAULT_TICKER = CONFIG.default_ticker

MAX_WORKERS = CONFIG.worker.max_workers
MAX_QUEUE_SIZE = CONFIG.worker.max_queue_size
QUEUE_POLL = CONFIG.worker.queue_poll

WINDOW_TITLE = CONFIG.window.title
WINDOW_GEOMETRY = CONFIG.window.geometry
APPEARANCE_MODE = CONFIG.window.appearance_mode
COLOR_THEME = CONFIG.window.color_theme
DEBOUNCE_RESIZE_MS = CONFIG.window.debounce_resize_ms

COLUMN_WEIGHT_MAIN_0 = CONFIG.layout.column_weight_main_0
COLUMN_WEIGHT_MAIN_1 = CONFIG.layout.column_weight_main_1
COLUMN_WEIGHT_MAIN_2 = CONFIG.layout.column_weight_main_2
ROW_WEIGHT_MAIN_0 = CONFIG.layout.row_weight_main_0
ROW_WEIGHT_MAIN_1 = CONFIG.layout.row_weight_main_1

PADDING_MAIN_X = CONFIG.layout.padding_main_x
PADDING_MAIN_Y = CONFIG.layout.padding_main_y

CHART_PANEL_WIDTH = CONFIG.chart.panel_width
CHART_PANEL_HEIGHT = CONFIG.chart.panel_height
PADDING_CHART_PANEL_X = CONFIG.chart.padding_panel_x
PADDING_CHART_PANEL_Y = CONFIG.chart.padding_panel_y
PADDING_CHART_INNER_X = CONFIG.chart.padding_inner_x
PADDING_CHART_INNER_Y = CONFIG.chart.padding_inner_y

FEAR_PANEL_WIDTH = CONFIG.fear.panel_width
FEAR_PANEL_HEIGHT = CONFIG.fear.panel_height
PADDING_FEAR_PANEL_X = CONFIG.fear.padding_panel_x
PADDING_FEAR_PANEL_Y = CONFIG.fear.padding_panel_y
PADDING_FEAR_INNER_X = CONFIG.fear.padding_inner_x
PADDING_FEAR_INNER_Y = CONFIG.fear.padding_inner_y

SENTIMENT_PANEL_WIDTH = CONFIG.sentiment.panel_width
SENTIMENT_PANEL_HEIGHT = CONFIG.sentiment.panel_height
PADDING_SENTIMENT_PANEL_X = CONFIG.sentiment.padding_panel_x
PADDING_SENTIMENT_PANEL_Y = CONFIG.sentiment.padding_panel_y
PADDING_SENTIMENT_INNER_X = CONFIG.sentiment.padding_inner_x
PADDING_SENTIMENT_INNER_Y = CONFIG.sentiment.padding_inner_y
PADDING_SENTIMENT_OUTER_Y = CONFIG.sentiment.padding_outer_y

NEWS_ROW_HEIGHT = CONFIG.sentiment.news_row_height
NEWS_ARTICLE_LIMIT = CONFIG.sentiment.news_article_limit
NEWS_CHAR_LIMIT = CONFIG.sentiment.news_char_limit
PADDING_NEWS_LIST_X = CONFIG.sentiment.padding_news_list_x
PADDING_NEWS_LIST_Y = CONFIG.sentiment.padding_news_list_y
PADDING_NEWS_BADGE_X = CONFIG.sentiment.padding_news_badge_x

ORDER_PANEL_WIDTH = CONFIG.order.panel_width
ORDER_PANEL_HEIGHT = CONFIG.order.panel_height
PADDING_ORDER_PANEL_X = CONFIG.order.padding_panel_x
PADDING_ORDER_PANEL_Y = CONFIG.order.padding_panel_y
PADDING_ORDER_INNER_X = CONFIG.order.padding_inner_x
PADDING_ORDER_INNER_Y = CONFIG.order.padding_inner_y
PADDING_ORDER_OUTER_Y = CONFIG.order.padding_outer_y

LEDGER_ROW_HEIGHT = CONFIG.order.ledger_row_height
LEDGER_ROW_WIDTH = CONFIG.order.ledger_row_width
PADDING_LEDGER_LIST_X = CONFIG.order.padding_ledger_list_x
DETAILS_PADDING_X = CONFIG.order.details_padding_x

JSON_PATH = CONFIG.order.json_path

FONT_FAMILY = CONFIG.font.family
FONT_SIZE_LARGE = CONFIG.font.size_large
FONT_SIZE_MEDIUM = CONFIG.font.size_medium
FONT_SIZE_NORMAL = CONFIG.font.size_normal
FONT_SIZE_SUB = CONFIG.font.size_sub
FONT_SIZE_BODY = CONFIG.font.size_body
FONT_SIZE_SMALL = CONFIG.font.size_small
FONT_SIZE_MINI = CONFIG.font.size_mini

FALLBACK_VIX_VALUE = CONFIG.fear.fallback_vix_value

CANVAS_DEFAULT_DPI_MIN = CONFIG.chart.canvas_dpi


AI_PANEL_WIDTH = CONFIG.ai.panel_width
AI_PANEL_HEIGHT = CONFIG.ai.panel_height
PADDING_AI_HEADER_X = CONFIG.ai.padding_header_x
PADDING_AI_HEADER_Y_TOP = CONFIG.ai.padding_header_y_top
PADDING_AI_HEADER_Y_BOTTOM = CONFIG.ai.padding_header_y_bottom
PADDING_AI_CHAT_X = CONFIG.ai.padding_chat_x
PADDING_AI_CHAT_Y = CONFIG.ai.padding_chat_y
PADDING_AI_DOCK_X = CONFIG.ai.padding_dock_x
PADDING_AI_DOCK_Y_BOTTOM = CONFIG.ai.padding_dock_y_bottom
PADDING_AI_INPUT_X_RIGHT = CONFIG.ai.padding_input_x_right
PADDING_AI_GRID_X_RIGHT = CONFIG.ai.padding_grid_x_right
AI_SEND_BTN_WIDTH = CONFIG.ai.send_btn_width

OLLAMA_URL = CONFIG.ai.ollama_url
DEFAULT_MODEL = CONFIG.ai.default_model

PRICE_PATTERN = CONFIG.patterns.price_pattern
TICKER_PATTERN = CONFIG.patterns.ticker_pattern

RED = CONFIG.color.red
GREEN = CONFIG.color.green
WHITE = CONFIG.color.white
BLACK = CONFIG.color.black
DARK_GRAY = CONFIG.color.dark_gray
CHARCOAL = CONFIG.color.charcoal
MID_GRAY = CONFIG.color.mid_gray
LIGHT_GRAY = CONFIG.color.light_gray
MUTED_GRAY = CONFIG.color.muted_gray
SOFT_WHITE = CONFIG.color.soft_white
DEEP_BLUE = CONFIG.color.deep_blue
CRIMSON = CONFIG.color.crimson
SKY_BLUE = CONFIG.color.sky_blue
NIGHT_GRAY = CONFIG.color.night_gray

CHART_WIDTH_RATIO = 0.88
CHART_HEIGHT_RATIO = 0.78

CHART_MAX_WIDTH = 460
CHART_MAX_HEIGHT = 250

CHART_MIN_WIDTH = 320
CHART_MIN_HEIGHT = 210

CHART_MARGIN_LEFT = 0.12
CHART_MARGIN_RIGHT = 0.97
CHART_MARGIN_TOP = 0.82
CHART_MARGIN_BOTTOM = 0.28

CANVAS_DEFAULT_DPI_MIN = 80
MATPLOTLIB_FIG_W = CONFIG.chart.fig_w
MATPLOTLIB_FIG_H = CONFIG.chart.fig_h
MATPLOTLIB_LINEWIDTH = CONFIG.chart.linewidth
MATPLOTLIB_LABELSIZE = CONFIG.chart.labelsize
MATPLOTLIB_INTERVAL_DAYS = CONFIG.chart.interval_days

COLS = "main cols"
ROWS = "rows"