/**
 * Pashu Suraksha - Master Application Controller
 * Orchestrates navigation, role-based views, dashboards, charts, and data synchronization.
 */

let currentRole = "DVO";
let epiChart = null;
let diseasePieChart = null;

let currentUser = null;

// ==========================================
// AUTHENTICATION & IDENTITY MANAGER
// ==========================================
class AuthenticationManager {
  constructor() {
    this.currentUser = null;
  }

  async init() {
    try {
      const res = await fetch('/api/auth/me');
      const data = await res.json();
      this.currentUser = data.user;
      currentRole = this.currentUser.role || 'DVO';
      this.updateHeaderProfile();
      this.applyRoleContext();
    } catch (err) {
      console.warn('Auth init fallback:', err);
    }
  }

  updateHeaderProfile() {
    if (!this.currentUser) return;

    const avatarMap = {
      'FARMER': '👨‍🌾',
      'PARA_VET': '🩺',
      'DVO': '🏛️',
      'DIRECTOR': '📊'
    };

    const avatarEl = document.getElementById('headerUserAvatar');
    const nameEl = document.getElementById('headerUserName');
    const roleEl = document.getElementById('headerUserRole');

    if (avatarEl) avatarEl.innerText = avatarMap[this.currentUser.role] || '👤';
    if (nameEl) nameEl.innerText = this.currentUser.full_name || 'User';
    if (roleEl) roleEl.innerText = this.currentUser.designation || this.currentUser.role;
  }

  applyRoleContext() {
    if (!this.currentUser) return;
    const role = this.currentUser.role;

    // Pre-populate Triage Reporter inputs
    const repType = document.getElementById('reporterTypeSelect');
    const repName = document.getElementById('reporterNameInput');
    const repPhone = document.getElementById('reporterPhoneInput');
    const repVillage = document.getElementById('reportVillageInput');
    const repBlock = document.getElementById('reportBlockInput');
    const repDistrict = document.getElementById('reportDistrictInput');

    if (repType) {
      if (role === 'FARMER') repType.value = 'FARMER';
      else if (role === 'PARA_VET') repType.value = 'PARA_VET';
      else repType.value = 'VET_OFFICER';
    }

    if (repName && this.currentUser.full_name) {
      repName.value = this.currentUser.full_name;
    }
    if (repPhone && this.currentUser.phone) {
      repPhone.value = this.currentUser.phone;
    }
    if (repVillage && this.currentUser.village) {
      repVillage.value = this.currentUser.village;
    }
    if (repBlock && this.currentUser.block) {
      repBlock.value = this.currentUser.block;
    }
    if (repDistrict && this.currentUser.district) {
      repDistrict.value = this.currentUser.district;
    }

    // Role-specific view recommendations
    if (role === 'FARMER') {
      const ehrSearch = document.getElementById('ehrSearchInput');
      if (ehrSearch && this.currentUser.full_name) {
        ehrSearch.value = this.currentUser.full_name;
        ehrSearch.dispatchEvent(new Event('input'));
      }
    }
  }

  openModal() {
    const modal = document.getElementById('loginModal');
    if (modal) modal.classList.add('open');
  }

  closeModal() {
    const modal = document.getElementById('loginModal');
    if (modal) modal.classList.remove('open');
    const err = document.getElementById('loginErrorMsg');
    if (err) err.style.display = 'none';
  }

