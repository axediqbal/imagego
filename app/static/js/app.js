/**
 * IMAGENERATOR // Next-Gen Multimodal AI Studio
 * Client Controller & State Management
 */

document.addEventListener('DOMContentLoaded', () => {
  // Model Metadata & Display Mappings
  const MODEL_META = {
    'pollinations_flux': { label: 'Pollinations Flux AI', badge: 'Flux HD (Free)', isPaid: false },
    'pollinations_sana': { label: 'Pollinations Sana AI', badge: 'Sana Fast (Free)', isPaid: false },
    'pollinations_turbo': { label: 'Pollinations Turbo AI', badge: 'Turbo (Free)', isPaid: false },
    'mock': { label: 'Local Mock Engine', badge: 'Local Mock (Offline)', isPaid: false },
    'openai': { label: 'OpenAI DALL-E 3', badge: 'DALL-E 3 (Paid Key)', isPaid: true },
    'stability': { label: 'Stability AI SDXL', badge: 'SDXL 1024 (Paid Key)', isPaid: true },
  };

  let savedProvider = localStorage.getItem('imagenerator_provider') || 'pollinations_flux';
  if (savedProvider === 'pollinations_sana') {
    savedProvider = 'pollinations_flux';
    localStorage.setItem('imagenerator_provider', 'pollinations_flux');
  }
  const savedApiKey = localStorage.getItem('imagenerator_api_key') || '';

  // Application State
  const state = {
    aspectRatio: '16:9',
    count: 1,
    style: 'cinematic',
    isGenerating: false,
    artworks: [],
    provider: savedProvider,
    apiKey: savedApiKey,
    activeLightboxArt: null,
  };

  // Curated inspiration prompts
  const PROMPT_LIBRARY = [
    "A cute fluffy golden retriever puppy wearing sunglasses on a sunny beach, photorealistic 8k",
    "A futuristic luxury sports car racing through neon rain, cyberpunk style reflections",
    "Gilded solarium astronomical observatory with brass celestial armillary spheres, volumetric god rays",
    "Surreal floating crystal pagoda above a sea of iridescent liquid mercury at sunset, cinematic mist",
    "Luminescent biomechanical jellyfish floating through an obsidian cosmic trench, bioluminescent tentacles, 8k render",
    "Astronaut floating high above planet Earth against deep blue atmosphere, hyper-detailed photography, 8k",
    "Ancient overgrown cyberpunk temple reclaimed by glowing crystalline flora and neon waterfalls",
    "Ethereal spirit fox with nine flaming cyan tails walking across a frozen lake under aurora borealis"
  ];

  // DOM Elements - Studio Prompt & Controls
  const promptInput = document.getElementById('promptInput');
  const promptCharCount = document.getElementById('promptCharCount');
  const randomizePromptBtn = document.getElementById('randomizePromptBtn');
  const aiOptimizePromptBtn = document.getElementById('aiOptimizePromptBtn');
  const agentStatusLabel = document.getElementById('agentStatusLabel');
  const agentRefineBtn = document.getElementById('agentRefineBtn');
  const toggleNegativeBtn = document.getElementById('toggleNegativePromptBtn');
  const negativePromptContainer = document.getElementById('negativePromptContainer');
  const negativePromptInput = document.getElementById('negativePromptInput');
  const aspectRatioGrid = document.getElementById('aspectRatioGrid');
  const styleCardsGrid = document.getElementById('styleCardsGrid');
  const activeStyleBadge = document.getElementById('activeStyleBadge');
  const styleSelect = document.getElementById('styleSelect');
  const countControl = document.getElementById('countControl');
  const batchPill = document.getElementById('batchPill');
  const simulateCorruptionToggle = document.getElementById('simulateCorruptionToggle');
  const generateBtn = document.getElementById('generateBtn');
  const generateBtnText = document.getElementById('generateBtnText');
  const telemetryCard = document.getElementById('telemetryCard');
  const telemetryStepText = document.getElementById('telemetryStepText');
  const telemetryRetryPill = document.getElementById('telemetryRetryPill');
  const telemetryDimsPill = document.getElementById('telemetryDimsPill');
  const telemetryProgressBar = document.getElementById('telemetryProgressBar');
  const telemetryLogText = document.getElementById('telemetryLogText');
  const artworkGrid = document.getElementById('artworkGrid');
  const emptyState = document.getElementById('emptyState');
  const artworksCounter = document.getElementById('artworksCounter');
  const refreshHistoryBtn = document.getElementById('refreshHistoryBtn');
  const navEngineName = document.getElementById('navEngineName');

  // Model & API Key Elements
  const modelSelector = document.getElementById('modelSelector');
  const activeModelBadge = document.getElementById('activeModelBadge');
  const apiKeyDrawer = document.getElementById('apiKeyDrawer');
  const apiKeyTitle = document.getElementById('apiKeyTitle');
  const customApiKeyInput = document.getElementById('customApiKeyInput');
  const toggleApiKeyVisBtn = document.getElementById('toggleApiKeyVisBtn');
  const saveApiKeyBtn = document.getElementById('saveApiKeyBtn');
  const clearApiKeyBtn = document.getElementById('clearApiKeyBtn');
  const modalApiKeySection = document.getElementById('modalApiKeySection');
  const modalApiKeyInput = document.getElementById('modalApiKeyInput');
  const modalToggleApiKeyVisBtn = document.getElementById('modalToggleApiKeyVisBtn');

  // Lightbox Elements
  const lightboxModal = document.getElementById('lightboxModal');
  const closeLightboxBtn = document.getElementById('closeLightboxBtn');
  const lightboxImage = document.getElementById('lightboxImage');
  const lightboxPrompt = document.getElementById('lightboxPrompt');
  const lightboxRatio = document.getElementById('lightboxRatio');
  const lightboxDimensions = document.getElementById('lightboxDimensions');
  const lightboxStyle = document.getElementById('lightboxStyle');
  const lightboxVerification = document.getElementById('lightboxVerification');
  const lightboxRetries = document.getElementById('lightboxRetries');
  const lightboxFileSize = document.getElementById('lightboxFileSize');
  const lightboxDownloadBtn = document.getElementById('lightboxDownloadBtn');
  const lightboxCopyPromptBtn = document.getElementById('lightboxCopyPromptBtn');
  const lightboxDeleteBtn = document.getElementById('lightboxDeleteBtn');

  // Settings Elements
  const openSettingsBtn = document.getElementById('openSettingsBtn');
  const settingsModal = document.getElementById('settingsModal');
  const closeSettingsBtn = document.getElementById('closeSettingsBtn');
  const saveSettingsBtn = document.getElementById('saveSettingsBtn');
  const toastContainer = document.getElementById('toastContainer');

  // Strict 1080p Standard Dimensions
  const RATIO_READOUT = {
    '16:9': '1920 × 1080 px',
    '1:1': '1080 × 1080 px',
    '9:16': '1080 × 1920 px',
  };

  // Initialize
  setProvider(state.provider, false);
  checkServerHealth();
  loadHistory();
  bindEvents();

  /**
   * Set and Synchronize Active AI Provider & Model
   */
  function setProvider(providerKey, persist = true) {
    if (!MODEL_META[providerKey]) {
      providerKey = 'pollinations_flux';
    }
    state.provider = providerKey;
    if (persist) {
      localStorage.setItem('imagenerator_provider', providerKey);
    }

    const meta = MODEL_META[providerKey];
    if (modelSelector) modelSelector.value = providerKey;
    if (activeModelBadge) activeModelBadge.textContent = meta.badge;
    if (navEngineName) navEngineName.textContent = meta.label;

    // Update settings modal tiles
    document.querySelectorAll('.provider-radio-tile').forEach((t) => {
      const isMatch = t.dataset.provider === providerKey;
      t.classList.toggle('active', isMatch);
      const radio = t.querySelector('input[type="radio"]');
      if (radio && isMatch) radio.checked = true;
    });

    // Toggle API Key drawer & modal section
    if (meta.isPaid) {
      if (apiKeyDrawer) apiKeyDrawer.classList.remove('hidden');
      if (modalApiKeySection) modalApiKeySection.classList.remove('hidden');
      const placeholder = providerKey === 'openai' ? 'Paste OpenAI Key (sk-proj-...)' : 'Paste Stability Key (sk-...)';
      if (customApiKeyInput) {
        customApiKeyInput.placeholder = placeholder;
        customApiKeyInput.value = state.apiKey;
      }
      if (modalApiKeyInput) {
        modalApiKeyInput.placeholder = placeholder;
        modalApiKeyInput.value = state.apiKey;
      }
      if (apiKeyTitle) {
        apiKeyTitle.textContent = `${meta.label} API Key Required`;
      }
    } else {
      if (apiKeyDrawer) apiKeyDrawer.classList.add('hidden');
      if (modalApiKeySection) modalApiKeySection.classList.add('hidden');
    }
  }

  /**
   * Save API Key helper
   */
  function saveApiKey(keyVal) {
    state.apiKey = (keyVal || '').trim();
    localStorage.setItem('imagenerator_api_key', state.apiKey);
    if (customApiKeyInput) customApiKeyInput.value = state.apiKey;
    if (modalApiKeyInput) modalApiKeyInput.value = state.apiKey;
    if (state.apiKey) {
      showToast('API Key saved safely in browser localStorage!', 'info');
    } else {
      showToast('API Key removed.', 'info');
    }
  }

  /**
   * Delete Artwork by Filename
   */
  async function deleteArtwork(filename, event) {
    if (event) event.stopPropagation();
    if (!filename) return;

    if (!confirm('Are you sure you want to delete this artwork? This action cannot be undone.')) {
      return;
    }

    try {
      const res = await fetch(`/api/history/${filename}`, {
        method: 'DELETE',
      });
      if (!res.ok) {
        throw new Error('Failed to delete artwork.');
      }

      state.artworks = state.artworks.filter((a) => a.filename !== filename);
      renderGallery();
      showToast('Artwork permanently deleted from archive.', 'info');

      if (state.activeLightboxArt && state.activeLightboxArt.filename === filename) {
        lightboxModal.classList.add('hidden');
        state.activeLightboxArt = null;
      }
    } catch (err) {
      showToast(err.message, 'error');
    }
  }

  /**
   * Bind DOM Events
   */
  function bindEvents() {
    // Character Counter
    promptInput.addEventListener('input', () => {
      promptCharCount.textContent = `${promptInput.value.length}/1000`;
    });

    // Randomize / Inspire
    randomizePromptBtn.addEventListener('click', () => {
      const prompt = PROMPT_LIBRARY[Math.floor(Math.random() * PROMPT_LIBRARY.length)];
      promptInput.value = prompt;
      promptCharCount.textContent = `${promptInput.value.length}/1000`;
      promptInput.focus();
      showToast('New concept loaded!', 'info');
    });

    // AI Prompt Intelligence Auto-Enhance Button
    if (aiOptimizePromptBtn) {
      aiOptimizePromptBtn.addEventListener('click', async () => {
        let current = promptInput.value.trim();
        if (!current) current = "Toyota Supra racing in neon city";
        aiOptimizePromptBtn.disabled = true;
        try {
          const res = await fetch('/api/prompt/optimize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              prompt: current,
              style: state.style,
              negative_prompt: negativePromptInput.value.trim() || null,
            }),
          });
          if (res.ok) {
            const data = await res.json();
            promptInput.value = data.optimized_prompt;
            promptCharCount.textContent = `${promptInput.value.length}/1000`;
            if (data.suggested_negative_prompt && !negativePromptInput.value.trim()) {
              negativePromptInput.value = data.suggested_negative_prompt;
            }
            showToast('Prompt expanded with 8k AI Intelligence!', 'info');
          }
        } catch (e) {
          showToast('Could not optimize prompt', 'error');
        } finally {
          aiOptimizePromptBtn.disabled = false;
        }
      });
    }

    // AI Vision Agent Refine Button (Translates Roman Urdu and reasons over prompt)
    if (agentRefineBtn) {
      agentRefineBtn.addEventListener('click', async () => {
        let current = promptInput.value.trim();
        if (!current) current = "Toyota Supra racing in neon city";
        agentRefineBtn.disabled = true;
        if (agentStatusLabel) agentStatusLabel.textContent = "Agent interpreting intent & translating semantics...";

        try {
          const res = await fetch('/api/agent/understand', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              prompt: current,
              style: state.style,
              negative_prompt: negativePromptInput.value.trim() || null,
              api_key: state.apiKey || null,
            }),
          });
          if (res.ok) {
            const data = await res.json();
            promptInput.value = data.final_prompt;
            promptCharCount.textContent = `${promptInput.value.length}/1000`;
            if (data.negative_prompt && !negativePromptInput.value.trim()) {
              negativePromptInput.value = data.negative_prompt;
            }
            if (agentStatusLabel) {
              agentStatusLabel.textContent = `Optimized via ${data.agent_type} (${data.detected_language})`;
            }
            if (data.detected_language && data.detected_language.includes('Urdu')) {
              showToast('🤖 Agent translated Roman Urdu and engineered 1080p photorealistic directives!', 'info');
            } else {
              showToast('🤖 Agent engineered vivid 1080p directives!', 'info');
            }
          }
        } catch (e) {
          showToast('Could not reach prompt agent', 'error');
          if (agentStatusLabel) agentStatusLabel.textContent = "Agent standby";
        } finally {
          agentRefineBtn.disabled = false;
        }
      });
    }

    // Inspiration Chips
    document.querySelectorAll('.chip-item').forEach((chip) => {
      chip.addEventListener('click', () => {
        if (chip.dataset.prompt) {
          promptInput.value = chip.dataset.prompt;
          promptCharCount.textContent = `${promptInput.value.length}/1000`;
          promptInput.focus();
        }
      });
    });

    // Model Selector dropdown
    if (modelSelector) {
      modelSelector.addEventListener('change', (e) => {
        setProvider(e.target.value);
        showToast(`Selected model: ${MODEL_META[e.target.value]?.label || e.target.value}`, 'info');
      });
    }

    // Inline API Key controls
    if (saveApiKeyBtn && customApiKeyInput) {
      saveApiKeyBtn.addEventListener('click', () => saveApiKey(customApiKeyInput.value));
      customApiKeyInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') saveApiKey(customApiKeyInput.value);
      });
    }

    if (clearApiKeyBtn) {
      clearApiKeyBtn.addEventListener('click', () => saveApiKey(''));
    }

    if (toggleApiKeyVisBtn && customApiKeyInput) {
      toggleApiKeyVisBtn.addEventListener('click', () => {
        const isPass = customApiKeyInput.type === 'password';
        customApiKeyInput.type = isPass ? 'text' : 'password';
        toggleApiKeyVisBtn.textContent = isPass ? '🔒' : '👁️';
      });
    }

    // Modal API Key controls
    if (modalToggleApiKeyVisBtn && modalApiKeyInput) {
      modalToggleApiKeyVisBtn.addEventListener('click', () => {
        const isPass = modalApiKeyInput.type === 'password';
        modalApiKeyInput.type = isPass ? 'text' : 'password';
        modalToggleApiKeyVisBtn.textContent = isPass ? '🔒' : '👁️';
      });
    }

    if (modalApiKeyInput) {
      modalApiKeyInput.addEventListener('input', () => {
        state.apiKey = modalApiKeyInput.value.trim();
        localStorage.setItem('imagenerator_api_key', state.apiKey);
        if (customApiKeyInput) customApiKeyInput.value = state.apiKey;
      });
    }

    // Negative Prompt Accordion
    toggleNegativeBtn.addEventListener('click', () => {
      const isOpen = negativePromptContainer.classList.toggle('open');
      toggleNegativeBtn.setAttribute('aria-expanded', isOpen);
      toggleNegativeBtn.querySelector('.chevron-icon').textContent = isOpen ? '▴' : '▾';
    });

    // Aspect Ratio Selection
    aspectRatioGrid.addEventListener('click', (e) => {
      const pill = e.target.closest('.ratio-pill');
      if (pill && pill.dataset.ratio) {
        document.querySelectorAll('.ratio-pill').forEach((p) => p.classList.remove('active'));
        pill.classList.add('active');
        state.aspectRatio = pill.dataset.ratio;
        telemetryDimsPill.textContent = RATIO_READOUT[state.aspectRatio];
      }
    });

    // Style Capsule Selection
    styleCardsGrid.addEventListener('click', (e) => {
      const cap = e.target.closest('.style-capsule');
      if (cap && cap.dataset.style) {
        selectStyle(cap.dataset.style);
      }
    });

    // Batch Selector
    countControl.addEventListener('click', (e) => {
      const btn = e.target.closest('.batch-num-btn');
      if (btn && btn.dataset.count) {
        document.querySelectorAll('.batch-num-btn').forEach((b) => b.classList.remove('active'));
        btn.classList.add('active');
        state.count = parseInt(btn.dataset.count, 10);
        batchPill.textContent = `${state.count} Image${state.count > 1 ? 's' : ''}`;
      }
    });

    // Generate Action
    generateBtn.addEventListener('click', handleGenerate);

    // Refresh History
    refreshHistoryBtn.addEventListener('click', loadHistory);

    // Lightbox Controls
    closeLightboxBtn.addEventListener('click', () => {
      lightboxModal.classList.add('hidden');
      state.activeLightboxArt = null;
    });
    lightboxModal.addEventListener('click', (e) => {
      if (e.target === lightboxModal) {
        lightboxModal.classList.add('hidden');
        state.activeLightboxArt = null;
      }
    });

    lightboxCopyPromptBtn.addEventListener('click', () => {
      navigator.clipboard.writeText(lightboxPrompt.textContent).then(() => {
        showToast('Prompt copied to clipboard!', 'info');
      });
    });

    if (lightboxDeleteBtn) {
      lightboxDeleteBtn.addEventListener('click', () => {
        if (state.activeLightboxArt) {
          deleteArtwork(state.activeLightboxArt.filename);
        }
      });
    }

    // Settings Modal
    openSettingsBtn.addEventListener('click', () => {
      setProvider(state.provider, false);
      settingsModal.classList.remove('hidden');
    });
    closeSettingsBtn.addEventListener('click', () => settingsModal.classList.add('hidden'));
    settingsModal.addEventListener('click', (e) => {
      if (e.target === settingsModal) settingsModal.classList.add('hidden');
    });

    document.querySelectorAll('.provider-radio-tile').forEach((tile) => {
      tile.addEventListener('click', () => {
        const prov = tile.dataset.provider;
        if (prov) {
          setProvider(prov);
        }
      });
    });

    saveSettingsBtn.addEventListener('click', () => {
      const selected = document.querySelector('input[name="providerSelect"]:checked');
      if (selected) {
        setProvider(selected.value);
        showToast(`Engine configured: ${MODEL_META[selected.value]?.label || selected.value}`, 'info');
      }
      settingsModal.classList.add('hidden');
    });

    // Keyboard Shortcuts
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        lightboxModal.classList.add('hidden');
        settingsModal.classList.add('hidden');
      }
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        if (!state.isGenerating) handleGenerate();
      }
    });
  }

  /**
   * Select style helper
   */
  function selectStyle(styleName) {
    state.style = styleName;
    styleSelect.value = styleName;
    activeStyleBadge.textContent = styleName.charAt(0).toUpperCase() + styleName.slice(1);

    document.querySelectorAll('.style-capsule').forEach((c) => {
      if (c.dataset.style === styleName) {
        c.classList.add('active');
      } else {
        c.classList.remove('active');
      }
    });
  }

  /**
   * Health Check
   */
  async function checkServerHealth() {
    try {
      const res = await fetch('/api/health');
      if (res.ok) {
        const data = await res.json();
        if (!localStorage.getItem('imagenerator_provider') && data.provider) {
          const map = {
            'pollinations_flux_ai': 'pollinations_flux',
            'mock_studio_engine': 'mock',
            'openai_dall_e_3': 'openai',
            'stability_sdxl': 'stability',
          };
          const mappedKey = map[data.provider] || 'pollinations_flux';
          setProvider(mappedKey, false);
        }
      }
    } catch (err) {
      console.warn('Server connecting...', err);
    }
  }

  /**
   * Load History
   */
  async function loadHistory() {
    try {
      const res = await fetch('/api/history');
      if (res.ok) {
        const items = await res.json();
        state.artworks = items;
        renderGallery();
      }
    } catch (err) {
      console.warn('Could not sync history:', err);
    }
  }

  /**
   * Primary Generation Workflow
   */
  async function handleGenerate() {
    const prompt = promptInput.value.trim();
    if (!prompt || prompt.length < 3) {
      showToast('Please enter an artwork prompt of at least 3 characters.', 'error');
      promptInput.focus();
      return;
    }

    const currentMeta = MODEL_META[state.provider] || MODEL_META['pollinations_flux'];
    if (currentMeta.isPaid && (!state.apiKey || !state.apiKey.trim())) {
      showToast(`Please enter your ${currentMeta.label} API Key to generate with this model.`, 'error');
      if (apiKeyDrawer) apiKeyDrawer.classList.remove('hidden');
      if (customApiKeyInput) customApiKeyInput.focus();
      return;
    }

    state.isGenerating = true;
    updateGeneratingUI(true);

    // Show Telemetry HUD
    telemetryCard.classList.remove('hidden');
    telemetryProgressBar.style.width = '20%';
    telemetryDimsPill.textContent = RATIO_READOUT[state.aspectRatio];
    telemetryRetryPill.textContent = 'Retries: 0';
    telemetryStepText.textContent = `DISPATCHING TO ${currentMeta.label.toUpperCase()}...`;
    telemetryLogText.textContent = `Resolving 1080p pixel payload: ${state.aspectRatio} (${RATIO_READOUT[state.aspectRatio]}), count=${state.count}, provider=${state.provider}`;

    const simulateCorruption = simulateCorruptionToggle.checked;
    if (simulateCorruption) {
      telemetryLogText.textContent += '\n[TEST ACTIVE] Simulating 1 severed data stream to demonstrate auto-retry!';
    }

    const payload = {
      prompt: prompt,
      negative_prompt: negativePromptInput.value.trim() || null,
      aspect_ratio: state.aspectRatio,
      count: state.count,
      style: state.style,
      provider: state.provider,
      api_key: state.apiKey ? state.apiKey : undefined,
      simulate_corruption: simulateCorruption,
      enable_ai_enhancer: true,
    };

    const stepInterval = setTimeout(() => {
      telemetryProgressBar.style.width = '65%';
      telemetryStepText.textContent = 'SYNTHESIZING 1080p SCANLINES & Image.load()...';
      telemetryLogText.textContent += '\n[INTELLIGENCE GATE] Checking 1080p stream verification with Image.open().load()...';
    }, 450);

    try {
      const startTime = performance.now();
      const res = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      clearTimeout(stepInterval);
      const elapsed = ((performance.now() - startTime) / 1000).toFixed(2);

      if (!res.ok) {
        const errJson = await res.json().catch(() => ({}));
        throw new Error(errJson.detail || `Server returned error status ${res.status}`);
      }

      const result = await res.json();
      telemetryProgressBar.style.width = '100%';
      telemetryRetryPill.textContent = `Retries: ${result.total_retries}`;
      telemetryStepText.textContent = '1080p VERIFIED & PERSISTED!';
      telemetryLogText.textContent += `\n[PASSED] Binary stream verified with Pillow Image.load() (${elapsed}s). Retries: ${result.total_retries}. Saved to outputs/.`;

      // Prepend newly generated items to gallery
      result.images.forEach((img) => state.artworks.unshift(img));
      renderGallery();

      showToast(`Generated ${result.images.length} artwork(s) at 1080p!`, 'info');

      setTimeout(() => {
        telemetryCard.classList.add('hidden');
      }, 4000);

    } catch (err) {
      clearTimeout(stepInterval);
      telemetryProgressBar.style.width = '100%';
      telemetryStepText.textContent = 'GENERATION FAILED';
      telemetryLogText.textContent += `\n[ERROR] ${err.message}`;
      showToast(err.message, 'error');
    } finally {
      state.isGenerating = false;
      updateGeneratingUI(false);
    }
  }

  /**
   * Update UI button state
   */
  function updateGeneratingUI(isBusy) {
    generateBtn.disabled = isBusy;
    if (isBusy) {
      generateBtnText.textContent = 'Verifying Stream...';
    } else {
      generateBtnText.textContent = 'Generate Artwork';
    }
  }

  /**
   * Render Creations Gallery in a 3x3 Matrix Grid
   */
  function renderGallery() {
    artworksCounter.textContent = `${state.artworks.length} Creation${state.artworks.length === 1 ? '' : 's'}`;

    if (state.artworks.length === 0) {
      emptyState.classList.remove('hidden');
      artworkGrid.innerHTML = '';
      return;
    }

    emptyState.classList.add('hidden');
    artworkGrid.innerHTML = '';

    state.artworks.forEach((art) => {
      const card = document.createElement('div');
      card.className = 'artwork-card';
      card.dataset.id = art.id;

      const dimensions = `${art.width} × ${art.height}`;

      card.innerHTML = `
        <div class="card-media-wrap">
          <img src="${art.url}" alt="${escapeHtml(art.prompt)}" class="artwork-thumb" loading="lazy" />
          <div class="card-top-tags">
            <span class="card-tag">${escapeHtml(art.style)}</span>
            <span class="card-verified-badge">✓ 1080p</span>
          </div>
          <div class="card-hover-actions">
            <button type="button" class="card-act-btn inspect-act-btn" title="Inspect Fullscreen">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                <circle cx="12" cy="12" r="3"></circle>
              </svg>
            </button>
            <a href="${art.url}" download="${art.filename}" class="card-act-btn download-act-btn" title="Download PNG" onclick="event.stopPropagation()">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                <polyline points="7 10 12 15 17 10"></polyline>
                <line x1="12" y1="15" x2="12" y2="3"></line>
              </svg>
            </a>
            <button type="button" class="card-act-btn copy-act-btn" title="Copy Prompt">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
              </svg>
            </button>
            <button type="button" class="card-act-btn delete-act-btn" title="Delete Artwork">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="3 6 5 6 21 6"></polyline>
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
              </svg>
            </button>
          </div>
        </div>
        <div class="card-meta-body">
          <p class="card-prompt-title" title="${escapeHtml(art.prompt)}">${escapeHtml(art.prompt)}</p>
          <div class="card-meta-foot">
            <span class="card-dim-tag">${dimensions}</span>
            <span class="card-ratio-tag">${art.aspect_ratio || '16:9'}</span>
            <button type="button" class="card-delete-icon-btn" title="Delete Artwork">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="3 6 5 6 21 6"></polyline>
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
              </svg>
            </button>
          </div>
        </div>
      `;

      // Event listeners for card buttons
      const mediaWrap = card.querySelector('.card-media-wrap');
      const promptTitle = card.querySelector('.card-prompt-title');
      const inspectBtn = card.querySelector('.inspect-act-btn');
      const copyBtn = card.querySelector('.copy-act-btn');
      const deleteBtn = card.querySelector('.delete-act-btn');
      const deleteIconBtn = card.querySelector('.card-delete-icon-btn');

      mediaWrap.addEventListener('click', () => openLightbox(art));
      promptTitle.addEventListener('click', () => openLightbox(art));
      inspectBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        openLightbox(art);
      });

      copyBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        navigator.clipboard.writeText(art.prompt).then(() => {
          showToast('Prompt copied to clipboard!', 'info');
        });
      });

      deleteBtn.addEventListener('click', (e) => deleteArtwork(art.filename, e));
      deleteIconBtn.addEventListener('click', (e) => deleteArtwork(art.filename, e));

      artworkGrid.appendChild(card);
    });
  }

  /**
   * Open Lightbox Modal
   */
  function openLightbox(art) {
    state.activeLightboxArt = art;
    lightboxImage.src = art.url;
    lightboxPrompt.textContent = art.prompt;
    lightboxRatio.textContent = art.aspect_ratio;
    lightboxDimensions.textContent = `${art.width} × ${art.height} px`;
    lightboxStyle.textContent = art.style;
    lightboxRetries.textContent = art.retry_count;

    const sizeMb = (art.file_size_bytes / (1024 * 1024)).toFixed(2);
    lightboxFileSize.textContent = `${sizeMb} MB`;

    lightboxDownloadBtn.href = art.url;
    lightboxDownloadBtn.download = art.filename;

    lightboxModal.classList.remove('hidden');
  }

  /**
   * Toast Notification
   */
  function showToast(msg, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast-bubble ${type}`;
    toast.innerHTML = `
      <span>${type === 'error' ? '⚠' : '✦'}</span>
      <span>${escapeHtml(msg)}</span>
    `;

    toastContainer.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(15px)';
      setTimeout(() => toast.remove(), 300);
    }, 4200);
  }

  // Webflow Expanding Button Glow Circle Micro-Interaction
  document.querySelectorAll('.rt-button-main-v2, .generator-action-btn').forEach((btn) => {
    const circle = btn.querySelector('.rt-button-circle');
    if (!circle) return;
    btn.addEventListener('mousemove', (e) => {
      const rect = btn.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      circle.style.left = `${x}px`;
      circle.style.top = `${y}px`;
    });
  });

  // Webflow Mode Options Strip Handlers
  const tabOptionAiImage = document.getElementById('tabOptionAiImage');
  const tabOption1080p = document.getElementById('tabOption1080p');
  const tabOptionAgent = document.getElementById('tabOptionAgent');
  const tabOptionModels = document.getElementById('tabOptionModels');
  const tabOptionIntegrity = document.getElementById('tabOptionIntegrity');

  const optionTabs = [tabOptionAiImage, tabOption1080p, tabOptionAgent, tabOptionModels, tabOptionIntegrity].filter(Boolean);

  function setActiveOptionTab(activeTab) {
    optionTabs.forEach((tab) => tab.classList.remove('active'));
    if (activeTab) activeTab.classList.add('active');
  }

  if (tabOptionAiImage) {
    tabOptionAiImage.addEventListener('click', () => {
      setActiveOptionTab(tabOptionAiImage);
      promptInput.focus();
    });
  }

  if (tabOption1080p) {
    tabOption1080p.addEventListener('click', () => {
      setActiveOptionTab(tabOption1080p);
      showToast('1080p Strict Resolution active (1920×1080, 1080×1080, 1080×1920)', 'info');
      const ratioCard = document.getElementById('aspectCard169');
      if (ratioCard) ratioCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    });
  }

  if (tabOptionAgent) {
    tabOptionAgent.addEventListener('click', () => {
      setActiveOptionTab(tabOptionAgent);
      if (agentRefineBtn) agentRefineBtn.click();
    });
  }

  if (tabOptionModels) {
    tabOptionModels.addEventListener('click', () => {
      setActiveOptionTab(tabOptionModels);
      if (modelSelector) {
        modelSelector.focus();
        modelSelector.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
    });
  }

  if (tabOptionIntegrity) {
    tabOptionIntegrity.addEventListener('click', () => {
      setActiveOptionTab(tabOptionIntegrity);
      const auditBox = document.querySelector('.audit-box');
      if (auditBox) auditBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      showToast('Pillow Image.open().load() stream verification gate is active', 'info');
    });
  }

  /**
   * XSS Escape
   */
  function escapeHtml(str) {
    if (!str) return '';
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }
});
