class AutoStockError(Exception):
    """Base application error."""


class ValidationError(AutoStockError):
    """Raised when user or provider data fails validation."""


class ConfigurationError(AutoStockError):
    """Raised when required configuration is missing or invalid."""


class HttpRequestError(AutoStockError):
    """Raised when a remote HTTP request fails."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        response_body: str | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class ProviderError(AutoStockError):
    """Raised when a market data provider cannot complete a request."""


class ProviderUnavailableError(ProviderError):
    """Raised when a provider is not configured or reachable."""


class BrokerError(AutoStockError):
    """Raised when broker operations fail."""


class PersistenceError(AutoStockError):
    """Raised when persisted data cannot be loaded or saved."""
