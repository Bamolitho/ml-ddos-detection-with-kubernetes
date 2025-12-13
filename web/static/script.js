const flowsBody = document.getElementById('flowsBody');
const searchInput = document.getElementById('searchInput');
const verdictSelect = document.getElementById('verdictSelect');
const actionSelect = document.getElementById('actionSelect');
const applyBtn = document.getElementById('applyBtn');
const resetBtn = document.getElementById('resetBtn');

function showDeleteModal() {
  document.getElementById('confirmDeleteModal').style.display = 'flex';
}

function hideDeleteModal() {
  document.getElementById('confirmDeleteModal').style.display = 'none';
}

// Fermer le modal si clic extérieur
window.onclick = function (event) {
  const modal = document.getElementById('confirmDeleteModal');
  if (event.target === modal) hideDeleteModal();
};

async function fetchFlows() {
  try {
    const res = await fetch('/flows_json');
    if (!res.ok) {
      console.error('Erreur HTTP:', res.status, res.statusText);
      throw new Error(`Erreur HTTP ${res.status}`);
    }
    const data = await res.json();
    console.log('Données reçues:', data.length, 'flows');
    console.log('Premier flow:', data[0]); // Debug pour voir la structure
    return data;
  } catch (err) {
    console.error('Erreur fetch:', err);
    flowsBody.innerHTML = '<tr><td colspan="8" class="empty">Erreur de connexion au serveur.</td></tr>';
    return [];
  }
}

function formatProbability(p) {
  if (p === null || p === undefined) return '-';
  return (Number(p) * 100).toFixed(1) + '%';
}

function formatTimestamp(ts) {
  if (!ts) return '-';
  return ts;
}


function renderFlows(flows) {
  const search = searchInput.value.trim().toLowerCase();
  const verdictFilter = verdictSelect.value;
  const actionFilter = actionSelect.value;

  console.log('Filtrage:', { 
    search, 
    verdictFilter, 
    actionFilter, 
    totalFlows: flows.length 
  });

  const filtered = flows.filter(f => {
    // IMPORTANT: utiliser src_ip et dst_ip (noms MySQL)
    const matchSearch =
      !search ||
      (f.src_ip && f.src_ip.toLowerCase().includes(search)) ||
      (f.dst_ip && f.dst_ip.toLowerCase().includes(search)) ||
      String(f.src_port || '').includes(search) ||
      String(f.dst_port || '').includes(search) ||
      (f.verdict && f.verdict.toLowerCase().includes(search)) ||
      (f.action && f.action.toLowerCase().includes(search));

    const matchVerdict = !verdictFilter || f.verdict === verdictFilter;
    const matchAction = !actionFilter || f.action === actionFilter;

    return matchSearch && matchVerdict && matchAction;
  });

  console.log('Flows filtrés:', filtered.length);

  flowsBody.innerHTML = '';

  if (!filtered.length) {
    const message = flows.length === 0 
      ? 'Aucun flux dans la base de données.' 
      : 'Aucun flux ne correspond aux critères de recherche.';
    flowsBody.innerHTML = `<tr><td colspan="8" class="empty">${message}</td></tr>`;
    return;
  }

  filtered.forEach(f => {
    const tr = document.createElement('tr');
    
    // Ajouter classe 'ddos-row' si verdict = DDoS
    if (f.verdict && f.verdict.toLowerCase() === 'ddos') {
      tr.classList.add('ddos-row');
    }

    tr.innerHTML = `
      <td>${formatTimestamp(f.timestamp)}</td>
      <td>${f.src_ip || '-'}</td>
      <td>${f.dst_ip || '-'}</td>
      <td>${f.src_port || '-'}</td>
      <td>${f.dst_port || '-'}</td>
      <td><strong>${f.verdict || '-'}</strong></td>
      <td>${formatProbability(f.probability)}</td>
      <td>${f.action || '-'}</td>
    `;

    flowsBody.appendChild(tr);
  });
}

async function chargerEtAfficher() {
  console.log('Chargement des flows...');
  const flows = await fetchFlows();
  renderFlows(flows);
}

// Initial + refresh auto
chargerEtAfficher();
setInterval(chargerEtAfficher, 5000);

applyBtn.addEventListener('click', e => {
  e.preventDefault();
  chargerEtAfficher();
});

resetBtn.addEventListener('click', () => {
  searchInput.value = '';
  verdictSelect.value = '';
  actionSelect.value = '';
  chargerEtAfficher();
});