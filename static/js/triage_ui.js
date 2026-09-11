/**
 * Pashu Suraksha - Syndromic Triage UI Controller
 * Handles interactive symptom picking, dynamic real-time AI scoring, and offline-first reporting.
 */

const SYMPTOM_DEFINITIONS = [
  { id: "oral_vesicles", label: "मुंह/जीभ पर छाले (Oral Blisters/Vesicles)", icon: "👅" },
  { id: "hoof_lesions", label: "खुरों में छाले/घाव (Hoof Ulcers/Lesions)", icon: "🦶" },
  { id: "excessive_salivation", label: "मुंह से अधिक लार गिरना (Drooling/Salivation)", icon: "💧" },
  { id: "lameness", label: "लंगड़ाना/चलने में दर्द (Severe Lameness)", icon: "🦯" },
  { id: "skin_nodules", label: "त्वचा पर गोल गांठें (Cutaneous Nodules 2-5cm)", icon: "⚪" },
  { id: "enlarged_lymph_nodes", label: "गिल्टियों का बढ़ना (Enlarged Lymph Nodes)", icon: "🩺" },
  { id: "limb_edema", label: "पैरों/गले में सूजन (Limb/Dewlap Edema)", icon: "🦵" },
  { id: "throat_swelling", label: "गले में गर्म व दर्दनाक सूजन (Throat Swelling)", icon: "🧣" },
  { id: "stertorous_breathing", label: "घरघराहट/खर्राटे की सांस (Snoring Dyspnea)", icon: "🫁" },
  { id: "sudden_unexplained_death", label: "अचानक बिना लक्षण मृत्यु (Sudden Peracute Death)", icon: "⚠️" },
  { id: "unclotted_dark_blood", label: "नाक/गुदा से काला न जमने वाला खून (Dark Bleeding)", icon: "🩸" },
  { id: "crepitant_swelling", label: "मांसपेशियों में चरचराहट की सूजन (Crepitant Swelling)", icon: "💥" },
  { id: "erosive_stomatitis", label: "बकरी/भेड़ के मुंह में घाव (Erosive Stomatitis)", icon: "🐐" },
  { id: "severe_diarrhea", label: "तीव्र बदबूदार दस्त (Severe Foul Diarrhea)", icon: "🚽" },
  { id: "late_term_abortion", label: "6-8 माह में गर्भपात (Late-Term Abortion)", icon: "🤰" },
  { id: "cyanosis_comb_wattles", label: "मुर्गी की कलगी नीली पड़ना (Cyanosis Comb)", icon: "🐔" },
  { id: "drop_in_milk", label: "दूध उत्पादन में अचानक गिरावट (Drop in Milk)", icon: "🥛" },
  { id: "loss_of_appetite", label: "चारा न खाना/सुस्ती (Loss of Appetite)", icon: "🥣" }
];

let selectedSpecies = "Cattle";
let selectedSymptoms = new Set();
let debounceTimer = null;

function initTriageUI() {
  renderSymptomSelector();
  setupSpeciesSelectors();
  setupInputListeners();
}

function renderSymptomSelector() {
  const container = document.getElementById('symptomsContainer');
  if (!container) return;

  container.innerHTML = SYMPTOM_DEFINITIONS.map(sym => `
    <div class="symptom-tag" id="tag-${sym.id}" onclick="toggleSymptom('${sym.id}')">
      <span>${sym.icon}</span>
      <span>${sym.label}</span>
    </div>
  `).join('');
}

function setupSpeciesSelectors() {
  const cards = document.querySelectorAll('.species-card');
  cards.forEach(card => {
    card.addEventListener('click', () => {
      cards.forEach(c => c.classList.remove('active'));
      card.classList.add('active');
      selectedSpecies = card.dataset.species;
      triggerRealtimeAssessment();
    });
  });
}

function setupInputListeners() {
  const feverCheck = document.getElementById('hasFeverCheck');
  const affectedCount = document.getElementById('affectedCountInput');
  const mortalityCount = document.getElementById('mortalityCountInput');

  [feverCheck, affectedCount, mortalityCount].forEach(input => {
    if (input) {
      input.addEventListener('change', triggerRealtimeAssessment);
      input.addEventListener('input', triggerRealtimeAssessment);
    }
  });
}

function toggleSymptom(symptomId) {
  const el = document.getElementById(`tag-${symptomId}`);
  if (selectedSymptoms.has(symptomId)) {
    selectedSymptoms.delete(symptomId);
    el.classList.remove('checked');
  } else {
    selectedSymptoms.add(symptomId);
    el.classList.add('checked');
  }
  triggerRealtimeAssessment();
}

function triggerRealtimeAssessment() {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(async () => {
    const fever = document.getElementById('hasFeverCheck')?.checked || false;
    const affected = parseInt(document.getElementById('affectedCountInput')?.value || "1");
    const mortality = parseInt(document.getElementById('mortalityCountInput')?.value || "0");

    if (selectedSymptoms.size === 0 && !fever && mortality === 0) {
      renderTriagePlaceholder();
      return;
    }

    try {
      const res = await fetch('/api/triage/assess', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          species: selectedSpecies,
          symptoms: Array.from(selectedSymptoms),
          has_fever: fever,
          affected_count: affected,
          mortality_count: mortality
        })
      });
      const result = await res.json();
      renderTriageResultCard(result);
    } catch (err) {
      console.error('Triage assessment error:', err);
    }
  }, 250);
}