  switchAuthTab(tabId) {
    document.querySelectorAll('.auth-tab-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.authTab === tabId);
    });
    document.querySelectorAll('.auth-tab-pane').forEach(pane => {
      pane.classList.toggle('active', pane.id === `authPane-${tabId}`);
    });
  }

  async loginAsRole(role) {
    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ role: role })
      });
      const data = await res.json();
      if (data.success) {
        this.currentUser = data.user;
        currentRole = role;
        this.updateHeaderProfile();
        this.applyRoleContext();
        this.closeModal();
        alert(`✅ Logged in successfully as ${this.currentUser.full_name} (${this.currentUser.designation})`);
        refreshDashboardData();
      }
    } catch (err) {
      console.error('Quick login error:', err);
    }
  }

  async submitPasswordLogin(e) {
    e.preventDefault();
    const username = document.getElementById('loginUsernameInput')?.value.trim();
    const password = document.getElementById('loginPasswordInput')?.value.trim();
    const errorEl = document.getElementById('loginErrorMsg');
    const submitBtn = document.getElementById('loginSubmitBtn');

    if (errorEl) errorEl.style.display = 'none';
    submitBtn.disabled = true;
    submitBtn.innerText = 'Verifying Credentials...';

    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      const data = await res.json();

      if (data.success) {
        this.currentUser = data.user;
        currentRole = data.user.role;
        this.updateHeaderProfile();
        this.applyRoleContext();
        this.closeModal();
        alert(`✅ Welcome back, ${data.user.full_name}! (${data.user.designation})`);
        refreshDashboardData();
      } else {
        if (errorEl) {
          errorEl.innerText = data.error || 'Authentication failed. Please check credentials.';
          errorEl.style.display = 'block';
        }
      }
    } catch (err) {
      if (errorEl) {
        errorEl.innerText = 'Network error during login.';
        errorEl.style.display = 'block';
      }
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerText = 'Authenticate & Sign In';
    }
  }

  async sendOTP() {
    const phone = document.getElementById('otpPhoneInput')?.value.trim();
    if (!phone) {
      alert('Please enter a valid mobile number.');
      return;
    }

    try {
      const res = await fetch('/api/auth/otp/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone })
      });
      const data = await res.json();
      if (data.success) {
        const alertEl = document.getElementById('otpSentAlert');
        if (alertEl) alertEl.style.display = 'block';
        const otpInput = document.getElementById('otpValueInput');
        if (otpInput) otpInput.value = data.simulated_otp; // convenient testing auto-fill
      }
    } catch (err) {
      console.error('OTP Send error:', err);
    }
  }

  async verifyOTP() {
    const phone = document.getElementById('otpPhoneInput')?.value.trim();
    const otp = document.getElementById('otpValueInput')?.value.trim();

    if (!phone || !otp) {
      alert('Please enter both mobile number and OTP.');
      return;
    }

    try {
      const res = await fetch('/api/auth/otp/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone, otp })
      });
      const data = await res.json();

      if (data.success) {
        this.currentUser = data.user;
        currentRole = data.user.role;
        this.updateHeaderProfile();
        this.applyRoleContext();
        this.closeModal();
        alert(`✅ Mobile OTP Verified! Welcome, ${data.user.full_name}.`);
        refreshDashboardData();
      } else {
        alert(data.error || 'OTP verification failed.');
      }
    } catch (err) {
      console.error('OTP Verify error:', err);
    }
  }

  async logout() {
    await fetch('/api/auth/logout', { method: 'POST' });
    this.init();
    alert('You have logged out.');
  }
}

window.AuthManager = new AuthenticationManager();

document.addEventListener('DOMContentLoaded', async () => {
  // Initialize subsystems
  window.OfflineManager.initDB();
  window.AuthManager.init();
  window.TriageManager.init();
  window.IVRManager.init();
  window.EHRManager.init();
  window.LabManager.init();
  if (window.VisionManager) window.VisionManager.init();
  if (window.ChatbotManager) window.ChatbotManager.init();
  
  setupNavigation();
  setupAdvisoriesUI();
  setupWeatherPanel();
  
  await refreshDashboardData();

  // Register Service Worker
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js')
      .then(reg => console.log('PWA Service Worker registered:', reg.scope))
      .catch(err => console.log('Service Worker registration skipped:', err));
  }
});

function setupNavigation() {
  const tabs = document.querySelectorAll('.tab-btn');
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const targetView = tab.dataset.tab;
      switchTab(targetView);
    });
  });

  const mobileNavs = document.querySelectorAll('.mobile-nav-item');
  mobileNavs.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetView = btn.dataset.tab;
      if (targetView === 'chat') {
        if (window.ChatbotManager) window.ChatbotManager.openChat();
      } else if (targetView) {
        switchTab(targetView);
      }
    });
  });
}

function switchTab(viewId) {
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.tab === viewId);
  });

  document.querySelectorAll('.mobile-nav-item').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.tab === viewId);
  });

  document.querySelectorAll('.tab-view').forEach(view => {
    view.classList.toggle('active', view.id === `view-${viewId}`);
  });

  if (viewId === 'map') {
    setTimeout(() => {
      window.MapManager.init();
      window.MapManager.refresh();
      if (window.MapManager.invalidateSize) window.MapManager.invalidateSize();
    }, 150);
  } else if (viewId === 'dashboard') {
    renderCharts();
  }
}

async function refreshDashboardData() {
  try {
    const res = await fetch('/api/stats/dashboard');
    const data = await res.json();

    const m = data.metrics;
    document.getElementById('kpiTotalLivestock').innerText = m.total_registered_livestock.toLocaleString();
    document.getElementById('kpiActiveMorbidity').innerText = m.active_morbidity_count;
    document.getElementById('kpiTotalReports').innerText = m.total_surveillance_reports;
    document.getElementById('kpiOutbreakClusters').innerText = m.active_outbreak_clusters;
    document.getElementById('kpiPendingLab').innerText = m.pending_diagnostic_samples;
    document.getElementById('kpiVaccineCoverage').innerText = m.herd_immunity_index;

    renderRecentReports(data.recent_reports || []);
    updateCharts(data.disease_breakdown || []);
  } catch (err) {
    console.error('Failed to load dashboard stats:', err);
  }
}

