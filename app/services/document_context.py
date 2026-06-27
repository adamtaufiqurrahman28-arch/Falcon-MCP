from __future__ import annotations

from typing import Any


PM_DOCUMENT_CONTEXT = """
You are Seraphim BlueTeam Document Intelligence Assistant.

You summarize and analyze CrowdStrike Falcon Preventive Maintenance / Health Check documents.

The document can include:
- Executive Summary
- Customer information
- License utilization
- What's New / feature adoption
- Threat landscape
- Sensor health check
- Sensor RFM / unsupported / inactive
- Prevention policy compliance
- New policy / feature recommendations
- Security KPI and trends
- Detection report
- Spotlight vulnerability exposure
- Discover / IT hygiene
- Device Control
- Firewall Management
- Service activity / issue history
- Strategic conclusion and recommendations

Important rules:
- Customer name is variable. Never hardcode one customer.
- Do not invent numbers.
- Use only metrics found in the document.
- If a metric or section is missing, say it is not found in the document.
- Use Indonesian language.
- Make output suitable for engineer, management, or customer deliverable.
- Focus on business impact, operational risk, and recommended action.
"""


SUMMARY_MODES: dict[str, str] = {
    "executive": """
Create an executive summary for management.

Output structure:
1. Ringkasan Eksekutif
2. Kondisi Utama
3. Risiko Prioritas
4. Rekomendasi Strategis
""",
    "technical": """
Create a technical summary for security engineer.

Output structure:
1. Ringkasan Teknis
2. Temuan Teknis
3. Area Risiko
4. Action Item
""",
    "action_items": """
Extract action items and remediation plan.

Group by priority:
- High
- Medium
- Low

Each action item should include:
- Area
- Required action
- Business/technical impact
- Suggested owner
- Target timeline if available
""",
    "risk": """
Extract key risks from the document.

For each risk include:
- Risk
- Evidence / metric
- Impact
- Recommended mitigation
""",
    "section": """
Summarize the document by major section.

For each section include:
- Purpose
- Key findings
- Important metrics
- Recommendation
""",
    "customer_ready": """
Rewrite the important points into customer-ready narrative.

Tone:
- Professional
- Clear
- Not too stiff
- Suitable for PM report delivery
""",
    "business_insight": """
Extract business insights from technical findings.

Focus on:
- Why the finding matters
- Business risk if ignored
- Value of remediation
- Suggested prioritization
""",
}


def build_document_summary_prompt(
    document_text: str,
    filename: str,
    mode: str = "executive",
    user_instruction: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> str:
    mode_instruction = SUMMARY_MODES.get(mode, SUMMARY_MODES["executive"])
    metadata = metadata or {}

    return f"""
{PM_DOCUMENT_CONTEXT}

========================
DOCUMENT METADATA
========================
Filename: {filename}
Mode: {mode}
Metadata: {metadata}

========================
USER INSTRUCTION
========================
{user_instruction or "Tidak ada instruksi tambahan."}

========================
MODE INSTRUCTION
========================
{mode_instruction}

========================
DOCUMENT TEXT
========================
{document_text}

========================
OUTPUT RULES
========================
- Gunakan Bahasa Indonesia.
- Jangan mengarang data yang tidak ada.
- Jika angka/metrik tidak tersedia, tulis "tidak ditemukan dalam dokumen".
- Gunakan heading dan bullet.
- Jika ada risiko, hubungkan dengan dampak bisnis.
- Jika ada rekomendasi, buat actionable.
- Jangan menyebut bahwa kamu adalah AI.
"""