function renderTriagePlaceholder() {
  const card = document.getElementById('liveTriageCard');
  if (!card) return;
  card.className = 'triage-output-card';
  card.innerHTML = `
    <div style="text-align:center; padding:1.5rem; color:#94a3b8;">
      <div style="font-size:2rem; margin-bottom:0.5rem;">🤖</div>
      <h4 style="color:#64748b; margin-bottom:0.25rem;">AI Clinical Triage Assistant</h4>
      <p style="font-size:0.82rem;">Select animal species and observed symptoms to compute instant differential diagnosis and containment triggers.</p>
    </div>
  `;
}

function renderTriageResultCard(result) {
  const card = document.getElementById('liveTriageCard');
  if (!card) return;

  const top = result.top_diagnosis || {};
  const urgencyClass = (result.urgency || 'low').toLowerCase();
  card.className = `triage-output-card ${urgencyClass}`;

  let biohazardHtml = '';
  if (result.is_zoonotic || urgencyClass === 'critical') {
    biohazardHtml = `
      <div class="biohazard-banner">
        <span style="font-size:1.3rem;">⚠️</span>
        <div>
          <b>${result.is_zoonotic ? 'ZOONOTIC & BIOHAZARD WARNING' : 'HIGH EPIDEMIC THREAT'}:</b><br>
          ${result.biohazard_alert || top.biohazard_alert || ''}
        </div>
      </div>
    `;
  }

  let containmentRingHtml = '';
  if (result.trigger_containment_ring) {
    containmentRingHtml = `
      <div style="background:#fef3c7; border:1px solid #fcd34d; padding:0.6rem 0.8rem; border-radius:6px; font-size:0.82rem; margin:0.6rem 0; color:#92400e;">
        <b>🚨 Automated Quarantine Ring Activated:</b> 
        3 km Infected Zone + ${result.containment_ring_radius_km || 10} km Surveillance Zone buffer recommended.
      </div>
    `;
  }

  let diffListHtml = '';
  if (result.differential_diagnoses && result.differential_diagnoses.length > 0) {
    diffListHtml = `
      <div style="margin-top:0.75rem; font-size:0.82rem;">
        <span style="font-weight:600; color:#475569;">Differential Diagnoses:</span>
        <div style="display:flex; gap:0.5rem; flex-wrap:wrap; margin-top:0.25rem;">
          ${result.differential_diagnoses.map(d => `
            <span style="background:#f1f5f9; padding:2px 8px; border-radius:12px; border:1px solid #e2e8f0; font-size:0.75rem;">
              ${d.name} (<b>${d.confidence}%</b>)
            </span>
          `).join('')}
        </div>
      </div>
    `;
  }

  card.innerHTML = `
    <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:0.5rem;">
      <div>
        <span class="badge badge-${urgencyClass}">${result.urgency} URGENCY</span>
        ${result.is_zoonotic ? '<span class="badge badge-critical" style="margin-left:4px;">ZOONOTIC RISK</span>' : ''}
        <h3 style="margin-top:0.35rem; color:#0f172a; font-size:1.15rem;">${top.name}</h3>
      </div>
      <div style="text-align:right;">
        <div style="font-size:1.4rem; font-weight:800; color:${urgencyClass === 'critical' ? '#e11d48' : '#0f766e'};">${top.confidence}%</div>
        <div style="font-size:0.72rem; color:#64748b; font-weight:600;">MATCH SCORE</div>
      </div>
    </div>

    ${biohazardHtml}
    ${containmentRingHtml}

    <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; padding:0.6rem 0.8rem; margin:0.6rem 0; font-size:0.82rem;">
      <p style="margin-bottom:0.35rem;">🧪 <b>Diagnostic Specimen Needed:</b> ${result.recommended_sample || top.sample_required || 'Swab / Serum'}</p>
      <p style="margin:0;">🛡️ <b>Recommended Protocol:</b> ${result.recommended_containment || top.containment_action || 'Isolate animal and contact vet dispensary.'}</p>
    </div>

    ${diffListHtml}
  `;
}