function renderRecentReports(reports) {
  const tbody = document.getElementById('recentReportsTableBody');
  if (!tbody) return;

  if (reports.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; color:#94a3b8; padding:1.5rem;">No recent syndromic reports.</td></tr>`;
    return;
  }

  tbody.innerHTML = reports.map(r => `
    <tr>
      <td><code><b>${r.report_uid}</b></code><br><small style="color:#64748b;">${r.reporter_type}</small></td>
      <td><b>${r.species}</b></td>
      <td><b>${r.triage_name || 'General Sickness'}</b> (${r.confidence}%)</td>
      <td>${r.village}, ${r.district}</td>
      <td><span class="badge badge-${(r.urgency || 'low').toLowerCase()}">${r.urgency}</span></td>
      <td>
        <button class="btn btn-outline btn-sm" onclick="window.App.switchTab('map'); window.MapManager.focus(${r.latitude}, ${r.longitude}, 12);">
          View on Map
        </button>
      </td>
    </tr>
  `).join('');
}

function updateCharts(breakdown) {
  const labels = breakdown.map(b => b.triage_code || 'Unknown');
  const counts = breakdown.map(b => b.count);

  const ctxPie = document.getElementById('diseaseDonutChart')?.getContext('2d');
  if (ctxPie) {
    if (diseasePieChart) diseasePieChart.destroy();
    diseasePieChart = new Chart(ctxPie, {
      type: 'doughnut',
      data: {
        labels: labels,
        datasets: [{
          data: counts,
          backgroundColor: ['#e11d48', '#f59e0b', '#0284c7', '#10b981', '#8b5cf6', '#64748b']
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { position: 'bottom' }
        }
      }
    });
  }

  const ctxLine = document.getElementById('epiCurveChart')?.getContext('2d');
  if (ctxLine) {
    if (epiChart) epiChart.destroy();
    epiChart = new Chart(ctxLine, {
      type: 'line',
      data: {
        labels: ['Day -6', 'Day -5', 'Day -4', 'Day -3', 'Day -2', 'Yesterday', 'Today'],
        datasets: [
          {
            label: 'FMD Cases',
            data: [1, 2, 2, 4, 6, 8, 9],
            borderColor: '#e11d48',
            backgroundColor: 'rgba(225, 29, 72, 0.1)',
            fill: true,
            tension: 0.3
          },
          {
            label: 'LSD Cases',
            data: [0, 1, 1, 2, 3, 4, 4],
            borderColor: '#f59e0b',
            backgroundColor: 'rgba(245, 158, 11, 0.1)',
            fill: true,
            tension: 0.3
          },
          {
            label: 'HS Mortality',
            data: [0, 0, 1, 0, 1, 0, 1],
            borderColor: '#7c3aed',
            tension: 0.3
          }
        ]
      },
      options: {
        responsive: true,
        scales: {
          y: { beginAtZero: true }
        }
      }
    });
  }
}

function renderCharts() {
  refreshDashboardData();
}

async function setupWeatherPanel() {
  try {
    const res = await fetch('/api/weather-risk');
    const profiles = await res.json();
    const select = document.getElementById('weatherRegionSelect');
    if (!select) return;

    select.innerHTML = profiles.map((p, idx) => `
      <option value="${idx}">${p.district} (${p.state})</option>
    `).join('');

    select.addEventListener('change', () => {
      renderSelectedWeather(profiles[select.value]);
    });

    if (profiles.length > 0) {
      renderSelectedWeather(profiles[0]);
    }
  } catch (err) {
    console.error('Weather panel error:', err);
  }
}

function renderSelectedWeather(p) {
  if (!p) return;
  const c = p.meteorological_conditions;
  const idx = p.indices;

  document.getElementById('envTempDisplay').innerText = `${c.temperature_c}°C`;
  document.getElementById('envHumidityDisplay').innerText = `${c.relative_humidity_percent}%`;
  document.getElementById('envRainDisplay').innerText = `${c.precipitation_24h_mm} mm`;
  document.getElementById('envWindDisplay').innerText = `${c.wind_speed_kmh} km/h`;

  const setBar = (fillId, score, color) => {
    const el = document.getElementById(fillId);
    if (el) {
      el.style.width = `${score}%`;
      el.style.background = color;
    }
  };

  setBar('fillVectorRisk', idx.vector_breeding_suitability.score, idx.vector_breeding_suitability.score > 60 ? '#e11d48' : '#f59e0b');
  setBar('fillFMDRisk', idx.fmd_airborne_dispersion.score, idx.fmd_airborne_dispersion.score > 60 ? '#e11d48' : '#0f766e');
  setBar('fillHSRisk', idx.waterlogging_stress_hs.score, idx.waterlogging_stress_hs.score > 60 ? '#e11d48' : '#0284c7');
}

async function setupAdvisoriesUI() {
  const alertTypeSelect = document.getElementById('advisoryTypeSelect');
  const langSelect = document.getElementById('advisoryLangSelect');
  const playBtn = document.getElementById('playAdvisoryAudioBtn');
  const broadcastBtn = document.getElementById('broadcastSMSBtn');

  const loadPreview = async () => {
    const alertType = alertTypeSelect.value;
    const lang = langSelect.value;
    try {
      const res = await fetch(`/api/advisories/preview?alert_type=${alertType}&lang=${lang}`);
      const data = await res.json();
      document.getElementById('advisoryPreviewTitle').innerText = data.title;
      document.getElementById('advisoryPreviewText').innerText = data.text;
      document.getElementById('advisoryVoiceScript').innerText = data.voice_script;
    } catch (e) {
      console.error('Failed to preview advisory:', e);
    }
  };

  if (alertTypeSelect && langSelect) {
    alertTypeSelect.addEventListener('change', loadPreview);
    langSelect.addEventListener('change', loadPreview);
    loadPreview();
  }

  if (playBtn) {
    playBtn.addEventListener('click', () => {
      const text = document.getElementById('advisoryVoiceScript')?.innerText || "";
      const lang = langSelect?.value || "hi";
      const bcpMap = { "hi": "hi-IN", "en": "en-IN", "pa": "pa-IN", "bn": "bn-IN", "mr": "mr-IN", "te": "te-IN", "ta": "ta-IN" };
      window.VoiceManager.togglePlayback(text, bcpMap[lang] || 'hi-IN');
    });
  }

  if (broadcastBtn) {
    broadcastBtn.addEventListener('click', async () => {
      const alertType = alertTypeSelect.value;
      const lang = langSelect.value;
      const radius = parseFloat(document.getElementById('broadcastRadiusInput')?.value || "10");

      broadcastBtn.disabled = true;
      broadcastBtn.innerText = 'Broadcasting Emergency Alerts...';

      try {
        const res = await fetch('/api/advisories/broadcast', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            alert_type: alertType,
            language: lang,
            district: "Hisar",
            block: "Hansi",
            radius_km: radius,
            channel: "SMS_AND_VOICE"
          })
        });
        const data = await res.json();

        alert(`📢 Emergency Advisory Broadcast Dispatched!\n• Reached: ${data.farmers_reached} registered livestock keepers\n• Channels: SMS, Automated IVR Voice Broadcast & Pashu Sakhi App\n• Radius: ${radius} km quarantine containment zone.`);
        loadAdvisoriesHistory();
      } catch (e) {
        console.error('Broadcast error:', e);
      } finally {
        broadcastBtn.disabled = false;
        broadcastBtn.innerText = '📢 Broadcast Emergency SMS & Voice Alert';
      }
    });
  }

  loadAdvisoriesHistory();
}

