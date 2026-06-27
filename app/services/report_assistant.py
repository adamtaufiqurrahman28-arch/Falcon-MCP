from typing import Dict, Optional

from app.services.report_templates import PMReportTemplates


class ReportAssistant:
    """
    Membantu pembuatan draft dokumen PM tanpa LLM.
    Cocok untuk IF ELSE Mode.
    """

    def detect_report_section(self, prompt: str) -> Optional[str]:
        text = prompt.lower()

        if any(keyword in text for keyword in ["ringkasan eksekutif", "executive summary", "summary pm", "rangkuman pm"]):
            return "executive_summary"

        if any(keyword in text for keyword in ["sensor health", "coverage", "rfm", "unsupported", "inactive sensor"]):
            return "sensor_health"

        if any(keyword in text for keyword in ["prevention policy", "policy compliance", "quarantine", "tamper", "behavioral"]):
            return "prevention_policy"

        if any(keyword in text for keyword in ["laporan detection", "detection report", "top detection", "ioa", "non-ioa", "command line"]):
            return "detection_report"

        if any(keyword in text for keyword in ["scorecard", "kpi", "metrics", "tren", "protection score"]):
            return "scorecard"

        if any(keyword in text for keyword in ["rekomendasi strategis", "matriks rekomendasi", "kesimpulan", "prioritas"]):
            return "strategic_recommendation"

        if any(keyword in text for keyword in ["what's new", "whats new", "fitur baru", "policy baru", "feature"]):
            return "whats_new"

        return None

    def build_report_section(self, section_key: str, customer_name: str = "Customer") -> Dict:
        template = PMReportTemplates.get_template(section_key, customer_name)
        template["generated_by"] = "rule-based-document-template"
        return template

    def build_document_summary(self, report_section: Dict) -> str:
        title = report_section.get("title", "Draft Dokumen")
        recommendations = report_section.get("recommendations", [])

        rec_text = ""
        if recommendations:
            rec_text = "\n".join([f"- {item}" for item in recommendations])

        return (
            f"Draft bagian dokumen berhasil dibuat: {title}\n\n"
            f"Bagian ini masih berupa template awal. Isi nilai numerik berdasarkan data customer dari CrowdStrike Console/MCP.\n\n"
            f"Rekomendasi pengisian:\n{rec_text}"
        )
