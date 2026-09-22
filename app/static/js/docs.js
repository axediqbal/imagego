/**
 * IMAGENERATOR API DOCUMENTATION // Interactive Client Controller
 */
document.addEventListener('DOMContentLoaded', () => {
  // Tab switching
  document.querySelectorAll('.tab-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tab-btn').forEach((b) => b.classList.remove('active'));
      document.querySelectorAll('.tab-pane').forEach((p) => p.classList.remove('active'));

      btn.classList.add('active');
      const tabId = `tab-${btn.dataset.tab}`;
      const pane = document.getElementById(tabId);
      if (pane) pane.classList.add('active');
    });
  });

  // Dynamic API Key visibility
  const tryProvider = document.getElementById('tryProvider');
  const apiKeyRow = document.getElementById('apiKeyRow');

  if (tryProvider && apiKeyRow) {
    tryProvider.addEventListener('change', () => {
      const val = tryProvider.value;
      if (val === 'openai' || val === 'stability') {
        apiKeyRow.style.display = 'block';
      } else {
        apiKeyRow.style.display = 'none';
      }
    });
  }

  // Interactive Try It Out Form for POST /api/generate
  const tryGenerateForm = document.getElementById('tryGenerateForm');
  const executeGenerateBtn = document.getElementById('executeGenerateBtn');
  const generateOutputBox = document.getElementById('generateOutputBox');
  const genStatusPill = document.getElementById('genStatusPill');
  const genMetaPill = document.getElementById('genMetaPill');
  const generateJsonOutput = document.getElementById('generateJsonOutput');
  const generateImagePreview = document.getElementById('generateImagePreview');
  const previewImgElement = document.getElementById('previewImgElement');

  if (tryGenerateForm) {
    tryGenerateForm.addEventListener('submit', async (e) => {
      e.preventDefault();

      const prompt = document.getElementById('tryPrompt').value.trim();
      const aspect_ratio = document.getElementById('tryRatio').value;
      const provider = document.getElementById('tryProvider').value;
      const style = document.getElementById('tryStyle').value;
      const api_key = document.getElementById('tryApiKey')?.value.trim() || undefined;

      executeGenerateBtn.disabled = true;
      executeGenerateBtn.querySelector('span').textContent = 'Executing Request...';
      generateOutputBox.classList.remove('hidden');
      genStatusPill.className = 'output-status-pill';
      genStatusPill.textContent = 'DISPATCHING...';
      generateJsonOutput.textContent = 'Connecting to /api/generate endpoint...';
      generateImagePreview.classList.add('hidden');

      const startTime = performance.now();

      try {
        const payload = {
          prompt,
          aspect_ratio,
          provider,
          style,
          count: 1,
          api_key,
        };

        const res = await fetch('/api/generate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });

        const elapsed = ((performance.now() - startTime) / 1000).toFixed(2);
        const data = await res.json().catch(() => ({}));

        if (res.ok) {
          genStatusPill.className = 'output-status-pill';
          genStatusPill.textContent = `HTTP ${res.status} OK`;
          genMetaPill.textContent = `Latency: ${elapsed}s • Retries: ${data.total_retries ?? 0}`;
          generateJsonOutput.textContent = JSON.stringify(data, null, 2);

          if (data.images && data.images.length > 0) {
            previewImgElement.src = data.images[0].url;
            generateImagePreview.classList.remove('hidden');
          }
        } else {
          genStatusPill.className = 'output-status-pill error';
          genStatusPill.textContent = `HTTP ${res.status} ERROR`;
          genMetaPill.textContent = `Latency: ${elapsed}s`;
          generateJsonOutput.textContent = JSON.stringify(data, null, 2);
        }
      } catch (err) {
        genStatusPill.className = 'output-status-pill error';
        genStatusPill.textContent = 'REQUEST FAILED';
        generateJsonOutput.textContent = `Network / Client Error: ${err.message}`;
      } finally {
        executeGenerateBtn.disabled = false;
        executeGenerateBtn.querySelector('span').textContent = 'Execute POST Request';
      }
    });
  }

  // Interactive Live GET /api/history
  const executeHistoryBtn = document.getElementById('executeHistoryBtn');
  const historyOutputBox = document.getElementById('historyOutputBox');
  const historyJsonOutput = document.getElementById('historyJsonOutput');

  if (executeHistoryBtn) {
    executeHistoryBtn.addEventListener('click', async () => {
      executeHistoryBtn.disabled = true;
      executeHistoryBtn.querySelector('span').textContent = 'Fetching...';
      historyOutputBox.classList.remove('hidden');
      historyJsonOutput.textContent = 'Executing GET /api/history...';

      try {
        const res = await fetch('/api/history');
        const data = await res.json();
        historyJsonOutput.textContent = JSON.stringify(data, null, 2);
      } catch (err) {
        historyJsonOutput.textContent = `Error: ${err.message}`;
      } finally {
        executeHistoryBtn.disabled = false;
        executeHistoryBtn.querySelector('span').textContent = 'Execute GET /api/history';
      }
    });
  }

  // Interactive Live GET /api/health
  const executeHealthBtn = document.getElementById('executeHealthBtn');
  const healthOutputBox = document.getElementById('healthOutputBox');
  const healthJsonOutput = document.getElementById('healthJsonOutput');

  if (executeHealthBtn) {
    executeHealthBtn.addEventListener('click', async () => {
      executeHealthBtn.disabled = true;
      executeHealthBtn.querySelector('span').textContent = 'Checking...';
      healthOutputBox.classList.remove('hidden');
      healthJsonOutput.textContent = 'Executing GET /api/health...';

      try {
        const res = await fetch('/api/health');
        const data = await res.json();
        healthJsonOutput.textContent = JSON.stringify(data, null, 2);
      } catch (err) {
        healthJsonOutput.textContent = `Error: ${err.message}`;
      } finally {
        executeHealthBtn.disabled = false;
        executeHealthBtn.querySelector('span').textContent = 'Execute GET /api/health';
      }
    });
  }
});