async function submitSyndromicReport(e) {
  e.preventDefault();

  const fever = document.getElementById('hasFeverCheck')?.checked || false;
  const affected = parseInt(document.getElementById('affectedCountInput')?.value || "1");
  const mortality = parseInt(document.getElementById('mortalityCountInput')?.value || "0");
  const reporterType = document.getElementById('reporterTypeSelect')?.value || "FARMER";
  const reporterName = document.getElementById('reporterNameInput')?.value || "Local Reporter";
  const reporterPhone = document.getElementById('reporterPhoneInput')?.value || "9876543210";
  const animalTag = document.getElementById('reportAnimalTagInput')?.value || null;
  const village = document.getElementById('reportVillageInput')?.value || "Dhani Mohabbatpur";
  const block = document.getElementById('reportBlockInput')?.value || "Hansi";
  const district = document.getElementById('reportDistrictInput')?.value || "Hisar";
  const lat = parseFloat(document.getElementById('reportLatInput')?.value || "29.1023");
  const lon = parseFloat(document.getElementById('reportLonInput')?.value || "76.0125");
  const notes = document.getElementById('reportNotesInput')?.value || "";

  if (selectedSymptoms.size === 0 && !fever && mortality === 0) {
    alert('Please select at least one observed symptom or mortality indicator.');
    return;
  }

  const reportPayload = {
    species: selectedSpecies,
    symptoms: Array.from(selectedSymptoms),
    has_fever: fever,
    affected_count: affected,
    mortality_count: mortality,
    reporter_type: reporterType,
    reporter_name: reporterName,
    reporter_phone: reporterPhone,
    animal_tag: animalTag,
    village: village,
    block: block,
    district: district,
    latitude: lat,
    longitude: lon,
    additional_notes: notes
  };

  const submitBtn = document.getElementById('submitReportBtn');
  submitBtn.disabled = true;
  submitBtn.innerText = 'Submitting & Processing Triage...';

  try {
    if (!navigator.onLine) {
      // OFFLINE QUEUE
      await window.OfflineManager.saveReportLocally(reportPayload);
      alert('⚠️ Network Offline: Report securely saved to local device storage! It will automatically sync to the central server when connectivity resumes.');
      resetTriageForm();
    } else {
      // ONLINE POST
      const res = await fetch('/api/reports', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(reportPayload)
      });
      const data = await res.json();

      if (data.success) {
        let msg = `✅ Report successfully registered (ID: ${data.report_id})!\nDifferential Diagnosis: ${data.triage_result.top_diagnosis.name} (${data.triage_result.top_diagnosis.confidence}%)`;
        if (data.lab_referral_barcode) {
          msg += `\n🧪 Diagnostic Sample Requisition Generated: ${data.lab_referral_barcode}`;
        }
        if (data.cluster_alert) {
          msg += `\n🚨 OUTBREAK CLUSTER DETECTED: Automatic containment protocol dispatched to District Veterinary Officer.`;
        }
        alert(msg);
        resetTriageForm();
        if (window.App && window.App.refreshData) {
          window.App.refreshData();
        }
        // Switch to map view to show point
        window.App.switchTab('map');
        window.MapManager.focus(lat, lon, 11);
      }
    }
  } catch (err) {
    console.error('Error submitting report:', err);
    // Fallback to local storage
    await window.OfflineManager.saveReportLocally(reportPayload);
    alert('⚠️ Server connection error: Report saved to local device queue and will sync automatically.');
    resetTriageForm();
  } finally {
    submitBtn.disabled = false;
    submitBtn.innerText = 'Submit Disease Report';
  }
}

function resetTriageForm() {
  selectedSymptoms.clear();
  document.querySelectorAll('.symptom-tag').forEach(tag => tag.classList.remove('checked'));
  const notes = document.getElementById('reportNotesInput');
  if (notes) notes.value = '';
  const fever = document.getElementById('hasFeverCheck');
  if (fever) fever.checked = false;
  const aff = document.getElementById('affectedCountInput');
  if (aff) aff.value = '1';
  const mort = document.getElementById('mortalityCountInput');
  if (mort) mort.value = '0';
  renderTriagePlaceholder();
}

function loadPreset(type) {
  resetTriageForm();
  const cattleCard = document.querySelector('.species-card[data-species="Cattle"]');
  if (cattleCard) cattleCard.click();

  if (type === 'FMD') {
    ['oral_vesicles', 'hoof_lesions', 'excessive_salivation', 'lameness'].forEach(id => {
      if (!selectedSymptoms.has(id)) toggleSymptom(id);
    });
    const fever = document.getElementById('hasFeverCheck');
    if (fever) {
      fever.checked = true;
      fever.dispatchEvent(new Event('change'));
    }
  } else if (type === 'LSD') {
    ['skin_nodules', 'limb_edema', 'enlarged_lymph_nodes'].forEach(id => {
      if (!selectedSymptoms.has(id)) toggleSymptom(id);
    });
    const fever = document.getElementById('hasFeverCheck');
    if (fever) {
      fever.checked = true;
      fever.dispatchEvent(new Event('change'));
    }
  } else if (type === 'ANTHRAX') {
    ['sudden_unexplained_death', 'unclotted_dark_blood'].forEach(id => {
      if (!selectedSymptoms.has(id)) toggleSymptom(id);
    });
    const mort = document.getElementById('mortalityCountInput');
    if (mort) {
      mort.value = '1';
      mort.dispatchEvent(new Event('change'));
    }
  }
}

window.toggleSymptom = toggleSymptom;
window.selectedSymptoms = selectedSymptoms;

window.TriageManager = {
  init: initTriageUI,
  submit: submitSyndromicReport,
  toggleSymptom: toggleSymptom,
  selectedSymptoms: selectedSymptoms,
  loadPreset: loadPreset,
  resetForm: resetTriageForm
};
