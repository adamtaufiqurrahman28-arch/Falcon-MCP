HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Seraphim MCP Search</title>

  <style>
    :root {
      --bg: #ffffff;
      --surface: #ffffff;
      --soft: #f8fafc;
      --soft-2: #f3f4f6;
      --line: #e5e7eb;
      --text: #0f172a;
      --muted: #64748b;
      --primary: #0f172a;
      --blue: #2563eb;
      --accent: #eff6ff;
      --accent-line: #bfdbfe;
      --warning: #fff7ed;
      --warning-line: #fdba74;
      --shadow: 0 8px 28px rgba(15, 23, 42, .05);
    }

    * { box-sizing: border-box; }

    html, body {
      margin: 0;
      padding: 0;
    }

    body {
      font-family: Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.45;
    }

    .page {
      max-width: 1360px;
      margin: 0 auto;
      padding: 40px 24px 48px;
    }

    .hero {
      text-align: center;
      margin-bottom: 28px;
    }

    .hero-logo {
      display: flex;
      justify-content: center;
      margin-bottom: 12px;
    }

    .hero-logo img {
      width: min(360px, 82vw);
      height: auto;
      display: block;
    }

    .eyebrow {
      font-size: 12px;
      letter-spacing: 2.6px;
      text-transform: uppercase;
      color: var(--muted);
      margin-bottom: 8px;
    }

    h1 {
      margin: 0;
      font-size: 30px;
      font-weight: 700;
      letter-spacing: -.02em;
    }

    .sub {
      margin: 10px auto 0;
      max-width: 580px;
      color: var(--muted);
      font-size: 14px;
    }

    .status-row {
      display: flex;
      justify-content: center;
      gap: 10px;
      flex-wrap: wrap;
      margin-top: 16px;
    }

    .status {
      font-size: 12px;
      border: 1px solid var(--accent-line);
      background: var(--accent);
      color: #1d4ed8;
      padding: 8px 12px;
      border-radius: 999px;
    }

    .status.warn {
      border-color: var(--warning-line);
      background: var(--warning);
      color: #c2410c;
    }

    .search-shell {
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: 24px;
      padding: 18px;
      box-shadow: var(--shadow);
      margin-bottom: 18px;
    }

    .search-row {
      display: flex;
      gap: 12px;
      align-items: center;
    }

    .search-input {
      flex: 1;
      min-width: 0;
      padding: 16px 18px;
      border: 1px solid #d7dde6;
      border-radius: 999px;
      background: #fff;
      font-size: 16px;
      color: var(--text);
      outline: none;
    }

    .search-input:focus {
      border-color: #93c5fd;
      box-shadow: 0 0 0 4px rgba(59, 130, 246, .10);
    }

    .search-btn {
      padding: 15px 22px;
      border: none;
      border-radius: 999px;
      background: var(--primary);
      color: white;
      font-size: 15px;
      font-weight: 700;
      cursor: pointer;
    }

    .controls {
      margin-top: 14px;
      display: flex;
      flex-direction: column;
      gap: 14px;
      align-items: center;
    }

    .mode-row {
      display: flex;
      align-items: center;
      gap: 10px;
      color: #475569;
      font-size: 14px;
    }

    .mode-label {
      font-weight: 700;
      color: #334155;
    }

    .switch {
      position: relative;
      width: 54px;
      height: 30px;
      display: inline-block;
    }

    .switch input {
      opacity: 0;
      width: 0;
      height: 0;
    }

    .slider {
      position: absolute;
      inset: 0;
      background: #9ca3af;
      border-radius: 999px;
      transition: .2s;
    }

    .slider:before {
      content: "";
      position: absolute;
      width: 24px;
      height: 24px;
      left: 3px;
      top: 3px;
      border-radius: 50%;
      background: #fff;
      transition: .2s;
    }

    input:checked + .slider {
      background: var(--primary);
    }

    input:checked + .slider:before {
      transform: translateX(24px);
    }

    .quick-actions {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      justify-content: center;
    }

    .chip {
      background: var(--soft-2);
      border: 1px solid transparent;
      border-radius: 999px;
      padding: 9px 14px;
      font-size: 13px;
      color: #1f2937;
      cursor: pointer;
    }

    .chip.outline {
      background: #fff;
      border-color: #cfd6e1;
    }

    .guide {
      display: none;
      width: 100%;
      max-width: 780px;
      border: 1px dashed #cbd5e1;
      background: var(--soft);
      border-radius: 16px;
      padding: 14px 16px;
      color: #475569;
      font-size: 13px;
    }

    .guide.active {
      display: block;
    }

    .guide strong {
      display: block;
      color: #0f172a;
      margin-bottom: 6px;
      font-size: 13px;
    }

    .guide ul {
      margin: 8px 0 0 18px;
      padding: 0;
    }

    .guide li {
      margin: 4px 0;
    }

    .investigation-card {
      width: 100%;
      max-width: 780px;
      border: 1px solid #dbe4f0;
      background:
        radial-gradient(circle at top left, rgba(37, 99, 235, .06), transparent 30%),
        #ffffff;
      border-radius: 18px;
      padding: 16px;
      color: #475569;
      font-size: 13px;
      box-shadow: 0 6px 18px rgba(15, 23, 42, .035);
    }

    .investigation-card-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 6px;
    }

    .investigation-card h2 {
      margin: 0;
      color: #0f172a;
      font-size: 16px;
    }

    .readonly-badge {
      display: inline-flex;
      align-items: center;
      width: fit-content;
      border: 1px solid #bfdbfe;
      background: #eff6ff;
      color: #1d4ed8;
      border-radius: 999px;
      padding: 5px 9px;
      font-size: 11px;
      font-weight: 700;
      white-space: nowrap;
    }

    .investigation-card p {
      margin: 6px 0 12px;
      color: #64748b;
    }

    .investigation-inline {
      display: flex;
      gap: 10px;
      align-items: center;
    }

    .investigation-inline .small-input {
      flex: 1;
      min-width: 0;
    }

    .investigation-inline .search-btn {
      padding: 11px 16px;
      font-size: 13px;
      white-space: nowrap;
    }

    .investigation-secondary {
      margin-top: 10px;
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      align-items: center;
    }

    @media (max-width: 760px) {
      .investigation-inline {
        flex-direction: column;
        align-items: stretch;
      }
    }

    .panel {
      display: none;
      margin-top: 16px;
      border-top: 1px solid var(--line);
      padding-top: 16px;
    }

    .panel.active {
      display: block;
    }

    .panel h2 {
      margin: 0 0 6px;
      font-size: 16px;
    }

    .muted {
      color: var(--muted);
      font-size: 13px;
    }

    .form-row {
      display: flex;
      gap: 10px;
      margin: 12px 0;
    }

    .small-input, textarea {
      width: 100%;
      border: 1px solid #d7dde6;
      border-radius: 14px;
      padding: 11px 12px;
      font-size: 14px;
      background: #fff;
      outline: none;
    }

    textarea {
      min-height: 120px;
      resize: vertical;
      font-family: Consolas, monospace;
      font-size: 13px;
    }

    .panel-actions {
      margin-top: 12px;
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      align-items: center;
    }

    .loading {
      display: none;
      margin: 14px 0 0;
      text-align: center;
      color: var(--muted);
      font-size: 13px;
    }

    .grid {
      display: grid;
      grid-template-columns: minmax(0, 1.55fr) minmax(360px, .85fr);
      gap: 18px;
      align-items: stretch;
    }

    .grid > .card,
    .grid > .side-stack {
      min-width: 0;
    }

    .grid > .card:first-child,
    .side-stack {
      min-height: 292px;
    }

    .summary-card {
      grid-column: 1 / -1;
    }

    .summary-card .card-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
    }

    .summary-card .card-header h2 {
      font-size: 18px;
    }

    .summary-badge {
      display: inline-flex;
      align-items: center;
      width: fit-content;
      border: 1px solid #bfdbfe;
      background: #eff6ff;
      color: #1d4ed8;
      border-radius: 999px;
      padding: 5px 10px;
      font-size: 12px;
      font-weight: 700;
    }

    .card {
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: 22px;
      box-shadow: var(--shadow);
      min-width: 0;
      overflow: hidden;
    }

    .card-header {
      padding: 18px 20px 0;
    }

    .card-header h2 {
      margin: 0;
      font-size: 20px;
    }

    .card-body {
      padding: 18px 20px 20px;
      min-width: 0;
      overflow: hidden;
    }

    /*
      Result table handling:
      - Page tidak ikut melebar.
      - Table di Result bisa di-scroll horizontal di dalam card.
      - Kolom panjang seperti detection id / cmdline tetap readable.
    */
    #resultBox {
      width: 100%;
      max-width: 100%;
      overflow-x: auto;
      overflow-y: hidden;
      padding-bottom: 8px;
    }

    .grid > .card:first-child .card-body {
      padding-left: 16px;
      padding-right: 16px;
    }

    #resultBox table {
      width: max-content;
      min-width: 1320px;
      table-layout: auto;
    }

    #resultBox th,
    #resultBox td {
      min-width: 120px;
      max-width: 280px;
      white-space: normal;
      overflow-wrap: anywhere;
      word-break: break-word;
      vertical-align: top;
    }

    #resultBox th:nth-child(2),
    #resultBox td:nth-child(2) {
      min-width: 360px;
      max-width: 520px;
    }

    #resultBox th:nth-child(9),
    #resultBox td:nth-child(9),
    #resultBox th:nth-child(10),
    #resultBox td:nth-child(10) {
      min-width: 260px;
      max-width: 460px;
    }

    #resultBox::-webkit-scrollbar {
      height: 10px;
    }

    #resultBox::-webkit-scrollbar-track {
      background: #f1f5f9;
      border-radius: 999px;
    }

    #resultBox::-webkit-scrollbar-thumb {
      background: #cbd5e1;
      border-radius: 999px;
    }

    #resultBox::-webkit-scrollbar-thumb:hover {
      background: #94a3b8;
    }

    .side-stack {
      display: flex;
      flex-direction: column;
      gap: 14px;
    }

    .side-stack .mini-card {
      flex: 1;
    }

    .mini-card {
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: 20px;
      padding: 16px;
      box-shadow: var(--shadow);
      min-width: 0;
      overflow: hidden;
    }

    .mini-card h3 {
      margin: 0 0 10px;
      font-size: 16px;
    }

    .summary-box {
      background:
        radial-gradient(circle at top left, rgba(37, 99, 235, .08), transparent 30%),
        linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
      border: 1px solid #dbe4f0;
      border-left: 5px solid #2563eb;
      border-radius: 18px;
      padding: 20px 22px;
      color: #334155;
      white-space: pre-line;
      font-size: 13px;
      line-height: 1.8;
      word-break: break-word;
      max-height: 560px;
      overflow-y: auto;
      box-shadow:
        inset 0 1px 0 rgba(255,255,255,.9),
        0 10px 28px rgba(15, 23, 42, .045);
    }

    .summary-box strong {
      color: #0f172a;
      font-weight: 800;
      background: #eff6ff;
      border: 1px solid #bfdbfe;
      border-radius: 8px;
      padding: 1px 5px;
    }

    .summary-box::-webkit-scrollbar {
      width: 8px;
    }

    .summary-box::-webkit-scrollbar-track {
      background: #f1f5f9;
      border-radius: 999px;
    }

    .summary-box::-webkit-scrollbar-thumb {
      background: #cbd5e1;
      border-radius: 999px;
    }

    .summary-box::-webkit-scrollbar-thumb:hover {
      background: #94a3b8;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }

    th, td {
      border: 1px solid var(--line);
      padding: 9px 10px;
      text-align: left;
      vertical-align: top;
    }

    th {
      background: var(--soft);
      color: #334155;
      font-weight: 700;
    }

    .mini-table th {
      width: 128px;
    }

    pre {
      margin: 0;
      background: #0f172a;
      color: #e5e7eb;
      border-radius: 14px;
      padding: 14px;
      font-size: 12px;
      overflow: auto;
      white-space: pre-wrap;
      max-height: 420px;
    }

    details {
      margin-top: 12px;
    }

    summary {
      cursor: pointer;
    }

    .footer {
      text-align: center;
      color: #94a3b8;
      font-size: 12px;
      margin-top: 22px;
    }

    @media (max-width: 960px) {
      .grid {
        grid-template-columns: 1fr;
      }
    }

    @media (max-width: 760px) {
      .page {
        padding: 28px 14px 36px;
      }

      .search-row, .form-row {
        flex-direction: column;
      }

      .search-btn {
        width: 100%;
      }

      h1 {
        font-size: 28px;
      }

      .search-shell, .card, .mini-card {
        border-radius: 18px;
      }
    }
  </style>
</head>

<body>
  <div class="page">
    <div class="hero">
      <div class="hero-logo">
        <img src="/static/img/seraphim-blueteam-logo.png" alt="Seraphim BlueTeam Logo" />
      </div>
      <div class="eyebrow">Seraphim BlueTeam</div>
      <h1>MCP Search</h1>
      <div class="sub" id="subtitleText">
        Minimal MCP client for CrowdStrike Falcon with clean search-first workflow.
      </div>

      <div class="status-row">
        <span class="status" id="serverStatus">Checking MCP server...</span>
        <span class="status warn" id="llmStatus">Checking LLM...</span>
      </div>
    </div>

    <div class="search-shell">
      <div class="search-row">
        <input
          id="promptInput"
          class="search-input"
          placeholder="Search hosts, detection, or query NGSIEM..."
          onkeydown="handleEnter(event)"
        />
        <button class="search-btn" onclick="sendPrompt()">Search</button>
      </div>

      <div class="controls">
        <div class="mode-row">
          <span>IF ELSE</span>
          <label class="switch">
            <input type="checkbox" id="modeToggle" onchange="updateModeUI()" />
            <span class="slider"></span>
          </label>
          <span>LLM Mode</span>
          <span class="mode-label" id="modeLabel">IF ELSE</span>
        </div>

        <div id="ruleQuickActions" class="quick-actions">
          <button class="chip" onclick="quickPrompt('cek koneksi')">check connection</button>
          <button class="chip" onclick="quickPrompt('list module aktif')">active module</button>
          <button class="chip" onclick="quickPrompt('cari host')">search host</button>
          <button class="chip" onclick="quickPrompt('cari detection')">search detection</button>
          <button class="chip" onclick="showDetectionReportPanel()">critical detection report</button>
          <button class="chip" onclick="showNgsiemPanel()">NGSIEM CQL</button>
          <button class="chip outline" onclick="loadTools()">see tools</button>
        </div>

        <div id="llmGuide" class="guide">
          <strong>Guide Prompt — LLM Mode</strong>
          Gunakan bahasa natural. LLM akan memahami prompt, memilih MCP tool, membuat FQL/CQL sederhana bila diperlukan, lalu merangkum hasil.
          <ul>
            <li>"Cari host Windows server yang last seen lebih dari 7 hari"</li>
            <li>"Cari detection high severity lalu jelaskan ringkas"</li>
            <li>"Cari aktivitas powershell 24 jam terakhir di NGSIEM"</li>
            <li>"Buatkan CQL untuk process execution yang mencurigakan"</li>
            <li>"Cari detail host dengan hostname ABC-SRV-01"</li>
          </ul>
        </div>

        <div id="investigationCard" class="investigation-card">
          <div class="investigation-card-header">
            <h2>Detection Investigation</h2>
            <span class="readonly-badge">Read-only workflow</span>
          </div>
          <p>
            Buat laporan investigasi dari Detection ID, atau cari detection critical terbaru.
            Panel ini tidak menjalankan containment, update status, RTR, atau aksi destructive.
          </p>

          <div class="investigation-inline">
            <input
              class="small-input"
              id="detectionIdInput"
              placeholder="Detection ID, contoh: ldt:xxxxxxxx"
              onkeydown="handleDetectionReportEnter(event)"
            />
            <button class="search-btn" onclick="runDetectionReport()">Generate Report</button>
          </div>

          <div class="investigation-secondary">
            <button class="chip outline" onclick="quickPrompt('Cari detection critical dan buatkan laporan investigasi status detection')">Search for Critical Detection</button>
          </div>
        </div>
      </div>

      <div class="loading" id="loading">Processing request...</div>

      <div class="panel" id="ngsiemPanel">
        <h2>NGSIEM CQL Query</h2>
        <div class="muted">
          Panel ini hanya untuk IF ELSE Mode. Di LLM Mode, cukup tulis prompt natural dan LLM akan membantu membuat CQL.
        </div>

        <div class="form-row">
          <input class="small-input" id="ngsiemStart" value="1h" placeholder="Time range: 30m, 1h, 1d, 7d" />
          <input class="small-input" id="ngsiemLimit" value="10000" placeholder="Limit" />
        </div>

        <textarea id="ngsiemQuery" placeholder="#event_simpleName=/Process/i">#event_simpleName=/Process/i</textarea>

        <div class="panel-actions">
          <button class="chip" onclick="setCql('#event_simpleName=/Process/i')">Process</button>
          <button class="chip" onclick="setCql('#event_simpleName=/Detection/i')">Detection</button>
          <button class="chip" onclick="setCql('#event_simpleName=/Network/i')">Network</button>
          <button class="search-btn" style="padding:10px 16px;" onclick="runNgsiemQuery()">Run NGSIEM Query</button>
        </div>
      </div>
    </div>

    <div class="grid">
      <div class="card">
        <div class="card-header">
          <h2>Result</h2>
        </div>
        <div class="card-body">
          <div id="resultBox" class="muted">The results will appear here.</div>
        </div>
      </div>

      <div class="side-stack">
        <div class="mini-card">
          <h3 id="selectedToolTitle">Selected Tool</h3>
          <div id="selectedTool" class="muted">There are no requests yet.</div>
        </div>

        <div class="mini-card">
          <h3>Available Tools</h3>
          <div id="toolsBox" class="muted">Click see tools to see the list of tools.</div>
        </div>
      </div>

      <div class="card summary-card">
        <div class="card-header">
          <h2 id="summaryTitle">Summary</h2>
          <span class="summary-badge">LLM Insight</span>
        </div>
        <div class="card-body">
          <div id="summaryBox" class="muted">The summary will appear here.</div>
        </div>
      </div>
    </div>

    <div class="footer">Seraphim BlueTeam MCP</div>
  </div>

  <script>
    function getMode() {
      return document.getElementById('modeToggle').checked ? 'llm' : 'rule';
    }

    function setLoading(value) {
      document.getElementById('loading').style.display = value ? 'block' : 'none';
    }

    function handleEnter(event) {
      if (event.key === 'Enter') sendPrompt();
    }

    function escapeHtml(value) {
      return String(value)
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#039;');
    }

    function updateModeUI() {
      const isLLM = getMode() === 'llm';

      document.getElementById('modeLabel').innerText = isLLM ? 'LLM Mode' : 'IF ELSE';
      document.getElementById('subtitleText').innerText = isLLM
        ? 'Natural-language mode for FQL, CQL, MCP tool selection, and CrowdStrike result summaries.'
        : 'Minimal MCP client for CrowdStrike Falcon with clean search-first workflow.';

      document.getElementById('promptInput').placeholder = isLLM
        ? 'Tulis prompt natural... contoh: Cari aktivitas powershell 24 jam terakhir'
        : 'Search hosts, detection, or query NGSIEM...';

      document.getElementById('ruleQuickActions').style.display = isLLM ? 'none' : 'flex';
      document.getElementById('llmGuide').classList.toggle('active', isLLM);

      // Important request:
      // Saat LLM Mode aktif, panel query manual tidak ditampilkan.
      if (isLLM) {
        document.getElementById('ngsiemPanel').classList.remove('active');
      }

      document.getElementById('selectedToolTitle').innerText = isLLM ? 'LLM Tool Selection' : 'Selected Tool';
      document.getElementById('summaryTitle').innerText = isLLM ? 'LLM Summary' : 'Summary';
    }

    function showNgsiemPanel() {
      if (getMode() === 'llm') return;
      document.getElementById('ngsiemPanel').classList.add('active');
      document.getElementById('promptInput').value = 'query ngsiem';
    }

    function showDetectionReportPanel() {
      document.getElementById('ngsiemPanel').classList.remove('active');
      document.getElementById('promptInput').value = 'Cari detection critical dan buatkan laporan investigasi status detection';
      document.getElementById('summaryTitle').innerText = 'Detection Investigation Report';

      const card = document.getElementById('investigationCard');
      if (card) {
        card.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }

      document.getElementById('detectionIdInput')?.focus();
    }

    function handleDetectionReportEnter(event) {
      if (event.key === 'Enter') runDetectionReport();
    }

    function runDetectionReport() {
      const detectionId = document.getElementById('detectionIdInput').value.trim();

      if (!detectionId) {
        alert('Detection ID wajib diisi untuk membuat report detail.');
        return;
      }

      document.getElementById('promptInput').value = `buatkan laporan detail detection ${detectionId}`;
      document.getElementById('summaryTitle').innerText = 'Detection Investigation Report';
      sendPrompt();
    }

    function isDetectionReportPrompt(prompt) {
      const value = String(prompt || '').toLowerCase();

      return (
        (value.includes('detection') || value.includes('alert') || value.includes('ldt:')) &&
        (
          value.includes('report') ||
          value.includes('laporan') ||
          value.includes('investigasi') ||
          value.includes('investigation') ||
          value.includes('analisa') ||
          value.includes('analysis') ||
          value.includes('status') ||
          value.includes('detail')
        )
      );
    }

    function quickPrompt(text) {
      document.getElementById('promptInput').value = text;
      sendPrompt();
    }

    function setCql(query) {
      document.getElementById('ngsiemQuery').value = query;
    }

    function getFormData() {
      return {
        cql_query: document.getElementById('ngsiemQuery')?.value?.trim() || '',
        start: document.getElementById('ngsiemStart')?.value?.trim() || '1h',
        limit: document.getElementById('ngsiemLimit')?.value?.trim() || '10000'
      };
    }

    function runNgsiemQuery() {
      const cql = document.getElementById('ngsiemQuery').value.trim();
      if (!cql) {
        alert('CQL Query wajib diisi untuk NGSIEM.');
        return;
      }

      document.getElementById('promptInput').value = 'query ngsiem ' + cql;
      sendPrompt();
    }


    function parseCqlTableColumns(queryString) {
      if (!queryString) return [];

      const match = String(queryString).match(/table\s*\(\s*\[([^\]]+)\]\s*\)/i);
      if (!match) return [];

      return match[1]
        .split(',')
        .map(item => item.trim())
        .filter(Boolean);
    }

    function buildRawColumns(rows, preferredOrder = []) {
      const seen = new Set();
      const columns = [];

      // Use CQL table([...]) order first, only if the field exists in at least one row.
      preferredOrder.forEach(key => {
        const exists = rows.some(row => row && Object.prototype.hasOwnProperty.call(row, key));
        if (exists && !seen.has(key)) {
          seen.add(key);
          columns.push(key);
        }
      });

      // Then follow raw JSON key order as it appears in the response.
      rows.slice(0, 50).forEach(row => {
        if (!row || typeof row !== 'object' || Array.isArray(row)) return;

        Object.keys(row).forEach(key => {
          if (!seen.has(key)) {
            seen.add(key);
            columns.push(key);
          }
        });
      });

      // Keep it readable but still flexible.
      return columns.slice(0, 24);
    }

    function renderRawDynamicTable(rows, preferredOrder = [], emptyMessage = 'Tidak ada data.') {
      if (!rows || rows.length === 0) {
        return `<p class="muted">${emptyMessage}</p>`;
      }

      const columns = buildRawColumns(rows, preferredOrder);

      if (!columns || columns.length === 0) {
        return `<p class="muted">${emptyMessage}</p>`;
      }

      let html = '<div style="overflow-x:auto;">';
      html += '<table><thead><tr>';

      columns.forEach(column => {
        html += `<th>${escapeHtml(column)}</th>`;
      });

      html += '</tr></thead><tbody>';

      rows.slice(0, 100).forEach(row => {
        html += '<tr>';

        columns.forEach(column => {
          let value = row?.[column];

          if (value === undefined || value === null || value === '') {
            value = '-';
          } else if (typeof value === 'object') {
            value = JSON.stringify(value);
          }

          html += `<td>${escapeHtml(value).slice(0, 500)}</td>`;
        });

        html += '</tr>';
      });

      html += '</tbody></table></div>';

      return html;
    }

    function parseJsonStringMaybe(value) {
      if (typeof value !== 'string') return value;

      const trimmed = value.trim();

      if (
        (trimmed.startsWith('{') && trimmed.endsWith('}')) ||
        (trimmed.startsWith('[') && trimmed.endsWith(']'))
      ) {
        try {
          return JSON.parse(trimmed);
        } catch (error) {
          return value;
        }
      }

      return value;
    }


    function renderTable(rows) {
      if (!rows || rows.length === 0) return '<p class="muted">Tidak ada data.</p>';

      const keys = Object.keys(rows[0]).slice(0, 8);
      let html = '<table><thead><tr>';
      keys.forEach(key => html += `<th>${escapeHtml(key)}</th>`);
      html += '</tr></thead><tbody>';

      rows.slice(0, 50).forEach(row => {
        html += '<tr>';
        keys.forEach(key => {
          let value = row[key];
          if (typeof value === 'object') value = JSON.stringify(value);
          html += `<td>${escapeHtml(value ?? '-').slice(0, 240)}</td>`;
        });
        html += '</tr>';
      });

      html += '</tbody></table>';
      return html;
    }

    function renderHostTable(rows) {
      if (!rows || rows.length === 0) return '<p class="muted">Tidak ada host ditemukan.</p>';

      const keys = [
        'hostname',
        'device_id',
        'aid',
        'platform_name',
        'os_version',
        'agent_version',
        'last_seen',
        'local_ip',
        'external_ip',
        'status'
      ];

      let html = '<table><thead><tr>';
      keys.forEach(key => html += `<th>${escapeHtml(key)}</th>`);
      html += '</tr></thead><tbody>';

      rows.slice(0, 50).forEach(row => {
        html += '<tr>';
        keys.forEach(key => {
          let value = row[key];

          if (value === undefined && key === 'hostname') value = row.hostname || row.computer_name || row.device_name;
          if (value === undefined && key === 'device_id') value = row.device_id || row.aid || row.id;
          if (value === undefined && key === 'agent_version') value = row.agent_version || row.sensor_version;

          if (typeof value === 'object') value = JSON.stringify(value);
          html += `<td>${escapeHtml(value ?? '-').slice(0, 180)}</td>`;
        });
        html += '</tr>';
      });

      html += '</tbody></table>';
      return html;
    }

    function renderDetectionTable(rows) {
      if (!rows || rows.length === 0) return '<p class="muted">Tidak ada detection ditemukan.</p>';

      const keys = [
        'detection_id',
        'id',
        'hostname',
        'severity',
        'status',
        'tactic',
        'technique',
        'filename',
        'cmdline',
        'created_timestamp'
      ];

      let html = '<table><thead><tr>';
      keys.forEach(key => html += `<th>${escapeHtml(key)}</th>`);
      html += '</tr></thead><tbody>';

      rows.slice(0, 50).forEach(row => {
        html += '<tr>';
        keys.forEach(key => {
          let value = row[key];

          if (value === undefined && key === 'hostname') value = row.hostname || row.device?.hostname || row.device_name;
          if (value === undefined && key === 'filename') value = row.filename || row.file_name || row.behaviors?.[0]?.filename;
          if (value === undefined && key === 'cmdline') value = row.cmdline || row.command_line || row.behaviors?.[0]?.cmdline;

          if (typeof value === 'object') value = JSON.stringify(value);
          html += `<td>${escapeHtml(value ?? '-').slice(0, 220)}</td>`;
        });
        html += '</tr>';
      });

      html += '</tbody></table>';
      return html;
    }

    function renderNgsiemTable(rows, queryString = '') {
      const cqlColumns = parseCqlTableColumns(queryString);

      return renderRawDynamicTable(
        rows,
        cqlColumns,
        'Tidak ada event ditemukan.'
      );
    }

    function normalizeResultToRows(payload) {
      const result = payload.result || [];
      let rows = [];

      function pushRowsFromValue(value) {
        value = parseJsonStringMaybe(value);

        if (Array.isArray(value)) {
          value.forEach(item => {
            if (item && typeof item === 'object' && !Array.isArray(item)) {
              rows.push(item);
            } else {
              rows.push({ value: item });
            }
          });
          return;
        }

        if (value && typeof value === 'object') {
          const candidateKeys = [
            'resources',
            'items',
            'data',
            'results',
            'hosts',
            'detections',
            'events',
            'rows'
          ];

          for (const key of candidateKeys) {
            if (Array.isArray(value[key])) {
              value[key].forEach(item => {
                if (item && typeof item === 'object' && !Array.isArray(item)) {
                  rows.push(item);
                } else {
                  rows.push({ value: item });
                }
              });
              return;
            }
          }

          // Preserve raw object keys exactly if there is no known container.
          rows.push(value);
          return;
        }

        rows.push({ output: value });
      }

      result.forEach(item => {
        if (item && typeof item === 'object' && Object.prototype.hasOwnProperty.call(item, 'data')) {
          pushRowsFromValue(item.data);
        } else {
          pushRowsFromValue(item);
        }
      });

      return rows;
    }

    function renderResultByType(data) {
      const rows = normalizeResultToRows(data);
      const type = data.result_type || 'generic';

      if (type === 'host') return renderHostTable(rows);
      if (type === 'detection') return renderDetectionTable(rows);
      if (type === 'ngsiem') {
        return renderNgsiemTable(rows, data.arguments?.query_string || '');
      }

      return renderRawDynamicTable(rows, [], 'Tidak ada data.');
    }

    async function healthCheck() {
      try {
        const response = await fetch('/api/health');
        const data = await response.json();

        document.getElementById('serverStatus').innerText = `MCP Server: ${data.mcp_server_url}`;

        if (data.llm_ready) {
          document.getElementById('llmStatus').innerText = `LLM: Ready (${data.openai_model})`;
          document.getElementById('llmStatus').className = 'status';
        } else {
          document.getElementById('llmStatus').innerText = 'LLM: Not Ready';
          document.getElementById('llmStatus').className = 'status warn';
        }
      } catch (error) {
        document.getElementById('serverStatus').innerText = 'Server check failed';
      }
    }

    async function loadTools() {
      setLoading(true);

      try {
        const response = await fetch('/api/tools');
        const data = await response.json();

        if (!response.ok) throw new Error(data.detail || 'Gagal mengambil tools');

        document.getElementById('toolsBox').innerHTML = renderTable(
          data.tools.map(t => ({
            name: t.name,
            description: t.description
          }))
        );
      } catch (error) {
        document.getElementById('toolsBox').innerHTML = `<pre>${escapeHtml(error.message)}</pre>`;
      } finally {
        setLoading(false);
      }
    }

    async function sendPrompt() {
      const prompt = document.getElementById('promptInput').value.trim();
      const mode = getMode();

      if (!prompt) return;

      const reportMode = isDetectionReportPrompt(prompt);
      document.getElementById('summaryTitle').innerText = reportMode
        ? 'Detection Investigation Report'
        : (mode === 'llm' ? 'LLM Summary' : 'Summary');

      // IF ELSE only: show manual NGSIEM panel when needed.
      // LLM mode should not show manual query panel.
      if (
        mode === 'rule' &&
        (prompt.toLowerCase().includes('ngsiem') || prompt.toLowerCase().includes('cql'))
      ) {
        document.getElementById('ngsiemPanel').classList.add('active');
      }

      if (mode === 'llm') {
        document.getElementById('ngsiemPanel').classList.remove('active');
      }

      setLoading(true);
      document.getElementById('selectedTool').innerHTML = 'Running request...';
      document.getElementById('summaryBox').innerHTML = 'Waiting response...';
      document.getElementById('resultBox').innerHTML = '';

      try {
        const response = await fetch('/api/prompt', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            prompt,
            mode,
            form_data: getFormData()
          })
        });

        const data = await response.json();

        if (!response.ok) throw new Error(data.detail || 'Request gagal');

        if (data.requires_input && data.required_input_type === 'cql') {
          if (mode === 'rule') showNgsiemPanel();
          throw new Error(data.error || 'NGSIEM membutuhkan CQL Query.');
        }

        if (data.error) throw new Error(data.message || data.error);

        document.getElementById('selectedTool').innerHTML = `
          <table class="mini-table">
            <tr><th>Prompt</th><td>${escapeHtml(data.prompt)}</td></tr>
            <tr><th>Mode</th><td>${escapeHtml(data.mode)}</td></tr>
            <tr><th>Tool</th><td>${escapeHtml(data.tool)}</td></tr>
            <tr><th>Selected By</th><td>${escapeHtml(data.selected_by || '-')}</td></tr>
            <tr><th>Reason</th><td>${escapeHtml(data.reason || '-')}</td></tr>
          </table>
          <details>
            <summary class="muted">Arguments</summary>
            <pre>${escapeHtml(JSON.stringify(data.arguments, null, 2))}</pre>
          </details>
        `;

        document.getElementById('summaryBox').innerHTML =
          `<div class="summary-box">${escapeHtml(data.summary || 'Tidak ada summary.')}</div>`;

        document.getElementById('resultBox').innerHTML =
          renderResultByType(data) +
          `<details><summary class="muted">Raw JSON</summary><pre>${escapeHtml(JSON.stringify(data, null, 2))}</pre></details>`;
      } catch (error) {
        document.getElementById('selectedTool').innerHTML = '<span class="muted">Error</span>';
        document.getElementById('summaryBox').innerHTML = '<span class="muted">Tidak ada summary.</span>';
        document.getElementById('resultBox').innerHTML = `<pre>${escapeHtml(error.message)}</pre>`;
      } finally {
        setLoading(false);
      }
    }

    healthCheck();
    updateModeUI();
  </script>
</body>
</html>
"""