async function loadAdvisoriesHistory() {
  try {
    const res = await fetch('/api/advisories');
    const advisories = await res.json();
    const tbody = document.getElementById('advisoriesHistoryTableBody');
    if (!tbody) return;

    if (advisories.length === 0) {
      tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; color:#94a3b8;">No broadcasts logged.</td></tr>`;
      return;
    }

    tbody.innerHTML = advisories.map(a => `
      <tr>
        <td><b>${a.title}</b></td>
        <td>${a.target_district} (${a.target_block})</td>
        <td>${a.target_radius_km} km Ring</td>
        <td><b>${a.farmers_notified_count}</b> Farmers</td>
        <td>${a.broadcast_at.split('T')[0] || a.broadcast_at}</td>
      </tr>
    `).join('');
  } catch (e) {
    console.error('Failed to load advisories log:', e);
  }
}

function triggerEmergencyAction(diseaseCode, district, block) {
  switchTab('advisories');
  const typeMap = {
    "FMD": "FMD_OUTBREAK",
    "LSD": "LSD_OUTBREAK",
    "ANTHRAX": "ANTHRAX_BIOHAZARD"
  };
  const typeSelect = document.getElementById('advisoryTypeSelect');
  if (typeSelect && typeMap[diseaseCode]) {
    typeSelect.value = typeMap[diseaseCode];
    typeSelect.dispatchEvent(new Event('change'));
  }
}

window.App = {
  switchTab: switchTab,
  refreshData: refreshDashboardData,
  triggerEmergencyAction: triggerEmergencyAction
};
