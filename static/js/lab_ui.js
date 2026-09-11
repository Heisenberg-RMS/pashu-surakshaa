/**
 * Pashu Suraksha - Laboratory Referral & Chain-of-Custody Tracker
 * Monitors diagnostic sample collection, cold-chain logistics, and PCR/ELISA test results.
 */

const STEPS = [
  { key: "SAMPLE_COLLECTED", label: "Sample Collected" },
  { key: "IN_TRANSIT", label: "Cold-Chain Transit" },
  { key: "RECEIVED_AT_LAB", label: "Lab Received" },
  { key: "TESTING_IN_PROGRESS", label: "PCR / ELISA Testing" },
  { key: "CONFIRMED", label: "Result Certified" }
];

let allReferralsCache = [];

async function initLabUI() {
  await loadLabReferrals();
}

async function loadLabReferrals() {
  try {
    const res = await fetch('/api/lab-referrals');
    allReferralsCache = await res.json();
    renderLabTable(allReferralsCache);
    if (allReferralsCache.length > 0) {
      renderChainOfCustodyDetail(allReferralsCache[0]);
    }
  } catch (err) {
    console.error('Failed to load lab referrals:', err);
  }
}

function selectBarcode(barcode) {
  const item = allReferralsCache.find(x => x.sample_barcode === barcode);
  if (item) renderChainOfCustodyDetail(item);
}

function renderLabTable(referrals) {
  const tbody = document.getElementById('labTableBody');
  if (!tbody) return;

  if (referrals.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; color:#94a3b8; padding:2rem;">No diagnostic requisitions found.</td></tr>`;
    return;
  }

  tbody.innerHTML = referrals.map(r => {
    let resultBadge = 'badge-medium';
    if (r.result_certified === 'POSITIVE') resultBadge = 'badge-critical';
    if (r.result_certified === 'NEGATIVE') resultBadge = 'badge-low';

    return `
      <tr style="cursor:pointer;" onclick="window.LabManager.selectBarcode('${r.sample_barcode}')">
        <td><code><b>${r.sample_barcode}</b></code></td>
        <td>${r.animal_tag || 'Herd Sample'}</td>
        <td><b>${r.suspect_disease}</b><br><small style="color:#64748b;">${r.sample_type}</small></td>
        <td>${r.target_lab}</td>
        <td><span class="badge ${resultBadge}">${r.result_certified}</span></td>
        <td>
          <button class="btn btn-outline btn-sm" onclick="event.stopPropagation(); window.LabManager.selectBarcode('${r.sample_barcode}')">
            Track Status
          </button>
        </td>
      </tr>
    `;
  }).join('');
}

