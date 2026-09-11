/**
 * Pashu Suraksha - Electronic Health Records (EHR) & Pashu Swasthya Card
 * Tracks animal tags, herd vaccination schedules, antimicrobial withdrawal stewardship, and clinical history.
 */

let allAnimalsCache = [];

async function initEHRUI() {
  await loadAnimalsList();
  setupEHRSearch();
}

async function loadAnimalsList() {
  try {
    const res = await fetch('/api/animals');
    allAnimalsCache = await res.json();
    renderAnimalsTable(allAnimalsCache);
    if (allAnimalsCache.length > 0) {
      // Auto-load first animal
      loadAnimalDetails(allAnimalsCache[0].tag_number);
    }
  } catch (err) {
    console.error('Failed to load animals:', err);
  }
}

function renderAnimalsTable(animals) {
  const tbody = document.getElementById('animalsTableBody');
  if (!tbody) return;

  if (animals.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; color:#94a3b8; padding:2rem;">No livestock records found.</td></tr>`;
    return;
  }

  tbody.innerHTML = animals.map(a => {
    let statusBadge = 'badge-low';
    if (a.health_status === 'SICK') statusBadge = 'badge-high';
    if (a.health_status === 'QUARANTINED') statusBadge = 'badge-critical';

    return `
      <tr style="cursor:pointer;" onclick="window.EHRManager.loadAnimalDetails('${a.tag_number}')">
        <td><b>${a.tag_number}</b><br><small style="color:#64748b;">${a.rfid_uid || 'RFID-N/A'}</small></td>
        <td>${a.species} (${a.breed || 'Indigenous'})</td>
        <td>${a.sex} • ${Math.round(a.age_months / 12)} yrs</td>
        <td>${a.owner_name}<br><small style="color:#64748b;">${a.village}, ${a.district}</small></td>
        <td><span class="badge ${statusBadge}">${a.health_status}</span></td>
        <td>
          <button class="btn btn-outline btn-sm" onclick="event.stopPropagation(); window.EHRManager.loadAnimalDetails('${a.tag_number}')">
            View EHR
          </button>
        </td>
      </tr>
    `;
  }).join('');
}

function setupEHRSearch() {
  const searchInput = document.getElementById('ehrSearchInput');
  if (!searchInput) return;

  searchInput.addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase().trim();
    if (!query) {
      renderAnimalsTable(allAnimalsCache);
      return;
    }
    const filtered = allAnimalsCache.filter(a =>
      a.tag_number.includes(query) ||
      a.owner_name.toLowerCase().includes(query) ||
      a.village.toLowerCase().includes(query) ||
      a.species.toLowerCase().includes(query)
    );
    renderAnimalsTable(filtered);
  });
}

async function loadAnimalDetails(tagNumber) {
  try {
    const res = await fetch(`/api/animals/${tagNumber}`);
    if (!res.ok) return;
    const animal = await res.json();
    renderAnimalPassport(animal);
  } catch (err) {
    console.error('Failed to load animal EHR:', err);
  }
}

