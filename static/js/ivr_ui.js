/**
 * Pashu Suraksha - Simulated Telephone IVR Hotline Engine (Toll-Free 1962)
 * Simulates interactive phone dialer with automated voice prompts for feature-phone users in low-connectivity areas.
 */

let ivrSession = {
  active: false,
  step: "START",
  selectedSpecies: null,
  callerPhone: "9876540001",
  audioPromptEnabled: true
};

function initIVRUI() {
  setupDialpadKeys();
  renderIVRScreen();
}

function setupDialpadKeys() {
  const dialButtons = document.querySelectorAll('.dial-btn');
  dialButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const num = btn.dataset.num;
      handleDialpadPress(num);
    });
  });

  const toggleCallBtn = document.getElementById('toggleCallBtn');
  if (toggleCallBtn) {
    toggleCallBtn.addEventListener('click', toggleIVRCall);
  }
}

function toggleIVRCall() {
  const toggleBtn = document.getElementById('toggleCallBtn');
  if (!ivrSession.active) {
    // Start call
    ivrSession.active = true;
    ivrSession.step = "START";
    ivrSession.selectedSpecies = null;
    toggleBtn.style.background = '#e11d48';
    toggleBtn.innerHTML = '📞 End Call (कॉल काटें)';
    sendIVRInput("");
  } else {
    // End call
    ivrSession.active = false;
    window.VoiceManager.stop();
    toggleBtn.style.background = '#059669';
    toggleBtn.innerHTML = '📞 Call Toll-Free 1962 (कॉल लगाएं)';
    renderIVRScreen("Call Ended. धन्यवाद।");
  }
}

function handleDialpadPress(num) {
  if (!ivrSession.active) {
    alert("Please press 'Call Toll-Free 1962' to initiate the call session first.");
    return;
  }
  // Play subtle DTMF tone simulation or feedback
  sendIVRInput(num);
}

async function sendIVRInput(digits) {
  try {
    const res = await fetch('/api/ivr/process', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        step: ivrSession.step,
        digits: digits,
        selected_species: ivrSession.selectedSpecies,
        caller_phone: ivrSession.callerPhone
      })
    });

    const data = await res.json();
    ivrSession.step = data.next_step;
    if (data.selected_species) {
      ivrSession.selectedSpecies = data.selected_species;
    }

    renderIVRResponse(data);

    // Speak voice prompt if enabled
    if (ivrSession.audioPromptEnabled && data.prompt_text) {
      window.VoiceManager.speak(data.prompt_text, 'hi-IN');
    }

  } catch (err) {
    console.error('IVR Error:', err);
    renderIVRScreen("Connection Error. कृपया पुनः प्रयास करें।");
  }
}

function renderIVRResponse(data) {
  const screenEl = document.getElementById('phoneScreenBody');
  if (!screenEl) return;

  let optionsHtml = '';
  if (data.options && data.options.length > 0) {
    optionsHtml = `
      <div style="margin-top:0.5rem; font-size:0.75rem; color:#38bdf8;">
        ${data.options.map(o => `<div>${o}</div>`).join('')}
      </div>
    `;
  }

  screenEl.innerHTML = `
    <div style="color:#a7f3d0; font-size:0.75rem; margin-bottom:0.35rem;">
      ${ivrSession.step === 'COMPLETED' ? '✅ REPORT REGISTERED' : '⚡ INTERACTIVE CALL IN PROGRESS'}
    </div>
    <div style="font-weight:600; color:#fff; font-size:0.88rem;">${data.prompt_text}</div>
    <div style="color:#94a3b8; font-size:0.75rem; margin-top:0.4rem; font-style:italic;">${data.prompt_text_en || ''}</div>
    ${optionsHtml}
  `;

  if (data.next_step === 'COMPLETED') {
    // Refresh app data to show new report
    if (window.App && window.App.refreshData) {
      window.App.refreshData();
    }
  }
}

function renderIVRScreen(text) {
  const screenEl = document.getElementById('phoneScreenBody');
  if (screenEl) {
    screenEl.innerHTML = `<div style="text-align:center; padding:2rem 0; color:#94a3b8;">${text || 'Toll-Free 1962 Animal Helpline<br><small>Press Call button below to connect</small>'}</div>`;
  }
}

window.IVRManager = {
  init: initIVRUI,
  toggle: toggleIVRCall
};