function renderChainOfCustodyDetail(r) {
  const container = document.getElementById('labDetailContainer');
  if (!container) return;

  const currentStatusIndex = STEPS.findIndex(s => s.key === r.chain_of_custody_status);

  container.innerHTML = `
    <div class="card">
      <div class="card-header">
        <div>
          <span style="font-size:0.75rem; text-transform:uppercase; color:#64748b; font-weight:700;">Diagnostic Chain of Custody</span>
          <h3 class="card-title" style="margin-top:0.25rem;">Specimen: ${r.sample_barcode}</h3>
        </div>
        <span class="badge badge-${r.result_certified === 'POSITIVE' ? 'critical' : 'medium'}">${r.chain_of_custody_status}</span>
      </div>

      <!-- Visual Step Tracker -->
      <div class="timeline-track">
        ${STEPS.map((s, idx) => {
          let stepClass = '';
          if (idx < currentStatusIndex || r.chain_of_custody_status === 'CONFIRMED') stepClass = 'completed';
          else if (idx === currentStatusIndex) stepClass = 'active';

          return `
            <div class="timeline-step ${stepClass}">
              <div class="step-node">${idx < currentStatusIndex ? '✓' : idx + 1}</div>
              <div class="step-label">${s.label}</div>
            </div>
          `;
        }).join('')}
      </div>

      <!-- Sample Metadata Grid -->
      <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:1rem; background:#f8fafc; padding:1rem; border-radius:8px; border:1px solid #e2e8f0; margin-bottom:1rem; font-size:0.85rem;">
        <div><b>Target Pathogen:</b><br>${r.suspect_disease}</div>
        <div><b>Specimen Type:</b><br>${r.sample_type}</div>
        <div><b>Testing Laboratory:</b><br>${r.target_lab}</div>
        <div><b>Collected On:</b><br>${r.collection_date}</div>
        <div><b>Animal Tag:</b><br>${r.animal_tag || 'Unspecified Herd'}</div>
        <div><b>Origin Village:</b><br>${r.village || 'Field Report'}, ${r.district || ''}</div>
      </div>

      <!-- Lab Notes & Certification Result -->
      <div style="background:#fff; border:1px solid #e2e8f0; border-radius:8px; padding:0.85rem; margin-bottom:1rem; font-size:0.85rem;">
        <b>🔬 Laboratory Findings / Test Notes:</b>
        <p style="color:#475569; margin:0.35rem 0 0 0;">${r.result_notes || 'Diagnostic testing awaiting completion.'}</p>
        ${r.tested_at ? `<small style="color:#64748b;">Report certified on: ${r.tested_at}</small>` : ''}
      </div>

      <!-- Action Controls for Lab Personnel -->
      <div style="display:flex; gap:0.5rem; justify-content:flex-end;">
        ${r.chain_of_custody_status === 'SAMPLE_COLLECTED' ? `
          <button class="btn btn-outline btn-sm" onclick="window.LabManager.updateStep('${r.sample_barcode}', 'IN_TRANSIT', 'PENDING', 'Dispatched via temperature-monitored cold transport courier')">
            🚚 Dispatch to Transit
          </button>
        ` : ''}

        ${r.chain_of_custody_status === 'IN_TRANSIT' ? `
          <button class="btn btn-outline btn-sm" onclick="window.LabManager.updateStep('${r.sample_barcode}', 'RECEIVED_AT_LAB', 'PENDING', 'Sample received at referral lab with cold-chain intact')">
            📥 Mark Received at Lab
          </button>
        ` : ''}

        ${r.chain_of_custody_status === 'RECEIVED_AT_LAB' ? `
          <button class="btn btn-primary btn-sm" onclick="window.LabManager.updateStep('${r.sample_barcode}', 'TESTING_IN_PROGRESS', 'PENDING', 'RNA/DNA extracted; Real-time PCR and ELISA running')">
            🧪 Start PCR/ELISA Analysis
          </button>
        ` : ''}

        ${r.chain_of_custody_status === 'TESTING_IN_PROGRESS' ? `
          <button class="btn btn-danger btn-sm" onclick="window.LabManager.certify('${r.sample_barcode}', 'POSITIVE')">
            🔴 Certify POSITIVE
          </button>
          <button class="btn btn-primary btn-sm" style="background:#059669;" onclick="window.LabManager.certify('${r.sample_barcode}', 'NEGATIVE')">
            🟢 Certify NEGATIVE
          </button>
        ` : ''}
      </div>
    </div>
  `;
}

function updateLabStep(barcode, status, resultCertified, notes) {
  fetch(`/api/lab-referrals/${barcode}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      chain_of_custody_status: status,
      result_certified: resultCertified,
      result_notes: notes
    })
  }).then(res => res.json()).then(() => {
    loadLabReferrals();
  });
}

function certifyResult(barcode, outcome) {
  const notes = prompt(`Enter Lab Certification Notes for ${barcode} (${outcome}):`,
    outcome === 'POSITIVE' ? 'Pathogen genomic sequence confirmed via multiplex RT-PCR. High copy number.' : 'Pathogen not detected above threshold.');
  if (notes === null) return;

  fetch(`/api/lab-referrals/${barcode}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      chain_of_custody_status: 'CONFIRMED',
      result_certified: outcome,
      result_notes: notes
    })
  }).then(res => res.json()).then(() => {
    alert(`Laboratory test result certified as ${outcome}! Escalation broadcast to District Veterinary Officer.`);
    loadLabReferrals();
    if (window.App && window.App.refreshData) {
      window.App.refreshData();
    }
  });
}

window.updateLabStep = updateLabStep;
window.certifyResult = certifyResult;
window.renderChainOfCustodyDetail = renderChainOfCustodyDetail;

window.LabManager = {
  init: initLabUI,
  load: loadLabReferrals,
  selectBarcode: selectBarcode,
  updateStep: updateLabStep,
  certify: certifyResult
};