function renderAnimalPassport(animal) {
  const container = document.getElementById('animalPassportContainer');
  if (!container) return;

  const vaccinations = animal.vaccinations || [];
  const treatments = animal.treatments || [];
  const reports = animal.reports || [];

  let statusBadge = 'badge-low';
  if (animal.health_status === 'SICK') statusBadge = 'badge-high';
  if (animal.health_status === 'QUARANTINED') statusBadge = 'badge-critical';

  // Check withdrawal stewardship
  let activeWithdrawal = treatments.find(t => {
    if (!t.withdrawal_end_date) return false;
    return new Date(t.withdrawal_end_date) >= new Date();
  });

  container.innerHTML = `
    <!-- Pashu Swasthya Card -->
    <div style="background: linear-gradient(135deg, #0f766e 0%, #115e59 100%); color:#fff; border-radius:12px; padding:1.25rem; margin-bottom:1.25rem; box-shadow:0 4px 6px -1px rgba(0,0,0,0.1);">
      <div style="display:flex; justify-content:space-between; align-items:flex-start;">
        <div>
          <span style="font-size:0.75rem; text-transform:uppercase; letter-spacing:0.05em; background:rgba(255,255,255,0.2); padding:2px 8px; border-radius:12px;">Digital Animal Health Passport</span>
          <h2 style="margin:0.4rem 0 0.1rem 0; font-size:1.4rem;">${animal.tag_number}</h2>
          <div style="font-size:0.8rem; color:#ccfbf1;">RFID UID: ${animal.rfid_uid || 'RFID-TAGGED'}</div>
        </div>
        <span class="badge ${statusBadge}" style="font-size:0.85rem; padding:0.35rem 0.75rem; background:#fff; color:#0f766e;">${animal.health_status}</span>
      </div>

      <div style="display:grid; grid-template-columns: repeat(4, 1fr); gap:0.75rem; margin-top:1rem; padding-top:0.75rem; border-top:1px solid rgba(255,255,255,0.2); font-size:0.85rem;">
        <div><small style="color:#a7f3d0;">Species/Breed</small><br><b>${animal.species}</b> (${animal.breed})</div>
        <div><small style="color:#a7f3d0;">Sex / Age</small><br><b>${animal.sex}</b> (${Math.round(animal.age_months/12)} Yrs)</div>
        <div><small style="color:#a7f3d0;">Livestock Owner</small><br><b>${animal.owner_name}</b></div>
        <div><small style="color:#a7f3d0;">Location</small><br><b>${animal.village}</b>, ${animal.district}</div>
      </div>
    </div>

    ${activeWithdrawal ? `
      <div style="background:#fff1f2; border:2px solid #fda4af; border-radius:8px; padding:0.85rem; margin-bottom:1.25rem; color:#9f1239; font-size:0.85rem;">
        <b>⚠️ ANTIMICROBIAL RESIDUE WITHDRAWAL ACTIVE:</b><br>
        Treated with <i>${activeWithdrawal.drug_administered}</i> on ${activeWithdrawal.treatment_date}.
        <b>Milk and meat are strictly UNFIT for human consumption</b> until <b>${activeWithdrawal.withdrawal_end_date}</b> (${activeWithdrawal.withdrawal_period_days} days withdrawal).
      </div>
    ` : ''}

    <!-- Vaccination History -->
    <div class="card" style="margin-bottom:1.25rem;">
      <div class="card-header">
        <h3 class="card-title">💉 Vaccination & Immunization History</h3>
        <button class="btn btn-outline btn-sm" onclick="window.EHRManager.openAddVaccinationModal('${animal.tag_number}')">
          + Record Vaccination
        </button>
      </div>
      <table class="custom-table">
        <thead>
          <tr>
            <th>Vaccine</th>
            <th>Target Disease</th>
            <th>Batch No</th>
            <th>Administered</th>
            <th>Next Due Date</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          ${vaccinations.length === 0 ? '<tr><td colspan="6" style="text-align:center; color:#94a3b8;">No vaccination records found.</td></tr>' : vaccinations.map(v => {
            const isOverdue = v.status === 'OVERDUE' || new Date(v.next_due_date) < new Date();
            return `
              <tr>
                <td><b>${v.vaccine_name}</b></td>
                <td>${v.disease_targeted}</td>
                <td><code>${v.batch_number || 'N/A'}</code></td>
                <td>${v.administered_date}</td>
                <td>${v.next_due_date}</td>
                <td>
                  <span class="badge ${isOverdue ? 'badge-critical' : 'badge-low'}">
                    ${isOverdue ? 'OVERDUE' : 'UP-TO-DATE'}
                  </span>
                </td>
              </tr>
            `;
          }).join('')}
        </tbody>
      </table>
    </div>

    <!-- Clinical Treatments & Prescriptions -->
    <div class="card">
      <div class="card-header">
        <h3 class="card-title">🩺 Clinical Treatments & Veterinary Care</h3>
      </div>
      <table class="custom-table">
        <thead>
          <tr>
            <th>Date</th>
            <th>Diagnosis</th>
            <th>Drug / Prescription</th>
            <th>Dosage</th>
            <th>Withdrawal Period</th>
            <th>Attending Vet</th>
          </tr>
        </thead>
        <tbody>
          ${treatments.length === 0 ? '<tr><td colspan="6" style="text-align:center; color:#94a3b8;">No recent treatment records.</td></tr>' : treatments.map(t => `
            <tr>
              <td>${t.treatment_date}</td>
              <td><b>${t.diagnosis}</b></td>
              <td>${t.drug_administered}</td>
              <td>${t.dosage || 'Standard'}</td>
              <td>${t.withdrawal_period_days > 0 ? `${t.withdrawal_period_days} Days` : 'Nil'}</td>
              <td>${t.vet_name || 'Field Vet'}</td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
  `;
}

function openAddVaccinationModal(tagNumber) {
  const vaccineName = prompt(`Enter Vaccine Name for ${tagNumber}:`, "Raksha-Ovac FMD");
  if (!vaccineName) return;
  const disease = prompt("Target Disease:", "Foot-and-Mouth Disease");
  const nextDueDate = prompt("Next Due Date (YYYY-MM-DD):", "2027-03-15");

  fetch('/api/vaccinations', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      animal_tag: tagNumber,
      vaccine_name: vaccineName,
      disease_targeted: disease,
      next_due_date: nextDueDate,
      administered_by: "Dr. Field Veterinarian"
    })
  }).then(res => res.json()).then(() => {
    alert("Vaccination successfully recorded!");
    loadAnimalDetails(tagNumber);
  });
}

window.loadAnimalDetails = loadAnimalDetails;
window.openAddVaccinationModal = openAddVaccinationModal;

window.EHRManager = {
  init: initEHRUI,
  loadAnimalDetails: loadAnimalDetails,
  openAddVaccinationModal: openAddVaccinationModal
};
