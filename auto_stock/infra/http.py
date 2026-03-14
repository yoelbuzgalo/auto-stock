from __future__ import annotations

import json
import socket
from abc import ABC, abstractmethod
from typing import Any
from urllib import parse, request
from urllib.error import HTTPError, URLError

from auto_stock.infra.errors import HttpRequestError


class HttpClient(ABC):
    @abstractmethod
    def request_json(
        self,
        method: str,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        payload: dict[str, Any] | None = None,
        timeout_seconds: float | None = None,
    ) -> Any:
        raise NotImplementedError


class UrllibHttpClient(HttpClient):
    def __init__(self, default_timeout_seconds: float = 8.0, user_agent: str = "auto-stock") -> None:
        self.default_timeout_seconds = default_timeout_seconds
        self.user_agent = user_agent

    def request_json(
        self,
        method: str,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        payload: dict[str, Any] | None = None,
        timeout_seconds: float | None = None,
    ) -> Any:
        final_url = self._build_url(url, params)
        request_headers = {
            "Accept": "application/json",
            "User-Agent": self.user_agent,
        }
        if headers:
            request_headers.update(headers)

        data: bytes | None = None
        if payload is not None:
            request_headers.setdefault("Content-Type", "application/json")
            data = json.dumps(payload).encode("utf-8")

        req = request.Request(final_url, method=method.upper(), headers=request_headers, data=data)
        try:
            with request.urlopen(req, timeout=timeout_seconds or self.default_timeout_seconds) as response:
                body = response.read().decode("utf-8").strip()
        except HTTPError as exc:
            response_body = exc.read().decode("utf-8", errors="replace")
            raise HttpRequestError(
                f"HTTP {exc.code} calling {final_url}",
                status_code=exc.code,
                response_body=response_body,
            ) from exc
        except (URLError, socket.timeout) as exc:
            raise HttpRequestError(f"Unable to reach remote service: {final_url}") from exc

        if not body:
            return {}
        try:
            return json.loads(body)
        except json.JSONDecodeError as exc:
            raise HttpRequestError(f"Remote service returned invalid JSON: {final_url}", response_body=body) from exc

    @staticmethod
    def _build_url(url: str, params: dict[str, Any] | None) -> str:
        if not params:
            return url
        encoded = parse.urlencode(
            {key: value for key, value in params.items() if value is not None},
            doseq=True,
        )
        separator = "&" if "?" in url else "?"
        return f"{url}{separator}{encoded}"
