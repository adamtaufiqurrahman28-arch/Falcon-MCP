# Seraphim Digital Technology MCP - PM Assistant Enhanced

Modular web client untuk demo koneksi ke `falcon-mcp` server dan membantu penyusunan draft dokumen Preventive Maintenance & Health Check CrowdStrike Falcon.

Enhancement utama:
- IF ELSE Mode sekarang bukan cuma query keyword, tapi juga bisa membuat draft bagian dokumen PM.
- LLM Mode tetap tersedia untuk OpenAI jika sudah diaktifkan.
- Draft dokumen PM bisa langsung dicopy ke laporan.
- Pupuk Kaltim hanya sample format, bukan hardcoded customer.

## Struktur

```text
seraphim-mcp-pm-enhanced/
├── app/
│   ├── main.py
│   ├── core/config.py
│   ├── models/schemas.py
│   ├── services/mcp_service.py
│   ├── services/prompt_router.py
│   ├── services/llm_service.py
│   ├── services/llm_router.py
│   ├── services/report_templates.py
│   ├── services/report_assistant.py
│   ├── api/routes.py
│   └── web/templates.py
├── requirements.txt
├── .env.example
└── README.md
```

## Setup

```powershell
cd seraphim-mcp-pm-enhanced
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Edit `.env`:

```env
MCP_SERVER_URL=
APP_NAME=Seraphim Digital Technology MCP
APP_ENV=development
DEFAULT_LIMIT=10

LLM_ENABLED=false
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
```

## Run

```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8080
```

Buka:

```text
http://127.0.0.1:8080
```

## Prompt IF ELSE untuk dokumen PM

```text
buat ringkasan eksekutif
buat sensor health
buat prevention policy
buat laporan detection
buat scorecard
buat rekomendasi strategis
buat fitur baru
```

## Prompt IF ELSE untuk MCP Tool

```text
cari host
cari detection
cari incident
cek log ngsiem
```

## Catatan

- Mode IF ELSE bisa jalan tanpa OpenAI API.
- LLM Mode butuh `LLM_ENABLED=true` dan `OPENAI_API_KEY`.
- Draft template masih perlu angka aktual dari data customer.

# Seraphim Digital Technology MCP - PM Assistant Enhanced

Modular web client untuk demo koneksi ke `falcon-mcp` server dan membantu penyusunan draft dokumen Preventive Maintenance & Health Check CrowdStrike Falcon.

Enhancement utama:
- IF ELSE Mode sekarang bukan cuma query keyword, tapi juga bisa membuat draft bagian dokumen PM.
- LLM Mode tetap tersedia untuk OpenAI jika sudah diaktifkan.
- Draft dokumen PM bisa langsung dicopy ke laporan.
- Pupuk Kaltim hanya sample format, bukan hardcoded customer.

## Struktur

```text
seraphim-mcp-pm-enhanced/
├── app/
│   ├── main.py
│   ├── core/config.py
│   ├── models/schemas.py
│   ├── services/mcp_service.py
│   ├── services/prompt_router.py
│   ├── services/llm_service.py
│   ├── services/llm_router.py
│   ├── services/report_templates.py
│   ├── services/report_assistant.py
│   ├── api/routes.py
│   └── web/templates.py
├── requirements.txt
├── .env.example
└── README.md
```

## Setup

```powershell
cd seraphim-mcp-pm-enhanced
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Edit `.env`:

```env
MCP_SERVER_URL=http://103.93.129.20:8000/mcp
APP_NAME=Seraphim Digital Technology MCP
APP_ENV=development
DEFAULT_LIMIT=10

LLM_ENABLED=false
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
```

## Run

```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8080
```

Buka:

```text
http://127.0.0.1:8080
```

## Prompt IF ELSE untuk dokumen PM

```text
buat ringkasan eksekutif
buat sensor health
buat prevention policy
buat laporan detection
buat scorecard
buat rekomendasi strategis
buat fitur baru
```

## Prompt IF ELSE untuk MCP Tool

```text
cari host
cari detection
cari incident
cek log ngsiem
```

## Catatan

- Mode IF ELSE bisa jalan tanpa OpenAI API.
- LLM Mode butuh `LLM_ENABLED=true` dan `OPENAI_API_KEY`.
- Draft template masih perlu angka aktual dari data customer.
#
