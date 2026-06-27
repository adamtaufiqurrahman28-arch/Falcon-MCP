from typing import Dict, List


class PMReportTemplates:
    """
    Template berbasis struktur dokumen Preventive Maintenance & Health Check.
    Dibuat generic untuk semua customer.
    """

    @staticmethod
    def executive_summary(customer_name: str = "Customer") -> Dict:
        return {
            "section": "1. Ringkasan Eksekutif",
            "title": "Ringkasan Eksekutif",
            "draft": f"""Laporan ini merupakan bagian dari siklus Preventive Maintenance dan Health Check CrowdStrike Falcon untuk {customer_name}. Pemeriksaan ini bertujuan untuk memberikan gambaran kondisi platform, status kesehatan sensor, efektivitas kebijakan prevention, status detection/incident, serta rekomendasi prioritas yang dapat digunakan sebagai dasar peningkatan postur keamanan.

Secara umum, environment {customer_name} perlu dievaluasi melalui beberapa indikator utama, yaitu sensor coverage, sensor health, detection response, prevention policy compliance, serta status modul tambahan seperti Spotlight, Discover, Device Control, Firewall Management, dan Falcon Next-Gen SIEM apabila digunakan.

Hasil pemeriksaan dari CrowdStrike Falcon perlu dikaitkan dengan dampak bisnis agar rekomendasi tidak hanya bersifat teknis, tetapi juga mendukung peningkatan visibilitas, pengurangan blind spot, percepatan respons insiden, dan kesiapan operasional security team.""",
            "tables": [
                {"Parameter": "Total Lisensi", "Nilai": "[isi dari data customer]", "Catatan": "Total entitlement CrowdStrike"},
                {"Parameter": "Sensor Aktif", "Nilai": "[isi dari Host Management]", "Catatan": "Jumlah endpoint/server aktif"},
                {"Parameter": "Total Detection", "Nilai": "[isi dari Detection]", "Catatan": "Total detection periode PM"},
                {"Parameter": "Detection New", "Nilai": "[isi dari Detection Status]", "Catatan": "Perlu triage"},
                {"Parameter": "Sensor RFM/Unsupported", "Nilai": "[isi dari Sensor Health]", "Catatan": "Perlu validasi/upgrade"},
            ],
            "recommendations": [
                "Validasi data lisensi dan sensor aktif untuk menghitung coverage aktual.",
                "Prioritaskan endpoint/server kritikal yang belum memiliki sensor.",
                "Tinjau detection berstatus New/In Progress agar tidak menjadi backlog.",
                "Pastikan sensor unsupported dan RFM memiliki rencana tindak lanjut.",
            ],
        }

    @staticmethod
    def sensor_health(customer_name: str = "Customer") -> Dict:
        return {
            "section": "4. Sensor Health Check",
            "title": "Sensor Health Check",
            "draft": f"""Sensor CrowdStrike Falcon pada environment {customer_name} perlu dipantau secara berkala untuk memastikan seluruh endpoint dan server tetap memiliki perlindungan yang optimal. Fokus utama pada bagian ini meliputi jumlah sensor aktif, versi sensor, sensor unsupported, kondisi RFM, serta sensor yang tidak aktif dalam periode tertentu.

Sensor dengan status unsupported atau RFM berpotensi menurunkan efektivitas proteksi karena host dapat kehilangan sebagian kemampuan deteksi/pencegahan. Oleh karena itu, host dengan kondisi tersebut perlu divalidasi berdasarkan platform, OS/kernel version, sensor version, dan last seen.

Apabila ditemukan sensor tidak aktif, perlu dilakukan validasi apakah aset tersebut masih digunakan, sedang dalam maintenance, decommissioned, atau mengalami gangguan konektivitas.""",
            "tables": [
                {"Kategori": "Total Sensor Aktif", "Nilai": "[isi]", "Aksi": "Validasi terhadap total endpoint/server"},
                {"Kategori": "Unsupported Sensor", "Nilai": "[isi]", "Aksi": "Upgrade sensor atau tuning update policy"},
                {"Kategori": "RFM", "Nilai": "[isi]", "Aksi": "Cek OS/kernel compatibility dan sensor version"},
                {"Kategori": "Inactive Sensor >14 hari", "Nilai": "[isi]", "Aksi": "Validasi aset dan konektivitas"},
            ],
            "recommendations": [
                "Prioritaskan upgrade sensor unsupported pada server atau endpoint kritikal.",
                "Untuk RFM Windows setelah patching, lakukan monitoring dan validasi ulang.",
                "Untuk RFM Linux, cek kernel/OS support matrix dan rencanakan upgrade OS/kernel atau sensor.",
                "Pertahankan monitoring inactive sensor agar coverage tetap optimal.",
            ],
        }

    @staticmethod
    def prevention_policy(customer_name: str = "Customer") -> Dict:
        return {
            "section": "5. Ringkasan Prevention Policy",
            "title": "Ringkasan Prevention Policy",
            "draft": f"""Prevention Policy pada CrowdStrike Falcon berperan penting dalam menentukan bagaimana platform melakukan deteksi, pencegahan, quarantine, dan perlindungan terhadap sensor tampering. Pada environment {customer_name}, evaluasi policy perlu dilakukan untuk membandingkan konfigurasi aktual dengan baseline best practice yang disepakati.

Gap pada prevention policy dapat meningkatkan risiko terhadap malware execution, behavior-based attack, file berbahaya yang tidak langsung dikarantina, serta upaya melemahkan sensor. Oleh karena itu, tuning policy perlu dilakukan secara bertahap untuk menghindari false positive dan gangguan operasional.

Evaluasi awal disarankan difokuskan pada policy yang paling banyak digunakan dan policy yang melindungi server atau endpoint kritikal.""",
            "tables": [
                {"Item": "Cloud Based Anti-malware Prevention", "Best Practice": "Moderate++", "Risiko Jika Gap": "Malware modern berpotensi tidak dicegah optimal"},
                {"Item": "Sensor Based Anti-malware Prevention", "Best Practice": "Moderate++", "Risiko Jika Gap": "Proteksi endpoint kurang agresif"},
                {"Item": "Behavioral Detection", "Best Practice": "Moderate++", "Risiko Jika Gap": "Living-off-the-land activity terlambat terdeteksi"},
                {"Item": "Quarantine on Write", "Best Practice": "ON", "Risiko Jika Gap": "File berbahaya tetap tersimpan di disk"},
                {"Item": "Sensor Tamper Prevention", "Best Practice": "ON", "Risiko Jika Gap": "Sensor dapat dilemahkan oleh attacker"},
            ],
            "recommendations": [
                "Lakukan tuning bertahap dimulai dari pilot policy.",
                "Aktifkan fitur prevention yang berdampak tinggi terlebih dahulu.",
                "Monitor false positive setelah perubahan policy.",
                "Dokumentasikan setiap perubahan policy dan hasil validasinya.",
            ],
        }

    @staticmethod
    def detection_report(customer_name: str = "Customer") -> Dict:
        return {
            "section": "8. Laporan Detection",
            "title": "Laporan Detection",
            "draft": f"""Bagian ini menyajikan ringkasan detection yang tercatat pada CrowdStrike Falcon untuk environment {customer_name}. Analisis detection perlu melihat jumlah total detection, status penanganan, severity, host penghasil detection terbanyak, tactic/technique MITRE ATT&CK, file name, dan command line yang paling sering muncul.

Detection dengan severity tinggi atau jumlah kemunculan besar perlu diprioritaskan untuk validasi. Namun demikian, tidak semua detection dapat langsung disimpulkan sebagai true positive. Beberapa detection dapat berasal dari aplikasi legitimate, dual AV, software tidak standar, atau aktivitas administratif yang memerlukan pengecekan lanjutan.

Tujuan utama bagian ini adalah memastikan detection tidak hanya dicatat, tetapi juga memiliki tindak lanjut yang jelas, baik berupa closure, exception, containment, maupun rekomendasi perbaikan.""",
            "tables": [
                {"Area": "Total Detection", "Nilai": "[isi]", "Tindakan": "Lihat tren dibanding PM sebelumnya"},
                {"Area": "Detection New", "Nilai": "[isi]", "Tindakan": "Prioritaskan triage"},
                {"Area": "In Progress", "Nilai": "[isi]", "Tindakan": "Pastikan ada PIC dan target closure"},
                {"Area": "Top Host", "Nilai": "[isi]", "Tindakan": "Investigasi host dengan count tertinggi"},
                {"Area": "Top Command Line", "Nilai": "[isi]", "Tindakan": "Validasi konteks parent-child process"},
            ],
            "recommendations": [
                "Prioritaskan detection dengan severity Critical/High.",
                "Validasi apakah detection bersifat true positive atau false positive.",
                "Buat exception hanya untuk aplikasi yang sudah tervalidasi aman dan memiliki justifikasi bisnis.",
                "Pastikan detection berstatus In Progress memiliki target penyelesaian.",
            ],
        }

    @staticmethod
    def scorecard(customer_name: str = "Customer") -> Dict:
        return {
            "section": "7. Security KPI, Metrics & Tren",
            "title": "Coverage & Protection Scorecard",
            "draft": f"""Scorecard digunakan untuk memberikan penilaian terukur terhadap kondisi keamanan CrowdStrike Falcon di environment {customer_name}. Penilaian ini bukan nilai resmi dari CrowdStrike, melainkan metode internal untuk membantu customer memahami area yang sudah baik dan area yang masih perlu peningkatan.

Area yang umum dinilai meliputi sensor coverage, sensor health, detection response, policy compliance, vulnerability posture, asset hygiene, dan SLA layanan. Setiap area dapat diberi bobot sesuai dampaknya terhadap risiko bisnis.

Dengan scorecard, rekomendasi perbaikan dapat disusun lebih objektif dan diprioritaskan berdasarkan gap terbesar terhadap target.""",
            "tables": [
                {"Area": "Sensor Coverage", "Formula": "Active Hosts / Total Lisensi x 100%", "Target": ">98%"},
                {"Area": "Sensor Health", "Formula": "1 - (RFM / Active Hosts)", "Target": ">98%"},
                {"Area": "Detection Response", "Formula": "(Total Detection - New) / Total Detection x 100%", "Target": ">95%"},
                {"Area": "Policy Compliance", "Formula": "Item sesuai / total item", "Target": ">90%"},
                {"Area": "Vulnerability Posture", "Formula": "Critical/High open risk review", "Target": "Risk-based remediation"},
            ],
            "recommendations": [
                "Gunakan scorecard untuk memprioritaskan perbaikan lintas area.",
                "Tampilkan tren antar periode PM agar customer melihat progress.",
                "Berikan target realistis dan PIC untuk setiap area yang masih rendah.",
            ],
        }

    @staticmethod
    def strategic_recommendation(customer_name: str = "Customer") -> Dict:
        return {
            "section": "11. Kesimpulan dan Rekomendasi Strategis",
            "title": "Matriks Rekomendasi Terprioritas",
            "draft": f"""Berdasarkan hasil Preventive Maintenance dan Health Check, rekomendasi untuk {customer_name} perlu disusun berdasarkan prioritas risiko, dampak bisnis, dan effort implementasi. Rekomendasi tidak hanya mencakup temuan teknis, tetapi juga target waktu dan PIC agar dapat ditindaklanjuti secara operasional.

Secara umum, prioritas utama biasanya mencakup peningkatan sensor coverage, penanganan sensor unsupported/RFM, tuning prevention policy, review detection, dan validasi modul tambahan seperti Spotlight, Discover, Device Control, Firewall, atau NGSIEM sesuai scope customer.

Setiap rekomendasi perlu memiliki alasan bisnis agar stakeholder memahami mengapa tindakan tersebut penting untuk mengurangi blind spot, meningkatkan deteksi, dan mempercepat respons insiden.""",
            "tables": [
                {"Prioritas": "Tinggi", "Area": "Sensor Coverage", "Tindakan": "Onboarding endpoint/server prioritas", "Target": "30-60 hari"},
                {"Prioritas": "Tinggi", "Area": "Sensor Unsupported/RFM", "Tindakan": "Upgrade sensor atau validasi OS/kernel", "Target": "14-30 hari"},
                {"Prioritas": "Tinggi", "Area": "Prevention Policy", "Tindakan": "Tuning bertahap sesuai best practice", "Target": "30-60 hari"},
                {"Prioritas": "Sedang", "Area": "Detection Management", "Tindakan": "Review backlog dan top recurring detection", "Target": "Berkala"},
                {"Prioritas": "Sedang", "Area": "Module Adoption", "Tindakan": "Evaluasi fitur baru/modul tambahan", "Target": "Siklus PM berikutnya"},
            ],
            "recommendations": [
                "Gunakan matriks prioritas agar tindakan lebih mudah diterima customer.",
                "Pisahkan rekomendasi immediate, short-term, dan next PM cycle.",
                "Pastikan rekomendasi memiliki dampak bisnis dan target waktu.",
            ],
        }

    @staticmethod
    def whats_new(customer_name: str = "Customer") -> Dict:
        return {
            "section": "2. What's New – CrowdStrike Falcon",
            "title": "What's New – CrowdStrike Falcon",
            "draft": f"""Bagian ini digunakan untuk mencatat pembaruan fitur CrowdStrike Falcon yang relevan untuk {customer_name}. Fitur baru tidak harus langsung diaktifkan, namun perlu dievaluasi apakah memiliki dampak terhadap deployment sensor, visibility, exposure management, investigasi, otomasi, atau pelaporan.

Setiap fitur baru perlu diklasifikasikan sebagai Direkomendasikan, Belum Dievaluasi, atau Tidak Relevan agar customer memahami mana yang perlu ditindaklanjuti dan mana yang cukup dicatat sebagai informasi platform.""",
            "tables": [
                {"Fitur": "Monitor Deployment", "Status": "Direkomendasikan", "Catatan": "Membantu monitoring rollout sensor"},
                {"Fitur": "LogScale Collector Policies", "Status": "Belum Dievaluasi", "Catatan": "Relevan jika ada forwarding log/NGSIEM"},
                {"Fitur": "Asset Criticality Rules", "Status": "Direkomendasikan", "Catatan": "Membantu prioritas aset kritikal"},
                {"Fitur": "Scheduled Dashboard Reports", "Status": "Direkomendasikan", "Catatan": "Mendukung laporan berkala"},
                {"Fitur": "Unified Content Library", "Status": "Direkomendasikan", "Catatan": "Mempercepat use case SIEM/automation"},
            ],
            "recommendations": [
                "Evaluasi fitur baru setiap siklus PM.",
                "Prioritaskan fitur yang berdampak langsung pada operasi security.",
                "Lakukan pilot sebelum aktivasi luas jika ada risiko false positive atau gangguan operasional.",
            ],
        }

    @staticmethod
    def get_template(section_key: str, customer_name: str = "Customer") -> Dict:
        mapping = {
            "executive_summary": PMReportTemplates.executive_summary,
            "sensor_health": PMReportTemplates.sensor_health,
            "prevention_policy": PMReportTemplates.prevention_policy,
            "detection_report": PMReportTemplates.detection_report,
            "scorecard": PMReportTemplates.scorecard,
            "strategic_recommendation": PMReportTemplates.strategic_recommendation,
            "whats_new": PMReportTemplates.whats_new,
        }
        func = mapping.get(section_key, PMReportTemplates.executive_summary)
        return func(customer_name)
