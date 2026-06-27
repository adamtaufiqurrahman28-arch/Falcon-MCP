from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List

from redis.asyncio import Redis

from app.core.config import settings


class AuditService:
    """
    Redis-backed audit trail for Seraphim MCP.

    This service is intentionally fail-safe:
    Redis errors must not break MCP execution.
    """

    def __init__(self) -> None:
        self.enabled = bool(settings.audit_enabled and settings.redis_url)
        self.stream_key = settings.audit_stream_key
        self.max_len = settings.audit_max_len
        self.redis: Redis | None = None

        if self.enabled:
            self.redis = Redis.from_url(settings.redis_url, decode_responses=True)

    def new_request_id(self) -> str:
        return str(uuid.uuid4())

    def now(self) -> str:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    async def write_event(self, event_type: str, request_id: str, payload: Dict[str, Any]) -> None:
        if not self.enabled or self.redis is None:
            return

        event = {
            "timestamp": self.now(),
            "event_type": event_type,
            "request_id": request_id,
            "payload": self._safe_json(payload),
        }

        try:
            await self.redis.xadd(
                self.stream_key,
                event,
                maxlen=self.max_len,
                approximate=True,
            )
        except Exception:
            return

    async def write_request(
        self,
        request_id: str,
        prompt: str,
        mode: str,
        selected_by: str | None = None,
        tool: str | None = None,
        arguments: Dict[str, Any] | None = None,
        risk_level: str = "read",
        confirmed: bool = False,
    ) -> None:
        await self.write_event(
            "request",
            request_id,
            {
                "prompt": prompt,
                "mode": mode,
                "selected_by": selected_by,
                "tool": tool,
                "arguments": self._redact_arguments(arguments or {}),
                "risk_level": risk_level,
                "confirmed": confirmed,
            },
        )

    async def write_success(
        self,
        request_id: str,
        tool: str | None,
        result_type: str | None = None,
        result_count: int | None = None,
    ) -> None:
        await self.write_event(
            "success",
            request_id,
            {
                "tool": tool,
                "result_type": result_type,
                "result_count": result_count,
            },
        )

    async def write_error(
        self,
        request_id: str,
        tool: str | None,
        error: str,
        result_type: str | None = None,
    ) -> None:
        await self.write_event(
            "error",
            request_id,
            {
                "tool": tool,
                "result_type": result_type,
                "error": str(error)[:2000],
            },
        )

    async def write_blocked(
        self,
        request_id: str,
        tool: str,
        arguments: Dict[str, Any],
        risk_level: str,
        reason: str,
    ) -> None:
        await self.write_event(
            "blocked",
            request_id,
            {
                "tool": tool,
                "arguments": self._redact_arguments(arguments),
                "risk_level": risk_level,
                "reason": reason,
            },
        )

    async def recent(self, limit: int = 25) -> List[Dict[str, Any]]:
        if not self.enabled or self.redis is None:
            return []

        limit = max(1, min(int(limit), 100))

        try:
            rows = await self.redis.xrevrange(self.stream_key, count=limit)
        except Exception:
            return []

        events: List[Dict[str, Any]] = []

        for event_id, fields in rows:
            payload = fields.get("payload", "{}")
            try:
                payload_obj = json.loads(payload)
            except Exception:
                payload_obj = {"raw": payload}

            events.append(
                {
                    "id": event_id,
                    "timestamp": fields.get("timestamp"),
                    "event_type": fields.get("event_type"),
                    "request_id": fields.get("request_id"),
                    "payload": payload_obj,
                }
            )

        return events

    def _safe_json(self, value: Any) -> str:
        try:
            return json.dumps(value, default=str, ensure_ascii=False)
        except Exception:
            return json.dumps({"unserializable": str(value)}, ensure_ascii=False)

    def _redact_arguments(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        redacted: Dict[str, Any] = {}

        sensitive_fragments = [
            "client_secret",
            "secret",
            "token",
            "api_key",
            "password",
            "authorization",
        ]

        for key, value in arguments.items():
            lowered = str(key).lower()

            if any(fragment in lowered for fragment in sensitive_fragments):
                redacted[key] = "[REDACTED]"
                continue

            if isinstance(value, str) and len(value) > 2000:
                redacted[key] = value[:2000] + f"...[truncated {len(value) - 2000} chars]"
            else:
                redacted[key] = value

        return redacted
