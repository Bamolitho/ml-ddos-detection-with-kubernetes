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
    if (!res.ok) throw new Error('Erreur lors du fetch des flux');
    return await res.json();
  } catch (err) {
    console.error(err);
    return [];
  }
}

function formatProbability(p) {
  if (p === null || p === undefined) return '-';
  return (Number(p) * 100).toFixed(1) + '%';
}

function renderFlows(flows) {
  const search = searchInput.value.trim().toLowerCase();
  const verdictFilter = verdictSelect.value;
  const actionFilter = actionSelect.value;

  const filtered = flows.filter(f => {
    const matchSearch =
      !search ||
      (f.source_ip && f.source_ip.toLowerCase().includes(search)) ||
      (f.destination_ip && f.destination_ip.toLowerCase().includes(search)) ||
      String(f.source_port || '').includes(search) ||
      String(f.destination_port || '').includes(search) ||
      (f.verdict && f.verdict.toLowerCase().includes(search)) ||
      (f.action && f.action.toLowerCase().includes(search));

    const matchVerdict = !verdictFilter || f.verdict === verdictFilter;
    const matchAction = !actionFilter || f.action === actionFilter;

    return matchSearch && matchVerdict && matchAction;
  });

  flowsBody.innerHTML = '';

  if (!filtered.length) {
    flowsBody.innerHTML =
      '<tr><td colspan="8" class="empty">Aucun flux trouvé.</td></tr>';
    return;
  }

  filtered.forEach(f => {
    const tr = document.createElement('tr');

    let ts = f.timestamp || f.Timestamp || '';
    try {
      const d = new Date(ts * 1000);
      if (!isNaN(d.getTime())) ts = d.toLocaleString();
      else {
        const d2 = new Date(ts);
        if (!isNaN(d2.getTime())) ts = d2.toLocaleString();
      }
    } catch {}

    tr.innerHTML = `
      <td>${ts}</td>
      <td>${f.source_ip || f["Source IP"] || '-'}</td>
      <td>${f.destination_ip || f["Destination IP"] || '-'}</td>
      <td>${f.source_port || f["Source Port"] || '-'}</td>
      <td>${f.destination_port || f["Destination Port"] || '-'}</td>
      <td>${f.verdict || '-'}</td>
      <td>${formatProbability(f.probability)}</td>
      <td>${f.action || '-'}</td>
    `;

    flowsBody.appendChild(tr);
  });
}

async function chargerEtAfficher() {
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
