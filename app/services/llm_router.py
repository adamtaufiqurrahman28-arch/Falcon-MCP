from __future__ import annotations

import json
import re
from datetime import datetime, timedelta, timezone
from typing import Any

from app.services.llm_context import build_planner_prompt, build_summary_prompt
from app.services.llm_service import LLMService


class LLMRouter:
    """
    LLM planner untuk memilih MCP tool berdasarkan natural language prompt.

    Fix penting:
    - Summary tidak lagi mengirim raw MCP response full ke LLM.
    - MCP response akan di-compact dulu supaya tidak kena ContextWindowExceededError.
    """

    def __init__(self, llm_service: LLMService) -> None:
        self.llm_service = llm_service

    def select_tool(
        self,
        prompt: str,
        available_tools: list[dict[str, Any]],
    ) -> tuple[str | None, dict[str, Any], str]:
        if not self.llm_service.is_ready():
            return None, {}, "LLM belum siap. Cek LLM_API_KEY, LLM_BASE_URL, dan LLM_MODEL."

        planner_prompt = build_planner_prompt(prompt, available_tools)
        raw = self.llm_service.generate(planner_prompt, temperature=0.0)

        try:
            data = self._parse_json(raw)
        except Exception as error:
            return None, {}, f"LLM gagal mengembalikan JSON valid: {error}. Raw: {raw[:300]}"

        tool_name = data.get("tool_name")
        arguments = data.get("arguments") or {}
        reason = data.get("reason") or "Dipilih oleh LLM."

        if tool_name in {"null", "None", ""}:
            tool_name = None

        available_names = {tool.get("name") for tool in available_tools}
        if tool_name and tool_name not in available_names:
            return None, {}, f"LLM memilih tool yang tidak tersedia: {tool_name}"

        if not isinstance(arguments, dict):
            arguments = {}

        arguments = self._normalize_arguments(tool_name, arguments)

        return tool_name, arguments, reason

    def summarize_result(
        self,
        prompt: str,
        mcp_response: Any,
        tool_name: str | None = None,
        arguments: dict[str, Any] | None = None,
    ) -> str:
        """
        Summary LLM dibuat dari compact response, bukan raw response penuh.

        Ini mencegah error:
        ContextWindowExceededError / Input tokens exceed configured limit.
        """
        if not self.llm_service.is_ready():
            return "LLM belum siap, summary otomatis tidak dapat dibuat."

        try:
            compact_response = self._compact_mcp_response(
                mcp_response,
                max_items=15,
                max_text_chars=12000,
            )

            summary_prompt = build_summary_prompt(
                user_prompt=prompt,
                tool_name=tool_name,
                arguments=arguments or {},
                mcp_response=compact_response,
            )

            return self.llm_service.generate(summary_prompt, temperature=0.2)

        except Exception as error:
            return f"Summary LLM gagal dibuat: {error}"

    def _parse_json(self, text: str) -> dict[str, Any]:
        """
        LLM kadang membungkus JSON dengan markdown.
        Function ini ambil object JSON pertama yang valid.
        """
        cleaned = text.strip()

        if cleaned.startswith("```"):
            cleaned = re.sub(
                r"^```(?:json)?",
                "",
                cleaned,
                flags=re.IGNORECASE,
            ).strip()
            cleaned = re.sub(r"```$", "", cleaned).strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
            if not match:
                raise
            return json.loads(match.group(0))

    def _normalize_arguments(
        self,
        tool_name: str | None,
        arguments: dict[str, Any],
    ) -> dict[str, Any]:
        if not tool_name:
            return {}

        # Normalize NGSIEM
        if tool_name == "falcon_search_ngsiem":
            if "query" in arguments and "query_string" not in arguments:
                arguments["query_string"] = arguments.pop("query")

            if "cql" in arguments and "query_string" not in arguments:
                arguments["query_string"] = arguments.pop("cql")

            if "cql_query" in arguments and "query_string" not in arguments:
                arguments["query_string"] = arguments.pop("cql_query")

            arguments.setdefault("start", "1h")
            arguments["start"] = self._normalize_start_time(str(arguments["start"]))
            arguments["limit"] = self._safe_limit(arguments.get("limit", 5000))

            return arguments

        # Normalize Cloud Security tools
        if tool_name in {
            "falcon_search_cspm_assets",
            "falcon_search_images_vulnerabilities",
            "falcon_search_kubernetes_containers",
        }:
            arguments["limit"] = self._safe_limit(arguments.get("limit", 1000), tool_name=tool_name)

            if arguments.get("filter") in {"", None}:
                arguments.pop("filter", None)

            return arguments

        if tool_name == "falcon_count_kubernetes_containers":
            # Count tool can run without limit.
            arguments.pop("limit", None)

            if arguments.get("filter") in {"", None}:
                arguments.pop("filter", None)

            return arguments

        # Normalize Custom IOA tools
        if tool_name in {
            "falcon_get_ioa_platforms",
            "falcon_get_ioa_rule_types",
            "falcon_search_ioa_rule_groups",
            "falcon_create_ioa_rule",
            "falcon_create_ioa_rule_group",
            "falcon_update_ioa_rule",
            "falcon_update_ioa_rule_group",
            "falcon_delete_ioa_rules",
            "falcon_delete_ioa_rule_groups",
        }:
            if "limit" in arguments:
                arguments["limit"] = self._safe_limit(arguments.get("limit", 500), tool_name=tool_name)

            if arguments.get("filter") in {"", None}:
                arguments.pop("filter", None)

            return arguments

        # Normalize detail tools
        if tool_name in {
            "falcon_get_host_details",
            "falcon_get_detection_details",
            "falcon_get_incident_details",
            "falcon_get_behavior_details",
        }:
            alias_keys = [
                "id",
                "detection_id",
                "detect_id",
                "incident_id",
                "behavior_id",
                "device_id",
                "aid",
            ]

            for key in alias_keys:
                if key in arguments and "ids" not in arguments:
                    value = arguments.pop(key)
                    arguments["ids"] = value if isinstance(value, list) else [value]

            if isinstance(arguments.get("ids"), str):
                arguments["ids"] = [arguments["ids"]]

            if isinstance(arguments.get("ids"), list):
                arguments["ids"] = [
                    str(item).strip()
                    for item in arguments["ids"]
                    if str(item).strip()
                ]

            return arguments

        # Normalize search tools
        if tool_name.startswith("falcon_search_"):
            arguments["limit"] = self._safe_limit(arguments.get("limit", 5000))

            # Clean empty filter
            if arguments.get("filter") in {"", None}:
                arguments.pop("filter", None)

            return arguments

        # No-argument tools
        if tool_name in {
            "falcon_check_connectivity",
            "falcon_list_enabled_modules",
            "falcon_list_modules",
            "falcon_show_crowd_score",
        }:
            if tool_name != "falcon_show_crowd_score":
                return {}

        return arguments

    def _safe_limit(self, value: Any, tool_name: str | None = None) -> int:
        """
        Clamp limit based on MCP tool policy.

        Policy:
        - Cloud Security tools max limit <= 1000
        - Custom IOA tools max limit <= 500
        - Other Falcon search tools max limit <= 5000
        """
        cloud_tools = {
            "falcon_search_cspm_assets",
            "falcon_search_images_vulnerabilities",
            "falcon_search_kubernetes_containers",
            "falcon_count_kubernetes_containers",
        }

        custom_ioa_tools = {
            "falcon_get_ioa_platforms",
            "falcon_get_ioa_rule_types",
            "falcon_search_ioa_rule_groups",
            "falcon_create_ioa_rule",
            "falcon_create_ioa_rule_group",
            "falcon_update_ioa_rule",
            "falcon_update_ioa_rule_group",
            "falcon_delete_ioa_rules",
            "falcon_delete_ioa_rule_groups",
        }

        if tool_name in custom_ioa_tools or (tool_name and "ioa" in tool_name):
            max_limit = 500
        elif tool_name in cloud_tools:
            max_limit = 1000
        else:
            max_limit = 5000

        try:
            limit = int(value)
        except Exception:
            limit = max_limit

        return max(1, min(limit, max_limit))

    def _normalize_start_time(self, value: str) -> str:
        """
        Convert 30m, 1h, 24h, 1d, 7d to ISO datetime UTC.
        falcon_search_ngsiem membutuhkan ISO datetime.
        """
        if not value:
            value = "1h"

        value = str(value).strip()
        value_lower = value.lower()
        now = datetime.now(timezone.utc)

        try:
            if value_lower.endswith("m"):
                minutes = int(value_lower[:-1])
                return (now - timedelta(minutes=minutes)).isoformat().replace("+00:00", "Z")

            if value_lower.endswith("h"):
                hours = int(value_lower[:-1])
                return (now - timedelta(hours=hours)).isoformat().replace("+00:00", "Z")

            if value_lower.endswith("d"):
                days = int(value_lower[:-1])
                return (now - timedelta(days=days)).isoformat().replace("+00:00", "Z")

            # If already ISO datetime, validate and return as-is.
            datetime.fromisoformat(value.replace("Z", "+00:00"))
            return value

        except Exception:
            # Safe fallback: last 1 hour
            return (now - timedelta(hours=1)).isoformat().replace("+00:00", "Z")

    def _compact_mcp_response(
        self,
        mcp_response: Any,
        max_items: int = 15,
        max_text_chars: int = 12000,
    ) -> Any:
        """
        Meringkas MCP response sebelum dikirim ke LLM.
        Tujuannya agar summary tidak melebihi context window.

        Frontend tetap bisa menerima raw result dari backend,
        tapi LLM summary hanya membaca compact response.
        """
        if mcp_response is None:
            return None

        if isinstance(mcp_response, str):
            return self._truncate_text(mcp_response, max_text_chars)

        if isinstance(mcp_response, list):
            return [
                self._compact_mcp_response(
                    item,
                    max_items=max_items,
                    max_text_chars=max_text_chars,
                )
                for item in mcp_response[:max_items]
            ]

        if isinstance(mcp_response, dict):
            compact: dict[str, Any] = {}

            # Keep important top-level metadata
            for key in [
                "status",
                "status_code",
                "error",
                "message",
                "summary",
                "tool",
                "result_type",
            ]:
                if key in mcp_response:
                    compact[key] = self._compact_mcp_response(
                        mcp_response[key],
                        max_items=max_items,
                        max_text_chars=max_text_chars,
                    )

            # Handle MCP result format
            if "result" in mcp_response and isinstance(mcp_response["result"], list):
                compact["result_count"] = len(mcp_response["result"])
                compact["result_sample"] = [
                    self._compact_mcp_response(
                        item,
                        max_items=max_items,
                        max_text_chars=max_text_chars,
                    )
                    for item in mcp_response["result"][:max_items]
                ]

            # Handle common data containers
            for key in [
                "data",
                "resources",
                "items",
                "results",
                "hosts",
                "detections",
                "events",
                "rows",
            ]:
                value = mcp_response.get(key)

                if isinstance(value, list):
                    compact[f"{key}_count"] = len(value)
                    compact[f"{key}_sample"] = [
                        self._compact_record(item)
                        for item in value[:max_items]
                    ]
                elif isinstance(value, dict):
                    compact[key] = self._compact_mcp_response(
                        value,
                        max_items=max_items,
                        max_text_chars=max_text_chars,
                    )

            # If dict did not match known fields, compact important keys only
            if not compact:
                compact = self._compact_record(mcp_response)

            return compact

        return mcp_response

    def _compact_record(self, record: Any) -> Any:
        """
        Ambil field penting saja dari 1 record host/detection/ngsiem.
        """
        if not isinstance(record, dict):
            if isinstance(record, str):
                return self._truncate_text(record, 2000)
            return record

        important_keys = [
            # Common / host
            "id",
            "aid",
            "device_id",
            "cid",
            "hostname",
            "computer_name",
            "device_name",
            "platform_name",
            "os_version",
            "product_type_desc",
            "agent_version",
            "sensor_version",
            "last_seen",
            "status",
            "local_ip",
            "external_ip",

            # Detection
            "detection_id",
            "max_severity_displayname",
            "severity",
            "tactic",
            "technique",
            "objective",
            "filename",
            "file_name",
            "cmdline",
            "command_line",
            "created_timestamp",
            "updated_timestamp",

            # Incident / behavior
            "incident_id",
            "behavior_id",
            "display_name",
            "description",
            "confidence",
            "scenario",
            "pattern_id",
            "parent_details",
            "device",

            # NGSIEM
            "@timestamp",
            "timestamp",
            "#event_simpleName",
            "event_simpleName",
            "ComputerName",
            "UserName",
            "FileName",
            "CommandLine",
            "ParentBaseFileName",
            "GrandParentBaseFileName",
            "TargetProcessId",
            "ContextProcessId",
            "ParentProcessId",
        ]

        compact = {}

        for key in important_keys:
            if key in record:
                value = record[key]
                if isinstance(value, str):
                    compact[key] = self._truncate_text(value, 1000)
                elif isinstance(value, dict):
                    compact[key] = self._compact_record(value)
                elif isinstance(value, list):
                    compact[key] = [
                        self._compact_record(item)
                        for item in value[:5]
                    ]
                else:
                    compact[key] = value

        # Kalau semua field penting kosong, ambil maksimal 12 key pertama
        if not compact:
            for index, (key, value) in enumerate(record.items()):
                if index >= 12:
                    break

                if isinstance(value, str):
                    compact[key] = self._truncate_text(value, 1000)
                elif isinstance(value, (int, float, bool)) or value is None:
                    compact[key] = value
                elif isinstance(value, list):
                    compact[key] = f"[list with {len(value)} items]"
                elif isinstance(value, dict):
                    compact[key] = "[object]"
                else:
                    compact[key] = str(value)

        return compact

    def _truncate_text(self, text: str, max_chars: int) -> str:
        if len(text) <= max_chars:
            return text

        return text[:max_chars] + f"\n...[truncated {len(text) - max_chars} chars]"
