classDiagram

class BrokerClient {
    <<abstract>>
    +authenticate()
    +get_account(account_id) Account
    +get_positions(account_id) list~Position~
    +get_orders(account_id) list~Order~
    +place_order(account_id, order) Order
    +cancel_order(account_id, order_id) bool
}

class SchwabClient {
    -client_id: str
    -client_secret: str
    -redirect_uri: str
    -access_token: str
    -refresh_token: str
    +authenticate()
    +refresh_access_token()
    +get_account(account_id) Account
    +get_positions(account_id) list~Position~
    +get_orders(account_id) list~Order~
    +place_order(account_id, order) Order
    +cancel_order(account_id, order_id) bool
}

BrokerClient <|-- SchwabClient

class Account {
    +account_id: str
    +account_type: str
    +cash_balance: float
    +buying_power: float
    +equity: float
}

class Position {
    +symbol: str
    +quantity: float
    +average_price: float
    +market_value: float
}

class Order {
    +order_id: str
    +symbol: str
    +side: str
    +quantity: float
    +order_type: str
    +status: str
    +price: float
    +time_in_force: str
}

class OrderLeg {
    +symbol: str
    +instruction: str
    +quantity: float
}

Account "1" o-- "*" Position
Account "1" o-- "*" Order
Order "1" o-- "*" OrderLeg

class MarketDataProvider {
    <<abstract>>
    +get_quote(symbol) Quote
    +get_candles(symbol, timeframe, start, end) list~Candle~
    +is_available() bool
    +normalize_quote(raw) Quote
    +normalize_candles(raw) list~Candle~
}

class SchwabDataSource {
    -base_url: str
    +get_quote(symbol) Quote
    +get_candles(symbol, timeframe, start, end) list~Candle~
    +is_available() bool
    +normalize_quote(raw) Quote
    +normalize_candles(raw) list~Candle~
}

class PolygonDataSource {
    -api_key: str
    -base_url: str
    +get_quote(symbol) Quote
    +get_candles(symbol, timeframe, start, end) list~Candle~
    +is_available() bool
    +normalize_quote(raw) Quote
    +normalize_candles(raw) list~Candle~
}

class AlpacaDataSource {
    -api_key: str
    -api_secret: str
    -base_url: str
    +get_quote(symbol) Quote
    +get_candles(symbol, timeframe, start, end) list~Candle~
    +is_available() bool
    +normalize_quote(raw) Quote
    +normalize_candles(raw) list~Candle~
}

MarketDataProvider <|-- SchwabDataSource
MarketDataProvider <|-- PolygonDataSource
MarketDataProvider <|-- AlpacaDataSource

class Quote {
    +symbol: str
    +bid: float
    +ask: float
    +last: float
    +volume: int
    +timestamp: datetime
    +source: str
}

class Candle {
    +symbol: str
    +timestamp: datetime
    +open: float
    +high: float
    +low: float
    +close: float
    +volume: int
    +source: str
}

class Endpoint {
    +base_url: str
    +path: str
    +method: str
    +headers: dict
    +params: dict
    +timeout: int
}

SchwabDataSource --> Quote
SchwabDataSource --> Candle
PolygonDataSource --> Quote
PolygonDataSource --> Candle
AlpacaDataSource --> Quote
AlpacaDataSource --> Candle

SchwabClient --> Account
SchwabClient --> Position
SchwabClient --> Order