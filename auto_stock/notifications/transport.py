from __future__ import annotations

import json
import socket
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any
from urllib import parse, request
from urllib.error import HTTPError, URLError

from auto_stock.infra.errors import HttpRequestError


@dataclass(frozen=True, slots=True)
class NotificationResponse:
    status_code: int
    body: str


class NotificationTransport(ABC):
    @abstractmethod
    def post_json(
        self,
        url: str,
        payload: dict[str, Any],
        *,
        headers: dict[str, str] | None = None,
        timeout_seconds: float | None = None,
    ) -> NotificationResponse:
        raise NotImplementedError

    @abstractmethod
    def post_form(
        self,
        url: str,
        payload: dict[str, Any],
        *,
        headers: dict[str, str] | None = None,
        timeout_seconds: float | None = None,
    ) -> NotificationResponse:
        raise NotImplementedError


class UrllibNotificationTransport(NotificationTransport):
    def __init__(self, default_timeout_seconds: float = 8.0, user_agent: str = "auto-stock/0.1.0") -> None:
        self.default_timeout_seconds = default_timeout_seconds
        self.user_agent = user_agent

    def post_json(
        self,
        url: str,
        payload: dict[str, Any],
        *,
        headers: dict[str, str] | None = None,
        timeout_seconds: float | None = None,
    ) -> NotificationResponse:
        return self._request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            content_type="application/json",
            headers=headers,
            timeout_seconds=timeout_seconds,
        )

    def post_form(
        self,
        url: str,
        payload: dict[str, Any],
        *,
        headers: dict[str, str] | None = None,
        timeout_seconds: float | None = None,
    ) -> NotificationResponse:
        encoded = parse.urlencode(
            {key: value for key, value in payload.items() if value is not None},
            doseq=True,
        ).encode("utf-8")
        return self._request(
            url,
            data=encoded,
            content_type="application/x-www-form-urlencoded",
            headers=headers,
            timeout_seconds=timeout_seconds,
        )

    def _request(
        self,
        url: str,
        *,
        data: bytes,
        content_type: str,
        headers: dict[str, str] | None,
        timeout_seconds: float | None,
    ) -> NotificationResponse:
        request_headers = {
            "Accept": "application/json",
            "Content-Type": content_type,
            "User-Agent": self.user_agent,
        }
        if headers:
            request_headers.update(headers)

        req = request.Request(url, data=data, method="POST", headers=request_headers)
        try:
            with request.urlopen(req, timeout=timeout_seconds or self.default_timeout_seconds) as response:
                body = response.read().decode("utf-8", errors="replace").strip()
                return NotificationResponse(status_code=response.getcode(), body=body)
        except HTTPError as exc:
            response_body = exc.read().decode("utf-8", errors="replace")
            raise HttpRequestError(
                f"HTTP {exc.code} calling {url}",
                status_code=exc.code,
                response_body=response_body,
            ) from exc
        except (URLError, socket.timeout) as exc:
            raise HttpRequestError(f"Unable to reach remote service: {url}") from exc
