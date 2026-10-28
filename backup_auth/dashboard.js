/**
 * ==============================================================================
 * MINDBLOOM — CAREGIVER DASHBOARD & PROGRESS ANALYTICS (PHASE 6)
 * Client-Side Logic for Caregiver Progress Monitoring
 * ==============================================================================
 */

document.addEventListener('DOMContentLoaded', () => {
  'use strict';

  /* --------------------------------------------------------------------------
   * 1. Configuration & Global State
   * -------------------------------------------------------------------------- */
  const API_BASE_URL = window.MINDBLOOM_API_URL || 'http://127.0.0.1:8000/api';
  const CURRENT_USER_ID = 1; // Maps to Grandma Rose (DEMO User #1)

  let allSessions = [];
  let currentFilter = 'all';
  let chartInstances = {};

  // DOM Elements
  const loadingEl = document.getElementById('dashboard-loading');
  const contentEl = document.getElementById('dashboard-content');
  const emptyStateEl = document.getElementById('dashboard-empty-state');
  const errorBannerEl = document.getElementById('dashboard-error-banner');
  const errorMsgEl = document.getElementById('dashboard-error-msg');
  const btnRefresh = document.getElementById('btn-refresh-dashboard');
  const btnRetry = document.getElementById('btn-error-retry');
  const patientLastActiveEl = document.getElementById('patient-last-active');

  // Summary Card Elements
  const elTotalGames = document.getElementById('summary-total-games');
  const elGamesBreakdown = document.getElementById('summary-games-breakdown');
  const elAvgScore = document.getElementById('summary-avg-score');
  const elAvgAccuracy = document.getElementById('summary-avg-accuracy');
  const elTotalMistakes = document.getElementById('summary-total-mistakes');
  const elAvgDuration = document.getElementById('summary-avg-duration');
  const elTotalHints = document.getElementById('summary-total-hints');

  // Table Elements
  const historyTableBody = document.getElementById('history-table-body');
  const filterButtons = document.querySelectorAll('.filter-btn');

  /* --------------------------------------------------------------------------
   * 2. Accessibility Controls (Font Sizing & High Contrast)
   * -------------------------------------------------------------------------- */
  const body = document.body;
  const btnFontNormal = document.getElementById('btn-font-normal');
  const btnFontLarge = document.getElementById('btn-font-large');
  const btnFontXLarge = document.getElementById('btn-font-xlarge');
  const btnHighContrast = document.getElementById('btn-high-contrast');

  const savedFontSize = localStorage.getItem('mindbloom_font_size');
  const savedContrast = localStorage.getItem('mindbloom_contrast');

  if (savedFontSize === 'large') applyFontSize('large');
  else if (savedFontSize === 'xlarge') applyFontSize('xlarge');
  if (savedContrast === 'high') enableHighContrast(true);

  function applyFontSize(size) {
    body.classList.remove('font-large', 'font-xlarge');
    if (btnFontNormal) btnFontNormal.classList.remove('active');
    if (btnFontLarge) btnFontLarge.classList.remove('active');
    if (btnFontXLarge) btnFontXLarge.classList.remove('active');

    if (size === 'large') {
      body.classList.add('font-large');
      if (btnFontLarge) btnFontLarge.classList.add('active');
      localStorage.setItem('mindbloom_font_size', 'large');
    } else if (size === 'xlarge') {
      body.classList.add('font-xlarge');
      if (btnFontXLarge) btnFontXLarge.classList.add('active');
      localStorage.setItem('mindbloom_font_size', 'xlarge');
    } else {
      if (btnFontNormal) btnFontNormal.classList.add('active');
      localStorage.setItem('mindbloom_font_size', 'normal');
    }
  }

  function enableHighContrast(enabled) {
    if (enabled) {
      body.classList.add('high-contrast');
      if (btnHighContrast) {
        btnHighContrast.setAttribute('aria-pressed', 'true');
        btnHighContrast.classList.add('active');
      }
      localStorage.setItem('mindbloom_contrast', 'high');
    } else {
      body.classList.remove('high-contrast');
      if (btnHighContrast) {
        btnHighContrast.setAttribute('aria-pressed', 'false');
        btnHighContrast.classList.remove('active');
      }
      localStorage.setItem('mindbloom_contrast', 'normal');
    }
    // Re-render charts with contrast-aware colors if needed
    if (allSessions.length > 0) {
      fetchProgressAndRenderCharts();
    }
  }

  if (btnFontNormal) btnFontNormal.addEventListener('click', () => applyFontSize('normal'));
  if (btnFontLarge) btnFontLarge.addEventListener('click', () => applyFontSize('large'));
  if (btnFontXLarge) btnFontXLarge.addEventListener('click', () => applyFontSize('xlarge'));
  if (btnHighContrast) {
    btnHighContrast.addEventListener('click', () => {
      enableHighContrast(!body.classList.contains('high-contrast'));
    });
  }

  // Mobile Menu Toggle
  const menuToggle = document.getElementById('menu-toggle');
  const navMenu = document.getElementById('nav-menu');
  if (menuToggle && navMenu) {
    menuToggle.addEventListener('click', () => {
      const isOpen = navMenu.classList.toggle('is-open');
      menuToggle.setAttribute('aria-expanded', isOpen.toString());
    });
  }

  /* --------------------------------------------------------------------------
   * 3. Utility Helpers
   * -------------------------------------------------------------------------- */
  function formatSeconds(secs) {
    const s = Math.round(secs);
    const m = Math.floor(s / 60);
    const rem = s % 60;
    if (m === 0) return `${s}s`;
    return `${m}m ${rem}s`;
  }

  function formatDateTime(isoString) {
    if (!isoString) return '—';
    try {
      const dt = new Date(isoString);
      if (isNaN(dt.getTime())) return isoString;
      return dt.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return isoString;
    }
  }

  /* --------------------------------------------------------------------------
   * 4. Data Fetching & Dashboard Controller
   * -------------------------------------------------------------------------- */
  async function loadDashboardData() {
    showLoading();

    try {
      // Fetch summary and session history concurrently
      const [summaryRes, sessionsRes] = await Promise.all([
        fetch(`${API_BASE_URL}/analytics/summary?user_id=${CURRENT_USER_ID}`),
        fetch(`${API_BASE_URL}/game-sessions?user_id=${CURRENT_USER_ID}&limit=100`)
      ]);

      if (!summaryRes.ok || !sessionsRes.ok) {
        throw new Error(`Server returned HTTP ${summaryRes.status} / ${sessionsRes.status}`);
      }

      const summary = await summaryRes.json();
      const sessions = await sessionsRes.json();

      allSessions = Array.isArray(sessions) ? sessions : [];

      if (summary.total_games === 0 && allSessions.length === 0) {
        showEmptyState();
        return;
      }

      renderSummaryCards(summary);
      renderHistoryTable();
      await fetchProgressAndRenderCharts();

      showContent();
    } catch (err) {
      console.error('MindBloom Dashboard Load Error:', err);
      showError(err.message);
    }
  }

  /* --------------------------------------------------------------------------
   * 5. UI State Management
   * -------------------------------------------------------------------------- */
  function showLoading() {
    if (loadingEl) loadingEl.style.display = 'block';
    if (contentEl) contentEl.style.display = 'none';
    if (emptyStateEl) emptyStateEl.style.display = 'none';
    if (errorBannerEl) errorBannerEl.style.display = 'none';
  }

  function showContent() {
    if (loadingEl) loadingEl.style.display = 'none';
    if (contentEl) contentEl.style.display = 'block';
    if (emptyStateEl) emptyStateEl.style.display = 'none';
    if (errorBannerEl) errorBannerEl.style.display = 'none';
  }

  function showEmptyState() {
    if (loadingEl) loadingEl.style.display = 'none';
    if (contentEl) contentEl.style.display = 'none';
    if (emptyStateEl) emptyStateEl.style.display = 'block';
    if (errorBannerEl) errorBannerEl.style.display = 'none';
  }

  function showError(msg) {
    if (loadingEl) loadingEl.style.display = 'none';
    if (contentEl) contentEl.style.display = 'none';
    if (emptyStateEl) emptyStateEl.style.display = 'none';
    if (errorBannerEl) errorBannerEl.style.display = 'flex';
    if (errorMsgEl) {
      errorMsgEl.textContent = 'Unable to load caregiver analytics. Please ensure the MindBloom backend service is running on http://127.0.0.1:8000.';
    }
  }

  /* --------------------------------------------------------------------------
   * 6. Render Summary Cards
   * -------------------------------------------------------------------------- */
  function renderSummaryCards(summary) {
    if (elTotalGames) elTotalGames.textContent = summary.total_games;
    if (elGamesBreakdown) {
      const b = summary.games_by_difficulty || {};
      elGamesBreakdown.textContent = `${b.easy || 0} Easy • ${b.medium || 0} Medium • ${b.hard || 0} Hard`;
    }

    if (elAvgScore) elAvgScore.textContent = Math.round(summary.average_score);
    if (elAvgAccuracy) elAvgAccuracy.textContent = `${Math.round(summary.average_accuracy)}%`;
    if (elTotalMistakes) {
      elTotalMistakes.textContent = `${summary.total_mistakes} total mismatches recorded`;
    }

    if (elAvgDuration) elAvgDuration.textContent = formatSeconds(summary.average_response_time);
    if (elTotalHints) {
      elTotalHints.textContent = `${summary.total_hints_used} hint requests recorded`;
    }

    // Update patient last active label from newest session
    if (allSessions.length > 0 && patientLastActiveEl) {
      const newest = allSessions[0]; // Ordered created_at DESC
      patientLastActiveEl.textContent = `Last played: ${formatDateTime(newest.created_at || newest.completed_at)}`;
    }
  }

  /* --------------------------------------------------------------------------
   * 7. Render Charts via Chart.js with Pure Fallback
   * -------------------------------------------------------------------------- */
  async function fetchProgressAndRenderCharts() {
    try {
      const res = await fetch(`${API_BASE_URL}/analytics/progress?user_id=${CURRENT_USER_ID}&limit=30`);
      if (!res.ok) return;
      const progress = await res.json();
      renderCharts(progress);
    } catch (err) {
      console.warn('MindBloom: Could not fetch progress series for charts:', err);
    }
  }

  function renderCharts(progress) {
    if (typeof Chart === 'undefined') {
      console.info('MindBloom: Chart.js not loaded. Relying on tabular data.');
      return;
    }

    const isHighContrast = body.classList.contains('high-contrast');
    const primaryColor = isHighContrast ? '#FFFF00' : '#185D50';
    const secondaryColor = isHighContrast ? '#FFFFFF' : '#C85A17';
    const blueColor = isHighContrast ? '#FFFF00' : '#2563EB';
    const gridColor = isHighContrast ? '#333333' : '#ECE7DE';
    const textColor = isHighContrast ? '#FFFF00' : '#423d4c';

    // 1. Score Trend Chart
    const canvasScore = document.getElementById('chart-score-trend');
    if (canvasScore) {
      if (chartInstances.score) chartInstances.score.destroy();
      chartInstances.score = new Chart(canvasScore, {
        type: 'line',
        data: {
          labels: progress.labels,
          datasets: [{
            label: 'Game Score',
            data: progress.score_trend,
            borderColor: primaryColor,
            backgroundColor: isHighContrast ? 'transparent' : 'rgba(24, 93, 80, 0.08)',
            borderWidth: 3,
            pointBackgroundColor: primaryColor,
            pointRadius: 5,
            pointHoverRadius: 7,
            fill: true,
            tension: 0.3
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: {
                label: (ctx) => `Score: ${ctx.parsed.y} points`
              }
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              grid: { color: gridColor },
              ticks: { color: textColor, font: { family: 'Segoe UI', size: 12 } }
            },
            x: {
              grid: { display: false },
              ticks: { color: textColor, font: { family: 'Segoe UI', size: 12 } }
            }
          }
        }
      });
    }

    // 2. Difficulty Distribution (Doughnut Chart)
    const canvasDiff = document.getElementById('chart-diff-distribution');
    if (canvasDiff) {
      if (chartInstances.diff) chartInstances.diff.destroy();
      const dist = progress.difficulty_distribution || {};
      const easyCount = dist.easy || 0;
      const medCount = dist.medium || 0;
      const hardCount = dist.hard || 0;

      chartInstances.diff = new Chart(canvasDiff, {
        type: 'doughnut',
        data: {
          labels: ['Easy (8 cards)', 'Medium (12 cards)', 'Hard (16 cards)'],
          datasets: [{
            data: [easyCount, medCount, hardCount],
            backgroundColor: isHighContrast 
              ? ['#FFFF00', '#FFFFFF', '#888888']
              : ['#10B981', '#F59E0B', '#EF4444'],
            borderWidth: 2,
            borderColor: isHighContrast ? '#000000' : '#FFFFFF'
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'bottom',
              labels: { color: textColor, font: { family: 'Segoe UI', size: 12 } }
            }
          }
        }
      });
    }

    // 3. Accuracy Trend Chart (Line Chart with Benchmark)
    const canvasAcc = document.getElementById('chart-accuracy-trend');
    if (canvasAcc) {
      if (chartInstances.accuracy) chartInstances.accuracy.destroy();
      chartInstances.accuracy = new Chart(canvasAcc, {
        type: 'line',
        data: {
          labels: progress.labels,
          datasets: [{
            label: 'Accuracy (%)',
            data: progress.accuracy_trend,
            borderColor: secondaryColor,
            backgroundColor: isHighContrast ? 'transparent' : 'rgba(200, 90, 23, 0.08)',
            borderWidth: 3,
            pointBackgroundColor: secondaryColor,
            pointRadius: 5,
            fill: true,
            tension: 0.25
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: {
                label: (ctx) => `Accuracy: ${ctx.parsed.y}%`
              }
            }
          },
          scales: {
            y: {
              min: 0,
              max: 100,
              grid: { color: gridColor },
              ticks: {
                callback: (v) => `${v}%`,
                color: textColor,
                font: { family: 'Segoe UI', size: 12 }
              }
            },
            x: {
              grid: { display: false },
              ticks: { color: textColor, font: { family: 'Segoe UI', size: 12 } }
            }
          }
        }
      });
    }

    // 4. Response Time (Duration) Trend Chart
    const canvasTime = document.getElementById('chart-time-trend');
    if (canvasTime) {
      if (chartInstances.time) chartInstances.time.destroy();
      chartInstances.time = new Chart(canvasTime, {
        type: 'bar',
        data: {
          labels: progress.labels,
          datasets: [{
            label: 'Duration (Seconds)',
            data: progress.response_time_trend,
            backgroundColor: isHighContrast ? '#FFFF00' : 'rgba(37, 99, 235, 0.75)',
            borderColor: blueColor,
            borderWidth: 1,
            borderRadius: 6
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: {
                label: (ctx) => `Time: ${ctx.parsed.y} seconds`
              }
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              grid: { color: gridColor },
              ticks: {
                callback: (v) => `${v}s`,
                color: textColor,
                font: { family: 'Segoe UI', size: 12 }
              }
            },
            x: {
              grid: { display: false },
              ticks: { color: textColor, font: { family: 'Segoe UI', size: 12 } }
            }
          }
        }
      });
    }
  }

  /* --------------------------------------------------------------------------
   * 8. Render Game Session History Table
   * -------------------------------------------------------------------------- */
  function renderHistoryTable() {
    if (!historyTableBody) return;
    historyTableBody.innerHTML = '';

    const filtered = currentFilter === 'all'
      ? allSessions
      : allSessions.filter(s => strDiff(s.difficulty) === currentFilter);

    const historyCountEl = document.getElementById('history-count');
    if (historyCountEl) {
      historyCountEl.textContent = `${filtered.length} session${filtered.length === 1 ? '' : 's'} (${currentFilter.toUpperCase()})`;
    }

    if (filtered.length === 0) {
      historyTableBody.innerHTML = `
        <tr>
          <td colspan="8" style="text-align: center; padding: 30px; color: var(--color-text-muted);">
            No sessions match the selected difficulty filter (${currentFilter.toUpperCase()}).
          </td>
        </tr>
      `;
      return;
    }

    filtered.forEach((session, index) => {
      const tr = document.createElement('tr');
      const diffClean = strDiff(session.difficulty);
      const diffBadge = `<span class="diff-tag tag-${diffClean}">${diffClean}</span>`;

      let aiBadge = `<span style="color: #9CA3AF;">—</span>`;
      if (session.recommended_difficulty) {
        const recClean = strDiff(session.recommended_difficulty);
        aiBadge = `<span class="ai-rec-tag" title="Recommended by AI for next round">🧠 ${recClean.toUpperCase()}</span>`;
      }

      const accVal = parseFloat(session.accuracy || 0).toFixed(1);
      const scoreVal = session.score || 0;
      const mistakesVal = session.mistakes !== undefined ? session.mistakes : '—';
      const durationVal = session.response_time ? `${session.response_time}s` : '—';
      const dateFormatted = formatDateTime(session.created_at || session.completed_at);

      tr.innerHTML = `
        <td><strong>#${allSessions.length - index}</strong></td>
        <td>${dateFormatted}</td>
        <td>${diffBadge}</td>
        <td><strong style="color: var(--color-primary-dark);">${scoreVal}</strong></td>
        <td><strong>${accVal}%</strong></td>
        <td>${mistakesVal}</td>
        <td>${durationVal}</td>
        <td>${aiBadge}</td>
      `;

      historyTableBody.appendChild(tr);
    });
  }

  function strDiff(val) {
    if (!val) return 'easy';
    return String(val).trim().toLowerCase();
  }

  /* --------------------------------------------------------------------------
   * 9. Filter Handlers & Refresh Listener
   * -------------------------------------------------------------------------- */
  filterButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      filterButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentFilter = btn.getAttribute('data-filter') || 'all';
      renderHistoryTable();
    });
  });

  if (btnRefresh) {
    btnRefresh.addEventListener('click', () => {
      console.log('MindBloom: Refreshing dashboard data...');
      loadDashboardData();
    });
  }

  if (btnRetry) {
    btnRetry.addEventListener('click', () => {
      loadDashboardData();
    });
  }

  // Initial Data Load
  loadDashboardData();

  console.log('MindBloom Phase 6: Caregiver Dashboard initialized.');
});
