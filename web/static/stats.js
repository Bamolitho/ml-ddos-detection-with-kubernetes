// =========================================================
// CONFIGURATION
// =========================================================
const REFRESH_INTERVAL = 5000; // 5 secondes
let chart = null;

// =========================================================
// FETCH STATISTIQUES
// =========================================================
async function fetchStats() {
  try {
    const res = await fetch('/stats_json');
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    console.log('✅ Stats reçues:', data);
    return data;
  } catch (err) {
    console.error('❌ Erreur fetch stats:', err);
    return null;
  }
}

// =========================================================
// CALCUL DES MÉTRIQUES
// =========================================================
function calculateMetrics(stats) {
  // Vrai Positif (VP) : DDoS détecté ET bloqué
  const truePositive = stats.ddos_blocked || 0;
  
  // Faux Positif (FP) : DDoS détecté mais PAS bloqué
  const falsePositive = stats.ddos_passed || 0;
  
  // Vrai Négatif (VN) : Benign détecté ET passé
  const trueNegative = stats.benign_passed || 0;
  
  // Faux Négatif (FN) : Benign bloqué à tort
  const falseNegative = stats.benign_blocked || 0;

  const total = truePositive + falsePositive + trueNegative + falseNegative;

  // Précision = VP / (VP + FP)
  const precision = (truePositive + falsePositive) > 0 
    ? (truePositive / (truePositive + falsePositive) * 100).toFixed(1)
    : 0;

  // Rappel = VP / (VP + FN)
  const recall = (truePositive + falseNegative) > 0
    ? (truePositive / (truePositive + falseNegative) * 100).toFixed(1)
    : 0;

  // F1-Score = 2 * (Précision * Rappel) / (Précision + Rappel)
  const f1Score = (parseFloat(precision) + parseFloat(recall)) > 0
    ? (2 * (parseFloat(precision) * parseFloat(recall)) / (parseFloat(precision) + parseFloat(recall))).toFixed(1)
    : 0;

  return {
    truePositive,
    falsePositive,
    trueNegative,
    falseNegative,
    total,
    precision,
    recall,
    f1Score
  };
}

// =========================================================
// MISE À JOUR DES CARTES STATISTIQUES
// =========================================================
function updateStatsCards(stats, metrics) {
  // Total
  document.getElementById('stat-total').textContent = stats.total || 0;
  
  // Benign
  document.getElementById('stat-benign').textContent = stats.benign || 0;
  
  // DDoS
  document.getElementById('stat-ddos').textContent = stats.ddos || 0;
  
  // Bloqués
  document.getElementById('stat-blocked').textContent = stats.blocked || 0;

  // Métriques de performance
  document.getElementById('stat-precision').textContent = metrics.precision + '%';
  document.getElementById('stat-recall').textContent = metrics.recall + '%';
  document.getElementById('stat-f1').textContent = metrics.f1Score + '%';
}

// =========================================================
// MISE À JOUR DU TABLEAU
// =========================================================
function updateTable(metrics) {
  document.getElementById('metric-vp').textContent = metrics.truePositive;
  document.getElementById('metric-fp').textContent = metrics.falsePositive;
  document.getElementById('metric-vn').textContent = metrics.trueNegative;
  document.getElementById('metric-fn').textContent = metrics.falseNegative;
}

// =========================================================
// GRAPHIQUE CHART.JS
// =========================================================
function updateChart(metrics) {
  const ctx = document.getElementById('confusionChart').getContext('2d');

  const data = {
    labels: [
      `Vrai Positif (${metrics.truePositive})`,
      `Faux Positif (${metrics.falsePositive})`,
      `Vrai Négatif (${metrics.trueNegative})`,
      `Faux Négatif (${metrics.falseNegative})`
    ],
    datasets: [{
      data: [
        metrics.truePositive,
        metrics.falsePositive,
        metrics.trueNegative,
        metrics.falseNegative
      ],
      backgroundColor: [
        '#d42506', // Vert - Vrai Positif (DDoS bloqué)
        '#f5f10b', // Jaune - Faux Positif (DDoS non bloqué)
        '#10b981', // Bleu - Vrai Négatif (Benign passé)
        '#000000'  // Noir - Faux Négatif (Benign bloqué)
      ],
      borderColor: '#ffffff',
      borderWidth: 3
    }]
  };

  const config = {
    type: 'doughnut',
    data: data,
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            font: { size: 13, family: 'system-ui' },
            padding: 15,
            usePointStyle: true
          }
        },
        tooltip: {
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          padding: 12,
          titleFont: { size: 14, weight: 'bold' },
          bodyFont: { size: 13 },
          callbacks: {
            label: function(context) {
              const total = context.dataset.data.reduce((a, b) => a + b, 0);
              const value = context.parsed;
              const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
              return ` ${value} flux (${percentage}%)`;
            }
          }
        }
      }
    }
  };

  // Détruire le graphique existant si nécessaire
  if (chart) {
    chart.destroy();
  }

  chart = new Chart(ctx, config);
}

// =========================================================
// MISE À JOUR COMPLÈTE
// =========================================================
async function updateAll() {
  const stats = await fetchStats();
  if (!stats) return;

  const metrics = calculateMetrics(stats);

  updateStatsCards(stats, metrics);
  updateTable(metrics);
  updateChart(metrics);

  // Mise à jour du timestamp
  const now = new Date().toLocaleString('fr-CA', {
    timeZone: 'America/Montreal',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });
  document.getElementById('last-update').textContent = `Dernière mise à jour : ${now}`;
}

// =========================================================
// INITIALISATION
// =========================================================
document.addEventListener('DOMContentLoaded', () => {
  console.log('📊 Initialisation des statistiques...');
  
  // Première mise à jour
  updateAll();
  
  // Mise à jour automatique
  setInterval(updateAll, REFRESH_INTERVAL);
  
  console.log(`✅ Auto-refresh activé (${REFRESH_INTERVAL / 1000}s)`);
});