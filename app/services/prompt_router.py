from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Tuple

from app.core.config import settings


class PromptRouter:
    """
    Rule-based router untuk IF ELSE Mode.

    Fokus IF ELSE:
    - Tidak membuat draft laporan PM
    - Mapping prompt sederhana ke MCP tools yang tersedia
    - Build argument dasar
    - Khusus NGSIEM, user wajib supply CQL
    - Relative time seperti 30m, 1h, 1d, 7d akan dikonversi ke ISO datetime UTC
    """

    def detect_tool(self, prompt: str, available_tools: list[dict]) -> Tuple[Optional[str], str]:
        text = prompt.lower().strip()
        tool_names = {tool["name"] for tool in available_tools}

        def exists(name: str) -> Optional[str]:
            return name if name in tool_names else None

        # Connectivity & modules
        if any(keyword in text for keyword in ["cek koneksi", "check connection", "check connectivity", "test koneksi", "connectivity"]):
            return exists("falcon_check_connectivity"), "Matched connectivity command"

        if any(keyword in text for keyword in ["module aktif", "active module", "enabled module", "enabled modules", "list module aktif"]):
            return exists("falcon_list_enabled_modules"), "Matched enabled modules command"

        if any(keyword in text for keyword in ["semua module", "all module", "list modules", "list semua module"]):
            return exists("falcon_list_modules"), "Matched list modules command"

        # Detection Investigation Report / specific Detection ID
        if self._looks_like_detection_report_prompt(text) or self._extract_detection_ids(prompt, {}):
            if any(keyword in text for keyword in ["detection", "alert", "ldt:", "report", "investigasi", "investigation", "analisa", "analyse", "analyze"]):
                return exists("falcon_get_detection_details"), "Matched specific detection investigation/report command"

        # CrowdScore
        if any(keyword in text for keyword in ["crowd score", "crowdscore", "security score", "posture score"]):
            return exists("falcon_show_crowd_score"), "Matched CrowdScore command"

        # Cloud Security
        if any(keyword in text for keyword in ["kubernetes", "k8s", "container", "containers", "cluster", "namespace", "pod"]):
            if any(keyword in text for keyword in ["berapa", "jumlah", "count", "how many"]):
                return exists("falcon_count_kubernetes_containers"), "Matched Kubernetes container count command"
            return exists("falcon_search_kubernetes_containers"), "Matched Kubernetes container search command"

        if any(keyword in text for keyword in ["image vulnerability", "image vulnerabilities", "image assessment", "cvss", "vulnerable image", "container image cve", "cve image"]):
            return exists("falcon_search_images_vulnerabilities"), "Matched image vulnerability search command"

        if any(keyword in text for keyword in ["cloud asset", "cspm", "ec2", "vpc", "subnet", "load balancer", "public exposed", "public exposure", "aws", "azure", "gcp", "non-compliant", "compliance"]):
            return exists("falcon_search_cspm_assets"), "Matched CSPM cloud asset search command"

        # Custom IOA
        if any(keyword in text for keyword in ["ioa platform", "custom ioa platform", "available platform"]):
            return exists("falcon_get_ioa_platforms"), "Matched Custom IOA platforms command"

        if any(keyword in text for keyword in ["ioa rule type", "ioa rule types", "custom ioa rule type", "disposition id", "disposition ids"]):
            return exists("falcon_get_ioa_rule_types"), "Matched Custom IOA rule types command"

        if any(keyword in text for keyword in ["ioa rule group", "ioa rule groups", "custom ioa group", "custom ioa rule", "custom ioa"]):
            if any(keyword in text for keyword in ["delete", "hapus", "remove"]):
                if any(keyword in text for keyword in ["group", "groups"]):
                    return exists("falcon_delete_ioa_rule_groups"), "Matched Custom IOA rule group delete command"
                return exists("falcon_delete_ioa_rules"), "Matched Custom IOA rule delete command"
            if any(keyword in text for keyword in ["create", "buat", "add", "tambahkan"]):
                if any(keyword in text for keyword in ["group", "groups"]):
                    return exists("falcon_create_ioa_rule_group"), "Matched Custom IOA rule group create command"
                return exists("falcon_create_ioa_rule"), "Matched Custom IOA rule create command"
            if any(keyword in text for keyword in ["update", "ubah", "enable", "disable", "aktifkan", "nonaktifkan"]):
                if any(keyword in text for keyword in ["group", "groups"]):
                    return exists("falcon_update_ioa_rule_group"), "Matched Custom IOA rule group update command"
                return exists("falcon_update_ioa_rule"), "Matched Custom IOA rule update command"
            return exists("falcon_search_ioa_rule_groups"), "Matched Custom IOA rule group search command"

        # Host
        if self._is_detail_prompt(text) and any(keyword in text for keyword in ["host", "device", "sensor", "endpoint"]):
            return exists("falcon_get_host_details"), "Matched host detail command"

        if any(keyword in text for keyword in ["host", "device", "sensor", "endpoint"]):
            return exists("falcon_search_hosts"), "Matched host search command"

        # Detection
        if self._is_detail_prompt(text) and any(keyword in text for keyword in ["detection", "alert"]):
            return exists("falcon_get_detection_details"), "Matched detection detail command"

        if any(keyword in text for keyword in ["detection", "alert"]):
            return exists("falcon_search_detections"), "Matched detection search command"

        # Incident
        if self._is_detail_prompt(text) and any(keyword in text for keyword in ["incident"]):
            return exists("falcon_get_incident_details"), "Matched incident detail command"

        if any(keyword in text for keyword in ["incident"]):
            return exists("falcon_search_incidents"), "Matched incident search command"

        # Behavior
        if self._is_detail_prompt(text) and any(keyword in text for keyword in ["behavior", "behaviour"]):
            return exists("falcon_get_behavior_details"), "Matched behavior detail command"

        if any(keyword in text for keyword in ["behavior", "behaviour"]):
            return exists("falcon_search_behaviors"), "Matched behavior search command"

        # NGSIEM
        if any(keyword in text for keyword in ["ngsiem", "cql", "query log", "search log", "event"]):
            return exists("falcon_search_ngsiem"), "Matched NGSIEM search command"

        return None, "No IF ELSE rule matched"

    def build_arguments(self, tool_name: str, prompt: str, form_data: Dict[str, Any] | None = None) -> Dict[str, Any]:
        """
        Build arguments untuk MCP tool.

        form_data dipakai untuk input eksplisit dari UI, misalnya:
        - cql_query
        - query_string
        - start
        - limit
        - filter
        - ids
        """
        form_data = form_data or {}
        text = prompt.strip()

        if tool_name in {
            "falcon_check_connectivity",
            "falcon_list_enabled_modules",
            "falcon_list_modules",
            "falcon_show_crowd_score",
        }:
            return {}

        if tool_name == "falcon_search_hosts":
            return self._build_search_hosts_args(text, form_data)

        if tool_name == "falcon_get_host_details":
            ids = self._extract_ids(text, form_data)
            return {"ids": ids} if ids else {}

        if tool_name == "falcon_search_detections":
            return self._build_search_detections_args(text, form_data)

        if tool_name == "falcon_get_detection_details":
            ids = self._extract_detection_ids(text, form_data) or self._extract_ids(text, form_data)
            return {"ids": ids} if ids else {}

        if tool_name == "falcon_search_incidents":
            return self._build_search_incidents_args(text, form_data)

        if tool_name == "falcon_get_incident_details":
            ids = self._extract_ids(text, form_data)
            return {"ids": ids} if ids else {}

        if tool_name == "falcon_search_behaviors":
            return self._build_search_behaviors_args(text, form_data)

        if tool_name == "falcon_get_behavior_details":
            ids = self._extract_ids(text, form_data)
            return {"ids": ids} if ids else {}

        if tool_name in {
            "falcon_count_kubernetes_containers",
            "falcon_search_kubernetes_containers",
            "falcon_search_images_vulnerabilities",
            "falcon_search_cspm_assets",
        }:
            return self._build_cloud_security_args(tool_name, text, form_data)

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
            return self._build_custom_ioa_args(tool_name, text, form_data)

        if tool_name == "falcon_search_ngsiem":
            return self._build_ngsiem_args(text, form_data)

        if tool_name in {
            "falcon_search_cspm_assets",
            "falcon_search_images_vulnerabilities",
            "falcon_search_kubernetes_containers",
            "falcon_count_kubernetes_containers",
        }:
            limit = self._extract_limit(text, form_data, tool_name=tool_name)
            args: Dict[str, Any] = {"limit": limit}

            explicit_filter = form_data.get("filter")
            if explicit_filter:
                args["filter"] = explicit_filter

            if tool_name == "falcon_count_kubernetes_containers":
                # Count tool may accept filter, but does not need limit.
                args.pop("limit", None)

            return args


        return {}

    def validate_arguments(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[str]:
        """
        Return error message kalau argument belum valid.

        Important:
        - Jangan panggil builder argument di function ini.
        - Function ini hanya validasi arguments yang sudah dibuat.
        - Tidak boleh memakai variable prompt/text/form_data karena tidak tersedia di scope ini.
        """
        if tool_name == "falcon_search_ngsiem":
            query = arguments.get("query_string")
            if not query:
                return "NGSIEM membutuhkan CQL query. Isi field CQL Query terlebih dahulu."

        if tool_name in {
            "falcon_get_host_details",
            "falcon_get_detection_details",
            "falcon_get_incident_details",
            "falcon_get_behavior_details",
        }:
            ids = arguments.get("ids")
            if not ids:
                return "Detail tool membutuhkan ID. Masukkan ID spesifik terlebih dahulu."

        if tool_name in {
            "falcon_delete_ioa_rules",
            "falcon_delete_ioa_rule_groups",
        }:
            ids = (
                arguments.get("ids")
                or arguments.get("rule_ids")
                or arguments.get("rulegroup_ids")
                or arguments.get("rulegroup_ids[]")
            )
            if not ids:
                return "Delete Custom IOA membutuhkan ID spesifik. Jangan hapus berdasarkan nama saja."

        if tool_name in {
            "falcon_create_ioa_rule",
            "falcon_create_ioa_rule_group",
            "falcon_update_ioa_rule",
            "falcon_update_ioa_rule_group",
        }:
            # Validasi detail create/update sebaiknya mengikuti input_schema dari MCP server.
            # Jangan block terlalu agresif supaya confirmation guardrail di routes.py tetap jalan.
            return None

        # Cloud Security tools are read-only/count/search. Empty arguments are allowed.
        if tool_name in {
            "falcon_count_kubernetes_containers",
            "falcon_search_kubernetes_containers",
            "falcon_search_images_vulnerabilities",
            "falcon_search_cspm_assets",
        }:
            return None

        # Custom IOA read-only tools. Empty arguments are allowed for platform/rule type discovery.
        if tool_name in {
            "falcon_get_ioa_platforms",
            "falcon_get_ioa_rule_types",
            "falcon_search_ioa_rule_groups",
        }:
            return None

        return None

    def build_summary(self, tool_name: str) -> str:
        if tool_name == "falcon_check_connectivity":
            return "Connectivity check dijalankan untuk memastikan MCP server dapat terhubung ke Falcon API."

        if tool_name in {"falcon_list_enabled_modules", "falcon_list_modules"}:
            return "Daftar module Falcon MCP berhasil diminta. Gunakan hasil ini untuk memastikan capability yang tersedia di server."

        if tool_name == "falcon_show_crowd_score":
            return "CrowdScore diminta untuk melihat posture/security score environment berdasarkan data Falcon."

        if tool_name == "falcon_search_hosts":
            return (
                "Data host berhasil diambil. Fokus review host untuk kebutuhan PM adalah hostname, platform, OS version, "
                "product type, sensor version, last seen, status, dan device ID."
            )

        if tool_name == "falcon_get_host_details":
            return (
                "Detail host berhasil diminta. Gunakan informasi ini untuk validasi sensor health, policy assignment, "
                "last seen, network info, dan status endpoint."
            )

        if tool_name == "falcon_search_detections":
            return (
                "Data detection berhasil diambil. Prioritaskan review berdasarkan severity, status, hostname, tactic, "
                "technique, dan command line."
            )

        if tool_name == "falcon_get_detection_details":
            return ("Detail detection berhasil diminta. Gunakan hasilnya untuk membuat laporan investigasi: "
                    "status detection, affected asset, threat context, evidence, timeline, assessment, dan recommended action.")

        if tool_name == "falcon_search_incidents":
            return "Data incident berhasil diminta. Review incident aktif berdasarkan severity, status, host terdampak, dan timeline."

        if tool_name == "falcon_get_incident_details":
            return "Detail incident berhasil diminta. Gunakan hasilnya untuk memahami korelasi behavior dan rekomendasi respons."

        if tool_name == "falcon_search_behaviors":
            return "Data behavior berhasil diminta. Review behavior untuk memahami aktivitas mencurigakan yang terkait detection/incident."

        if tool_name == "falcon_get_behavior_details":
            return "Detail behavior berhasil diminta. Gunakan hasilnya untuk analisis tactic, technique, dan konteks proses."

        if tool_name in {
            "falcon_count_kubernetes_containers",
            "falcon_search_kubernetes_containers",
            "falcon_search_images_vulnerabilities",
            "falcon_search_cspm_assets",
        }:
            return self._build_cloud_security_args(tool_name, text, form_data)

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
            return self._build_custom_ioa_args(tool_name, text, form_data)

        if tool_name == "falcon_search_ngsiem":
            return (
                "Query NGSIEM berhasil dikirim. Validasi hasil berdasarkan event type, timestamp, host, user, process, "
                "command line, dan field penting lain sesuai use case."
            )

        if tool_name in {"falcon_search_cspm_assets"}:
            return "Data CSPM cloud assets berhasil diminta. Review provider, resource type, exposure, severity, compliance, dan tag bisnis."

        if tool_name in {"falcon_search_kubernetes_containers", "falcon_count_kubernetes_containers"}:
            return "Data Kubernetes/container berhasil diminta. Review cluster, namespace, image, container name, provider, dan runtime context."

        if tool_name == "falcon_search_images_vulnerabilities":
            return "Data image vulnerabilities berhasil diminta. Prioritaskan berdasarkan severity, CVSS, CVE, fix availability, registry, repository, dan tag image."

        if "ioa" in tool_name:
            return "Data Custom IOA berhasil diproses. Untuk create/update/delete, pastikan perubahan sudah dikonfirmasi dan validasi kembali status rule atau rule group di Falcon."

        return "Request berhasil diproses melalui MCP server."

    def get_result_type(self, tool_name: str) -> str:
        """
        Dipakai frontend untuk menentukan renderer table.
        """
        if "kubernetes" in tool_name or "container" in tool_name:
            return "container"

        if "images_vulnerabilities" in tool_name:
            return "image_vulnerability"

        if "cspm" in tool_name or "cloud" in tool_name:
            return "cloud_asset"

        if "ioa" in tool_name:
            return "custom_ioa"

        if "host" in tool_name:
            return "host"

        if "detection" in tool_name:
            return "detection"

        if "incident" in tool_name:
            return "incident"

        if "behavior" in tool_name:
            return "behavior"

        if "ngsiem" in tool_name:
            return "ngsiem"

        if "module" in tool_name:
            return "module"

        if "crowd_score" in tool_name:
            return "crowd_score"

        return "generic"

    def _build_search_hosts_args(self, prompt: str, form_data: Dict[str, Any]) -> Dict[str, Any]:
        limit = self._extract_limit(prompt, form_data)
        explicit_filter = form_data.get("filter")

        if explicit_filter:
            return {"filter": explicit_filter, "limit": limit}

        hostname = self._extract_after_keywords(prompt, ["hostname", "host", "nama host"])
        if hostname and not self._is_generic_word(hostname):
            return {
                "filter": f"hostname:'{hostname}'",
                "limit": limit,
            }

        prompt_lower = prompt.lower()

        if "windows" in prompt_lower:
            return {"filter": "platform_name:'Windows'", "limit": limit}

        if "linux" in prompt_lower:
            return {"filter": "platform_name:'Linux'", "limit": limit}

        if "mac" in prompt_lower:
            return {"filter": "platform_name:'Mac'", "limit": limit}

        if "server" in prompt_lower:
            return {"filter": "product_type_desc:'Server'", "limit": limit}

        return {"limit": limit}

    def _build_search_detections_args(self, prompt: str, form_data: Dict[str, Any]) -> Dict[str, Any]:
        limit = self._extract_limit(prompt, form_data)
        explicit_filter = form_data.get("filter")

        if explicit_filter:
            return {"filter": explicit_filter, "limit": limit}

        text = prompt.lower()

        if "critical" in text:
            return {"filter": "max_severity_displayname:'Critical'", "limit": limit}

        if "high" in text:
            return {"filter": "max_severity_displayname:'High'", "limit": limit}

        if "new" in text:
            return {"filter": "status:'new'", "limit": limit}

        if "in progress" in text:
            return {"filter": "status:'in_progress'", "limit": limit}

        hostname = self._extract_after_keywords(prompt, ["hostname", "host"])
        if hostname and not self._is_generic_word(hostname):
            return {"filter": f"hostname:'{hostname}'", "limit": limit}

        return {"limit": limit}

    def _build_search_incidents_args(self, prompt: str, form_data: Dict[str, Any]) -> Dict[str, Any]:
        limit = self._extract_limit(prompt, form_data)
        explicit_filter = form_data.get("filter")

        if explicit_filter:
            return {"filter": explicit_filter, "limit": limit}

        text = prompt.lower()

        if "closed" in text:
            return {"filter": "status:'closed'", "limit": limit}

        if "new" in text or "open" in text or "active" in text:
            return {"filter": "status:'new'", "limit": limit}

        # Keep safe small query. Some tenant/API combinations may return 500 without a valid filter.
        return {"limit": limit}

    def _build_search_behaviors_args(self, prompt: str, form_data: Dict[str, Any]) -> Dict[str, Any]:
        limit = self._extract_limit(prompt, form_data)
        explicit_filter = form_data.get("filter")

        if explicit_filter:
            return {"filter": explicit_filter, "limit": limit}

        # Keep safe small query. Some tenant/API combinations may return 500 without a valid filter.
        return {"limit": limit}

    def _build_cloud_security_args(self, tool_name: str, prompt: str, form_data: Dict[str, Any]) -> Dict[str, Any]:
        limit = self._extract_limit(prompt, form_data)
        explicit_filter = form_data.get("filter")

        # Jika filter eksplisit diberikan dari UI, teruskan langsung.
        if tool_name == "falcon_count_kubernetes_containers":
            return {"filter": explicit_filter} if explicit_filter else {}

        args: Dict[str, Any] = {"limit": limit}
        if explicit_filter:
            args["filter"] = explicit_filter

        # Safe fallback: search tanpa filter supaya tidak gagal karena field FQL salah.
        # Untuk FQL Cloud/Kubernetes/Image yang lebih presisi, gunakan LLM Mode atau isi form_data["filter"].
        return args

    def _build_custom_ioa_args(self, tool_name: str, prompt: str, form_data: Dict[str, Any]) -> Dict[str, Any]:
        if tool_name in {"falcon_get_ioa_platforms", "falcon_get_ioa_rule_types"}:
            return {}

        limit = self._extract_limit(prompt, form_data)
        explicit_filter = form_data.get("filter")

        if tool_name == "falcon_search_ioa_rule_groups":
            args: Dict[str, Any] = {"limit": limit}
            if explicit_filter:
                args["filter"] = explicit_filter
            return args

        # Untuk create/update/delete, schema detail sangat tergantung MCP tool input_schema.
        # Karena itu IF ELSE hanya meneruskan form_data yang eksplisit diberikan user/UI.
        # routes.py tetap akan meminta confirmation untuk modify/destructive tools.
        args = dict(form_data)
        for ignored_key in ["confirmed", "cql_query", "query_string", "query", "start", "time_range", "limit", "filter"]:
            args.pop(ignored_key, None)

        ids = self._extract_ids(prompt, form_data)
        if ids and "ids" not in args:
            args["ids"] = ids

        return args

    def _build_ngsiem_args(self, prompt: str, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        NGSIEM wajib CQL.

        NOTE:
        falcon_search_ngsiem schema membutuhkan key:
        - query_string

        Bukan:
        - query

        start harus ISO datetime.
        UI boleh isi 30m, 1h, 24h, 1d, 7d; backend akan convert ke ISO UTC.
        """
        cql_query = (
            form_data.get("cql_query")
            or form_data.get("query_string")
            or form_data.get("query")
            or self._extract_cql_from_prompt(prompt)
        )

        start_raw = form_data.get("start") or form_data.get("time_range") or "1h"
        start = self._normalize_start_time(start_raw)

        limit = self._extract_limit(prompt, form_data)

        args = {
            "query_string": cql_query,
            "start": start,
        }

        if limit:
            args["limit"] = limit

        return args

    def _normalize_start_time(self, value: str) -> str:
        """
        Convert input seperti 30m, 1h, 24h, 1d, 7d menjadi ISO datetime UTC.

        falcon_search_ngsiem membutuhkan ISO format, bukan relative time.
        Contoh output:
        2026-04-26T02:35:00.000000Z
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

            # Kalau user sudah isi ISO datetime, validasi lalu return as-is.
            datetime.fromisoformat(value.replace("Z", "+00:00"))
            return value

        except Exception:
            # fallback aman: 1 jam terakhir
            return (now - timedelta(hours=1)).isoformat().replace("+00:00", "Z")

    def _extract_cql_from_prompt(self, prompt: str) -> str:
        lowered = prompt.lower()

        markers = [
            "query ngsiem",
            "ngsiem query",
            "cql",
            "search ngsiem",
            "cek log ngsiem",
        ]

        for marker in markers:
            index = lowered.find(marker)
            if index >= 0:
                extracted = prompt[index + len(marker):].strip(" :-")
                return extracted

        return ""


    def _looks_like_detection_report_prompt(self, text: str) -> bool:
        """
        Detect prompt intent for detailed detection investigation report.
        """
        detection_terms = [
            "detection",
            "alert",
            "ldt:",
        ]

        report_terms = [
            "report",
            "laporan",
            "investigasi",
            "investigation",
            "analisa",
            "analysis",
            "status",
            "detail",
            "triage",
        ]

        return any(term in text for term in detection_terms) and any(term in text for term in report_terms)

    def _extract_detection_ids(self, prompt: str, form_data: Dict[str, Any]) -> list[str]:
        """
        Extract Falcon detection/composite IDs more safely.

        Detection IDs can contain colon, underscore, dash, dot, or long base-like strings.
        Preserve the exact ID as much as possible.
        """
        if form_data.get("ids"):
            ids = form_data["ids"]
            if isinstance(ids, list):
                return [str(item).strip() for item in ids if str(item).strip()]
            if isinstance(ids, str):
                return [item.strip() for item in re.split(r"[,\s]+", ids) if item.strip()]

        if form_data.get("id"):
            return [str(form_data["id"]).strip()]

        candidates: list[str] = []

        # Common explicit patterns.
        patterns = [
            r"\bldt:[A-Za-z0-9:_\-.]+",
            r"\bdetection_id[:=]\s*([A-Za-z0-9:_\-.]+)",
            r"\bdetect(?:ion)?\s+id[:=]?\s*([A-Za-z0-9:_\-.]+)",
        ]

        for pattern in patterns:
            for match in re.finditer(pattern, prompt, flags=re.IGNORECASE):
                value = match.group(1) if match.lastindex else match.group(0)
                value = value.strip().strip(".,;()[]{}<>\"'")
                if len(value) >= 8 and value not in candidates:
                    candidates.append(value)

        # Fallback: long token that includes detection-looking prefix or separators.
        for token in re.split(r"\s+", prompt):
            cleaned = token.strip().strip(".,;()[]{}<>\"'")
            lower = cleaned.lower()

            if len(cleaned) < 16:
                continue

            if lower in {
                "detection",
                "detection_id",
                "incident",
                "behavior",
                "detail",
                "report",
            }:
                continue

            if lower.startswith("ldt:") or ":" in cleaned or "_" in cleaned or "-" in cleaned:
                if cleaned not in candidates:
                    candidates.append(cleaned)

        return candidates


    def _extract_ids(self, prompt: str, form_data: Dict[str, Any]) -> list[str]:
        if form_data.get("ids"):
            ids = form_data["ids"]
            if isinstance(ids, list):
                return ids
            if isinstance(ids, str):
                return [item.strip() for item in ids.split(",") if item.strip()]

        if form_data.get("id"):
            return [str(form_data["id"]).strip()]

        words = prompt.replace(",", " ").split()
        candidates = []

        for word in words:
            cleaned = word.strip()
            if len(cleaned) >= 16 and cleaned.lower() not in {
                "detail",
                "host",
                "detection",
                "incident",
                "behavior",
                "behaviour",
            }:
                candidates.append(cleaned)

        return candidates


    def _get_tool_max_limit(self, tool_name: str | None = None) -> int:
        """
        Tool-specific max limit.

        Policy:
        - Cloud Security tools max limit <= 1000
        - Custom IOA tools max limit <= 500
        - Other Falcon search tools max limit <= 5000
        """
        if not tool_name:
            return 5000

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

        if tool_name in custom_ioa_tools or "ioa" in tool_name:
            return 500

        if tool_name in cloud_tools:
            return 1000

        return 5000

    def _apply_tool_limit(self, arguments: Dict[str, Any], tool_name: str | None = None) -> Dict[str, Any]:
        if not isinstance(arguments, dict):
            return {}

        if "limit" not in arguments:
            return arguments

        max_limit = self._get_tool_max_limit(tool_name)

        try:
            arguments["limit"] = min(max(int(arguments.get("limit", max_limit)), 1), max_limit)
        except Exception:
            arguments["limit"] = max_limit

        return arguments


    def _extract_limit(self, prompt: str, form_data: Dict[str, Any], tool_name: str | None = None) -> int:
        # Default max is intentionally small to avoid heavy API requests.
        max_limit = self._get_tool_max_limit(tool_name)

        if form_data.get("limit"):
            try:
                return min(max(int(form_data["limit"]), 1), max_limit)
            except Exception:
                pass

        for token in prompt.split():
            if token.isdigit():
                return min(max(int(token), 1), max_limit)

        return min(settings.default_limit, max_limit)

    def _extract_after_keywords(self, prompt: str, keywords: list[str]) -> str:
        words = prompt.strip().split()

        for index, word in enumerate(words):
            normalized = word.lower().strip(":")
            if normalized in keywords and index + 1 < len(words):
                return words[index + 1].strip()

        return ""

    def _is_detail_prompt(self, text: str) -> bool:
        return any(keyword in text for keyword in ["detail", "details", "lihat detail", "get detail"])

    def _is_generic_word(self, value: str) -> bool:
        return value.lower() in {
            "host",
            "device",
            "sensor",
            "endpoint",
            "windows",
            "linux",
            "mac",
            "server",
            "detail",
        }
