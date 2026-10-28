/**
 * ==========================================================================
 * MINDBLOOM - JAVASCRIPT (PHASE 1 FOUNDATION)
 * AI-Powered Cognitive & Memory Assistance Platform
 * 
 * Scope: Frontend interactions, accessibility controls, navigation,
 * and login UI state management.
 * Note: AI/ML, backend API calls, and database operations are strictly
 * reserved for subsequent phases.
 * ==========================================================================
 */

document.addEventListener('DOMContentLoaded', () => {
  'use strict';

  /* --------------------------------------------------------------------------
   * 1. Accessibility Controls (Font Sizing & High Contrast)
   * -------------------------------------------------------------------------- */
  const btnFontNormal = document.getElementById('btn-font-normal');
  const btnFontLarge = document.getElementById('btn-font-large');
  const btnFontXLarge = document.getElementById('btn-font-xlarge');
  const btnHighContrast = document.getElementById('btn-high-contrast');
  const body = document.body;

  // Restore saved accessibility preferences
  const savedFontSize = localStorage.getItem('mindbloom_font_size');
  const savedContrast = localStorage.getItem('mindbloom_contrast');

  if (savedFontSize === 'large') {
    applyFontSize('large');
  } else if (savedFontSize === 'xlarge') {
    applyFontSize('xlarge');
  }

  if (savedContrast === 'high') {
    enableHighContrast(true);
  }

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
  }

  if (btnFontNormal) {
    btnFontNormal.addEventListener('click', () => applyFontSize('normal'));
  }
  if (btnFontLarge) {
    btnFontLarge.addEventListener('click', () => applyFontSize('large'));
  }
  if (btnFontXLarge) {
    btnFontXLarge.addEventListener('click', () => applyFontSize('xlarge'));
  }
  if (btnHighContrast) {
    btnHighContrast.addEventListener('click', () => {
      const isCurrentlyHigh = body.classList.contains('high-contrast');
      enableHighContrast(!isCurrentlyHigh);
    });
  }

  /* --------------------------------------------------------------------------
   * 2. Mobile Navigation Toggle
   * -------------------------------------------------------------------------- */
  const menuToggle = document.getElementById('menu-toggle');
  const navMenu = document.getElementById('nav-menu');
  const navLinks = document.querySelectorAll('.nav-link, .nav-login-btn');

  if (menuToggle && navMenu) {
    menuToggle.addEventListener('click', () => {
      const isOpen = navMenu.classList.toggle('is-open');
      menuToggle.setAttribute('aria-expanded', isOpen.toString());
    });

    // Close menu when clicking any nav link
    navLinks.forEach(link => {
      link.addEventListener('click', () => {
        if (navMenu.classList.contains('is-open')) {
          navMenu.classList.remove('is-open');
          menuToggle.setAttribute('aria-expanded', 'false');
        }
      });
    });

    // Close menu when clicking outside
    document.addEventListener('click', (event) => {
      if (!navMenu.contains(event.target) && !menuToggle.contains(event.target)) {
        if (navMenu.classList.contains('is-open')) {
          navMenu.classList.remove('is-open');
          menuToggle.setAttribute('aria-expanded', 'false');
        }
      }
    });
  }

  /* --------------------------------------------------------------------------
   * 3. Active Link Highlight on Scroll
   * -------------------------------------------------------------------------- */
  const sections = document.querySelectorAll('section[id]');
  window.addEventListener('scroll', () => {
    const scrollY = window.pageYOffset + 120;

    sections.forEach(current => {
      const sectionHeight = current.offsetHeight;
      const sectionTop = current.offsetTop;
      const sectionId = current.getAttribute('id');
      const targetLink = document.querySelector(`.nav-menu a[href*="#${sectionId}"]`);

      if (targetLink) {
        if (scrollY >= sectionTop && scrollY < sectionTop + sectionHeight) {
          targetLink.classList.add('active');
        } else {
          targetLink.classList.remove('active');
        }
      }
    });
  });

  /* --------------------------------------------------------------------------
   * 4. Login UI - User Type Selector
   * -------------------------------------------------------------------------- */
  const typeButtons = document.querySelectorAll('.type-btn');
  const userInputLabel = document.getElementById('user-input-label');
  const userInput = document.getElementById('login-username');
  const userRoleInput = document.getElementById('selected-role');
  const roleHelpText = document.getElementById('role-help-text');

  typeButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      typeButtons.forEach(b => {
        b.classList.remove('active');
        b.setAttribute('aria-pressed', 'false');
      });

      btn.classList.add('active');
      btn.setAttribute('aria-pressed', 'true');

      const selectedRole = btn.getAttribute('data-role');
      if (userRoleInput) userRoleInput.value = selectedRole;

      // Adjust UI labels according to target role for clear UX
      if (selectedRole === 'patient') {
        if (userInputLabel) userInputLabel.textContent = 'Elderly User ID or Name:';
        if (userInput) userInput.placeholder = 'e.g., patient01 or Grandma Rose';
        if (roleHelpText) roleHelpText.textContent = 'Logging in as an Elderly User to access games and daily reminders.';
      } else {
        if (userInputLabel) userInputLabel.textContent = 'Caregiver Email or Username:';
        if (userInput) userInput.placeholder = 'e.g., caregiver@example.com';
        if (roleHelpText) roleHelpText.textContent = 'Logging in as Caregiver to view patient progress, game history, and alerts.';
      }

      // Reset feedback messages when switching roles
      clearFeedback();
    });
  });

  /* --------------------------------------------------------------------------
   * 5. Password Visibility Toggle
   * -------------------------------------------------------------------------- */
  const togglePasswordBtn = document.getElementById('toggle-password');
  const passwordInput = document.getElementById('login-password');

  if (togglePasswordBtn && passwordInput) {
    togglePasswordBtn.addEventListener('click', () => {
      const isPassword = passwordInput.type === 'password';
      passwordInput.type = isPassword ? 'text' : 'password';
      togglePasswordBtn.textContent = isPassword ? 'Hide' : 'Show';
      togglePasswordBtn.setAttribute('aria-label', isPassword ? 'Hide password' : 'Show password');
    });
  }

  /* --------------------------------------------------------------------------
   * 6. Login Form Submission (UI Demonstration Only)
   * -------------------------------------------------------------------------- */
  const loginForm = document.getElementById('login-form');
  const formFeedback = document.getElementById('form-feedback');

  function clearFeedback() {
    if (formFeedback) {
      formFeedback.className = 'form-feedback';
      formFeedback.textContent = '';
      formFeedback.style.display = 'none';
    }
  }

  if (loginForm && formFeedback) {
    loginForm.addEventListener('submit', (e) => {
      e.preventDefault();

      const usernameVal = userInput ? userInput.value.trim() : '';
      const passwordVal = passwordInput ? passwordInput.value.trim() : '';
      const role = userRoleInput ? userRoleInput.value : 'patient';
      const roleName = role === 'patient' ? 'Elderly User' : 'Caregiver';

      // Simple UI validation
      if (!usernameVal || !passwordVal) {
        formFeedback.className = 'form-feedback error';
        formFeedback.textContent = '⚠️ Please enter both your username/email and password.';
        formFeedback.style.display = 'block';
        return;
      }

      // Display friendly Phase 1 prototype message
      formFeedback.className = 'form-feedback info';
      formFeedback.innerHTML = `
        <strong>✓ Phase 1 UI Demonstration:</strong><br>
        Form inputs accepted for <em>${roleName} (${usernameVal})</em>.<br>
        Backend authentication, FastAPI REST endpoints, and SQL database will be connected in subsequent phases.
      `;
      formFeedback.style.display = 'block';
    });
  }

  /* --------------------------------------------------------------------------
   * 7. Interactive Hero Preview Tiles (Demonstration Widget)
   * -------------------------------------------------------------------------- */
  const previewTiles = document.querySelectorAll('.preview-tile');
  const previewStatusText = document.getElementById('preview-status-text');

  let matchCount = 0;
  previewTiles.forEach(tile => {
    tile.addEventListener('click', () => {
      if (!tile.classList.contains('matched')) {
        tile.classList.add('matched');
        matchCount++;
        if (previewStatusText) {
          previewStatusText.textContent = `Demo: ${matchCount} cards explored! Play the full game below ↓`;
        }
      }
    });
  });

  /* ==========================================================================
   * 8. MEMORY MATCH COGNITIVE GAME (PHASE 2)
   * ========================================================================== */

  // Available Card Symbols with clear visual emojis and friendly text labels
  const ALL_CARD_SYMBOLS = [
    { id: 'flower', emoji: '🌸', name: 'Flower' },
    { id: 'apple',  emoji: '🍎', name: 'Apple' },
    { id: 'sun',    emoji: '☀️', name: 'Sun' },
    { id: 'bell',   emoji: '🔔', name: 'Bell' },
    { id: 'tree',   emoji: '🌳', name: 'Tree' },
    { id: 'cup',    emoji: '☕', name: 'Tea Cup' },
    { id: 'house',  emoji: '🏠', name: 'House' },
    { id: 'bird',   emoji: '🕊️', name: 'Dove' }
  ];

  // Difficulty Configurations (Manually selected in Phase 2)
  const DIFFICULTY_SETTINGS = {
    easy:   { pairs: 4, gridClass: 'grid-easy',   name: 'Easy' },
    medium: { pairs: 6, gridClass: 'grid-medium', name: 'Medium' },
    hard:   { pairs: 8, gridClass: 'grid-hard',   name: 'Hard' }
  };

  // Backend API Configuration (Phase 3 Integration)
  const API_BASE_URL = window.MINDBLOOM_API_URL || 'http://127.0.0.1:8000/api';
  // Active demo user ID for prototype testing (Maps to Grandma Rose - DEMO User #1)
  const CURRENT_USER_ID = 1;

  // Game State Variables
  let currentDifficulty = 'easy';
  let totalPairs = 4;
  let matchedPairs = 0;
  let attempts = 0;
  let mistakes = 0;
  let score = 0;
  let hintsUsed = 0;
  let secondsElapsed = 0;
  let timerInterval = null;
  let gameStarted = false;
  let isChecking = false;
  let firstCard = null;
  let secondCard = null;
  let cardsData = [];
  let isHintActive = false;
  let gameStartTime = null;
  let gameEndTime = null;
  let recommendedDifficulty = null;
  let clientSessionId = null;

  // DOM Elements
  const gameBoard = document.getElementById('game-board');
  const btnStartGame = document.getElementById('btn-start-game');
  const btnRestartGame = document.getElementById('btn-restart-game');
  const btnHintGame = document.getElementById('btn-hint-game');
  const diffButtons = document.querySelectorAll('.btn-diff');

  // Stats DOM Elements
  const statScore = document.getElementById('stat-score');
  const statTimer = document.getElementById('stat-timer');
  const statMatched = document.getElementById('stat-matched');
  const statAttempts = document.getElementById('stat-attempts');
  const statMistakes = document.getElementById('stat-mistakes');
  const statAccuracy = document.getElementById('stat-accuracy');
  const statHints = document.getElementById('stat-hints');
  const gameSrStatus = document.getElementById('game-sr-status');

  // Modal DOM Elements
  const resultModal = document.getElementById('game-result-modal');
  const resScore = document.getElementById('res-score');
  const resAccuracy = document.getElementById('res-accuracy');
  const resTime = document.getElementById('res-time');
  const resDifficulty = document.getElementById('res-difficulty');
  const resAttempts = document.getElementById('res-attempts');
  const resMistakes = document.getElementById('res-mistakes');
  const resMatched = document.getElementById('res-matched');
  const resHints = document.getElementById('res-hints');
  const btnModalPlayAgain = document.getElementById('btn-modal-play-again');
  const btnModalClose = document.getElementById('btn-modal-close');

  // Phase 5 AI Adaptive Recommendation DOM Elements
  const aiRecCard = document.getElementById('ai-rec-card');
  const aiRecLoading = document.getElementById('ai-rec-loading');
  const aiRecContent = document.getElementById('ai-rec-content');
  const aiRecFallback = document.getElementById('ai-rec-fallback');
  const aiRecDifficultyBadge = document.getElementById('ai-rec-difficulty-badge');
  const aiRecConfidence = document.getElementById('ai-rec-confidence');
  const aiRecMessage = document.getElementById('ai-rec-message');
  const recCurrentDiff = document.getElementById('rec-current-diff');
  const recNextDiff = document.getElementById('rec-next-diff');
  const btnRecDiffText = document.getElementById('btn-rec-diff-text');
  const btnModalPlayRecommended = document.getElementById('btn-modal-play-recommended');

  /**
   * Updates Difficulty selection
   */
  function setDifficulty(level) {
    if (!DIFFICULTY_SETTINGS[level]) return;
    currentDifficulty = level;
    totalPairs = DIFFICULTY_SETTINGS[level].pairs;

    diffButtons.forEach(btn => {
      const isActive = btn.getAttribute('data-difficulty') === level;
      btn.classList.toggle('active', isActive);
      btn.setAttribute('aria-pressed', isActive.toString());
    });

    // Reset and start fresh with new difficulty
    initGame();
  }

  /**
   * Initializes or resets the game board and stats
   */
  function initGame() {
    stopTimer();
    secondsElapsed = 0;
    matchedPairs = 0;
    attempts = 0;
    mistakes = 0;
    score = 0;
    hintsUsed = 0;
    gameStarted = false;
    isChecking = false;
    firstCard = null;
    secondCard = null;
    isHintActive = false;
    gameStartTime = null;
    gameEndTime = null;

    // Reset database save status badge
    const saveStatusEl = document.getElementById('res-save-status');
    if (saveStatusEl) {
      saveStatusEl.style.display = 'none';
      saveStatusEl.className = 'res-save-status';
      saveStatusEl.textContent = '';
    }

    // Reset Phase 5 AI recommendation card state
    if (aiRecLoading) aiRecLoading.style.display = 'flex';
    if (aiRecContent) aiRecContent.style.display = 'none';
    if (aiRecFallback) aiRecFallback.style.display = 'none';
    if (btnModalPlayRecommended) btnModalPlayRecommended.style.display = 'none';
    recommendedDifficulty = null;

    totalPairs = DIFFICULTY_SETTINGS[currentDifficulty].pairs;

    updateStatsDisplay();
    createBoard();
    announceStatus(`Ready to play Memory Match on ${DIFFICULTY_SETTINGS[currentDifficulty].name} difficulty. ${totalPairs} pairs to find.`);
  }

  /**
   * Starts game actively (starts the timer)
   */
  function startGame() {
    if (!gameStarted) {
      gameStarted = true;
      gameStartTime = new Date();
      startTimer();
      announceStatus('Game started! Tap two cards to find matching pairs.');
    }
  }

  /**
   * Generates card deck based on difficulty and shuffles
   */
  function createCards() {
    const selectedSymbols = ALL_CARD_SYMBOLS.slice(0, totalPairs);
    // Duplicate each card to create pairs
    const deck = [];
    selectedSymbols.forEach(item => {
      deck.push({ ...item, uid: `${item.id}_a` });
      deck.push({ ...item, uid: `${item.id}_b` });
    });
    return shuffleCards(deck);
  }

  /**
   * Fisher-Yates shuffle algorithm
   */
  function shuffleCards(array) {
    const shuffled = [...array];
    for (let i = shuffled.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled;
  }

  /**
   * Creates DOM elements for cards and attaches to board
   */
  function createBoard() {
    if (!gameBoard) return;
    gameBoard.innerHTML = '';
    
    // Apply grid template class
    gameBoard.className = `game-board ${DIFFICULTY_SETTINGS[currentDifficulty].gridClass}`;
    cardsData = createCards();

    cardsData.forEach((card, index) => {
      const cardBtn = document.createElement('button');
      cardBtn.type = 'button';
      cardBtn.className = 'memory-card';
      cardBtn.setAttribute('data-index', index.toString());
      cardBtn.setAttribute('data-symbol', card.id);
      cardBtn.setAttribute('data-name', card.name);
      cardBtn.setAttribute('aria-label', `Card ${index + 1} face down`);

      cardBtn.innerHTML = `
        <div class="card-inner">
          <div class="card-face card-back">
            <svg class="card-back-icon" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
              <circle cx="24" cy="24" r="20" fill="#FFFFFF" stroke="#185D50" stroke-width="2.5"/>
              <path d="M24 14C21 14 19 17 19 20C19 23 24 28 24 28C24 28 29 23 29 20C29 17 27 14 24 14Z" fill="#C85A17"/>
              <circle cx="24" cy="24" r="3" fill="#FEF9E7"/>
            </svg>
            <span class="card-back-text">Tap</span>
          </div>
          <div class="card-face card-front">
            <span class="card-symbol" aria-hidden="true">${card.emoji}</span>
            <span class="card-label">${card.name}</span>
          </div>
        </div>
      `;

      cardBtn.addEventListener('click', () => handleCardClick(cardBtn));
      gameBoard.appendChild(cardBtn);
    });
  }

  /**
   * Handles user tapping on a card
   */
  function handleCardClick(cardBtn) {
    // If checking two cards or hint is running, ignore clicks
    if (isChecking || isHintActive) return;

    // Start timer on first card interaction if not already running
    if (!gameStarted) {
      startGame();
    }

    // Ignore if already flipped or matched
    if (cardBtn.classList.contains('flipped') || cardBtn.classList.contains('matched')) {
      return;
    }

    // Flip the selected card
    flipCard(cardBtn);

    if (!firstCard) {
      // First card chosen
      firstCard = cardBtn;
      announceStatus(`First card revealed: ${cardBtn.dataset.name}`);
    } else {
      // Second card chosen
      secondCard = cardBtn;
      attempts++;
      isChecking = true;
      announceStatus(`Second card revealed: ${cardBtn.dataset.name}`);

      checkMatch();
    }
  }

  /**
   * Reveals a card visually and updates aria attributes
   */
  function flipCard(cardBtn) {
    cardBtn.classList.add('flipped');
    cardBtn.setAttribute('aria-label', `Card revealed: ${cardBtn.dataset.name}`);
  }

  /**
   * Evaluates if firstCard and secondCard match
   */
  function checkMatch() {
    const isMatch = firstCard.dataset.symbol === secondCard.dataset.symbol;

    if (isMatch) {
      // Match found!
      matchedPairs++;
      score += 100;

      // Lock matched cards
      firstCard.classList.add('matched');
      secondCard.classList.add('matched');

      // Add checkmark badge for accessible visual confirmation
      addMatchBadge(firstCard);
      addMatchBadge(secondCard);

      firstCard.setAttribute('aria-label', `Matched: ${firstCard.dataset.name}`);
      secondCard.setAttribute('aria-label', `Matched: ${secondCard.dataset.name}`);

      announceStatus(`Wonderful! You matched ${firstCard.dataset.name}!`);

      resetSelection();
      updateStatsDisplay();

      // Check if all pairs are completed
      if (matchedPairs === totalPairs) {
        endGame();
      }
    } else {
      // Mismatch
      mistakes++;
      score = Math.max(0, score - 15);
      
      firstCard.classList.add('mismatch');
      secondCard.classList.add('mismatch');

      announceStatus(`Not a match. Showing cards briefly.`);
      updateStatsDisplay();

      // Give elderly users a comfortable 1.2 second pause to view cards
      setTimeout(() => {
        if (firstCard && secondCard) {
          firstCard.classList.remove('flipped', 'mismatch');
          secondCard.classList.remove('flipped', 'mismatch');
          firstCard.setAttribute('aria-label', `Card ${parseInt(firstCard.dataset.index) + 1} face down`);
          secondCard.setAttribute('aria-label', `Card ${parseInt(secondCard.dataset.index) + 1} face down`);
        }
        resetSelection();
      }, 1200);
    }
  }

  /**
   * Resets card selections and unlocks board
   */
  function resetSelection() {
    firstCard = null;
    secondCard = null;
    isChecking = false;
  }

  /**
   * Adds match indicator badge
   */
  function addMatchBadge(cardBtn) {
    const front = cardBtn.querySelector('.card-face.card-front');
    if (front && !front.querySelector('.matched-badge')) {
      const badge = document.createElement('span');
      badge.className = 'matched-badge';
      badge.innerHTML = '✓';
      badge.setAttribute('aria-hidden', 'true');
      front.appendChild(badge);
    }
  }

  /**
   * Calculates accuracy percentage
   */
  function calculateAccuracy() {
    if (attempts === 0) return 0;
    return Math.round((matchedPairs / attempts) * 100);
  }

  /**
   * Updates stats counters on screen
   */
  function updateStatsDisplay() {
    if (statScore) statScore.textContent = score;
    if (statTimer) statTimer.textContent = formatTime(secondsElapsed);
    if (statMatched) statMatched.textContent = `${matchedPairs} / ${totalPairs}`;
    if (statAttempts) statAttempts.textContent = attempts;
    if (statMistakes) statMistakes.textContent = mistakes;
    if (statAccuracy) statAccuracy.textContent = `${calculateAccuracy()}%`;
    if (statHints) statHints.textContent = hintsUsed;
  }

  /**
   * Formats seconds into mm:ss
   */
  function formatTime(totalSeconds) {
    const mins = Math.floor(totalSeconds / 60);
    const secs = totalSeconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }

  /**
   * Timer controls
   */
  function startTimer() {
    stopTimer();
    timerInterval = setInterval(() => {
      secondsElapsed++;
      if (statTimer) statTimer.textContent = formatTime(secondsElapsed);
    }, 1000);
  }

  function stopTimer() {
    if (timerInterval) {
      clearInterval(timerInterval);
      timerInterval = null;
    }
  }

  /**
   * Hint Functionality:
   * Briefly highlights one unmatched pair on the board
   */
  function provideHint() {
    if (isChecking || isHintActive) return;

    // Start timer if hint is clicked first
    if (!gameStarted) {
      startGame();
    }

    // Find all unmatched cards
    const unmatchedCards = Array.from(document.querySelectorAll('.memory-card:not(.matched)'));
    if (unmatchedCards.length < 2) return;

    // Find a matching pair among unmatched
    const symbolMap = {};
    let pairToReveal = null;

    for (const card of unmatchedCards) {
      const sym = card.dataset.symbol;
      if (symbolMap[sym]) {
        pairToReveal = [symbolMap[sym], card];
        break;
      } else {
        symbolMap[sym] = card;
      }
    }

    if (!pairToReveal) return;

    isHintActive = true;
    hintsUsed++;
    score = Math.max(0, score - 20);
    updateStatsDisplay();

    // Reveal and highlight both cards briefly
    pairToReveal.forEach(c => {
      c.classList.add('flipped', 'hint-highlight');
    });

    announceStatus(`Hint: Showing pair for ${pairToReveal[0].dataset.name} for a moment.`);

    setTimeout(() => {
      pairToReveal.forEach(c => {
        c.classList.remove('hint-highlight');
        // If not matched and not currently clicked as firstCard, flip back
        if (!c.classList.contains('matched') && c !== firstCard) {
          c.classList.remove('flipped');
        }
      });
      isHintActive = false;
    }, 1400);
  }

  /**
   * Concludes the game, collects local performance data, and shows result modal
   */
  /**
   * Concludes the game, collects local performance data, and saves session to backend
   */
  /**
   * Generates a unique client session ID for deduplication
   */
  function generateClientSessionId() {
    return 'mb_' + Date.now() + '_' + Math.random().toString(36).substring(2, 9);
  }

  /**
   * Synchronizes any queued offline sessions when connectivity is available
   */
  async function syncOfflineSessions() {
    try {
      const queueRaw = localStorage.getItem('mindbloom_offline_sessions');
      if (!queueRaw) return;
      const queue = JSON.parse(queueRaw);
      if (!Array.isArray(queue) || queue.length === 0) return;

      console.log(`MindBloom: Attempting to sync ${queue.length} offline game sessions...`);
      const remaining = [];

      for (const sessionPayload of queue) {
        try {
          const res = await fetch(`${API_BASE_URL}/game-sessions`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(sessionPayload)
          });
          if (res.ok) {
            const data = await res.json();
            console.log(`MindBloom: Synced offline session ${sessionPayload.client_session_id} -> ID ${data.session_id}`);
          } else if (res.status === 422) {
            // Unprocessable session: discard so queue does not get permanently clogged
            console.warn(`MindBloom: Discarding invalid offline session ${sessionPayload.client_session_id}`);
          } else {
            // Temporary server error, keep in queue
            remaining.push(sessionPayload);
          }
        } catch (err) {
          remaining.push(sessionPayload);
        }
      }

      if (remaining.length > 0) {
        localStorage.setItem('mindbloom_offline_sessions', JSON.stringify(remaining));
      } else {
        localStorage.removeItem('mindbloom_offline_sessions');
        console.log('MindBloom: All offline sessions synchronized successfully.');
      }
    } catch (e) {
      console.warn('MindBloom: Error while syncing offline sessions:', e);
    }
  }

  // Attempt offline sync when network comes online
  window.addEventListener('online', () => {
    console.info('MindBloom: Network restored. Syncing offline data...');
    syncOfflineSessions();
  });

  /**
   * Saves a session payload into localStorage queue for offline resilience
   */
  function saveSessionToOfflineQueue(payload) {
    try {
      const queueRaw = localStorage.getItem('mindbloom_offline_sessions');
      const queue = queueRaw ? JSON.parse(queueRaw) : [];
      // Deduplicate in local queue by client_session_id
      const exists = queue.some(s => s.client_session_id === payload.client_session_id);
      if (!exists) {
        queue.push(payload);
        localStorage.setItem('mindbloom_offline_sessions', JSON.stringify(queue));
        console.log(`MindBloom: Queued session ${payload.client_session_id} for offline sync.`);
      }
    } catch (e) {
      console.warn('MindBloom: Could not save session to localStorage offline queue:', e);
    }
  }

  /**
   * Requests AI adaptive difficulty prediction from trained Random Forest model
   */
  async function fetchAIRecommendation(performanceData) {
    if (aiRecLoading) aiRecLoading.style.display = 'flex';
    if (aiRecContent) aiRecContent.style.display = 'none';
    if (aiRecFallback) aiRecFallback.style.display = 'none';
    if (btnModalPlayRecommended) btnModalPlayRecommended.style.display = 'none';

    const mlPayload = {
      accuracy: parseFloat(performanceData.accuracy),
      response_time: parseInt(performanceData.timeTakenSeconds, 10),
      mistakes: parseInt(performanceData.mistakes, 10),
      score: parseInt(performanceData.score, 10),
      hints_used: parseInt(performanceData.hintsUsed, 10),
      previous_difficulty: performanceData.difficulty
    };

    try {
      const response = await fetch(`${API_BASE_URL}/ml/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(mlPayload)
      });

      if (response.ok) {
        const mlData = await response.json();
        const rawRec = mlData.recommended_difficulty || 'Medium';
        const recLevel = rawRec.toLowerCase();
        
        // Validate level
        if (DIFFICULTY_SETTINGS[recLevel]) {
          recommendedDifficulty = recLevel;
          const recName = DIFFICULTY_SETTINGS[recLevel].name;

          // Update difficulty badge
          if (aiRecDifficultyBadge) {
            aiRecDifficultyBadge.className = `rec-diff-badge diff-${recLevel}`;
            aiRecDifficultyBadge.textContent = recName;
          }

          // Update confidence tag
          if (aiRecConfidence) {
            const confPct = Math.round((mlData.confidence || 0.95) * 100);
            aiRecConfidence.textContent = `${confPct}% Match`;
          }

          // Generate friendly, encouraging rationale based strictly on gameplay metrics
          let friendlyMsg = '';
          const finalAcc = performanceData.accuracy;
          const timeSec = performanceData.timeTakenSeconds;
          const mistakesCount = performanceData.mistakes;

          if (recLevel === 'hard') {
            friendlyMsg = `🌟 Outstanding focus and fast matching (${finalAcc}% accuracy in ${timeSec}s)! Our AI recommends Hard difficulty (16 cards) for an engaging mental exercise.`;
          } else if (recLevel === 'medium') {
            friendlyMsg = `🌸 Wonderful memory rhythm! With ${finalAcc}% accuracy and ${mistakesCount} mistakes, Medium difficulty (12 cards) is your ideal sweet spot.`;
          } else {
            friendlyMsg = `🌿 Calm, relaxed pace! The AI suggests Easy difficulty (8 cards) for your next round so you can take all the time you need and enjoy every pair.`;
          }

          if (aiRecMessage) aiRecMessage.textContent = friendlyMsg;

          // Update comparison text
          if (recCurrentDiff) {
            recCurrentDiff.textContent = `${DIFFICULTY_SETTINGS[currentDifficulty].name} (${totalPairs * 2} cards)`;
          }
          if (recNextDiff) {
            recNextDiff.textContent = `${recName} (${DIFFICULTY_SETTINGS[recLevel].pairs * 2} cards)`;
          }

          // Update action button
          if (btnRecDiffText) btnRecDiffText.textContent = recName;
          if (btnModalPlayRecommended) {
            btnModalPlayRecommended.style.display = 'flex';
          }

          // Switch from loading to content state
          if (aiRecLoading) aiRecLoading.style.display = 'none';
          if (aiRecContent) aiRecContent.style.display = 'block';

          console.log(`MindBloom: AI Adaptive Difficulty predicted: ${rawRec} (Confidence: ${mlData.confidence})`);
          return rawRec;
        }
      }
      throw new Error(`Server returned status ${response.status}`);
    } catch (err) {
      console.warn('MindBloom: AI difficulty prediction unavailable or network offline:', err.message);
      recommendedDifficulty = null;
      if (aiRecLoading) aiRecLoading.style.display = 'none';
      if (aiRecContent) aiRecContent.style.display = 'none';
      if (aiRecFallback) {
        aiRecFallback.style.display = 'block';
        const msgEl = document.getElementById('ai-rec-fallback-msg');
        if (msgEl) {
          msgEl.textContent = 'ℹ️ Note: AI difficulty recommendation currently offline. You can continue playing at your own pace!';
        }
      }
      if (btnModalPlayRecommended) btnModalPlayRecommended.style.display = 'none';
      return null;
    }
  }

  /**
   * Concludes the game, collects performance data, requests AI recommendation,
   * and saves session to backend/MySQL with deduplication.
   */
  async function endGame() {
    stopTimer();
    const finalAccuracy = calculateAccuracy();

    gameEndTime = new Date();
    if (!gameStartTime) {
      gameStartTime = new Date(gameEndTime.getTime() - (secondsElapsed * 1000));
    }

    clientSessionId = generateClientSessionId();

    // Local performance data object (feeds backend API and ML models)
    const performanceData = {
      user_id: CURRENT_USER_ID,
      gameName: "Memory Match",
      difficulty: currentDifficulty,
      score: score,
      accuracy: finalAccuracy,
      timeTakenSeconds: secondsElapsed,
      attempts: attempts,
      mistakes: mistakes,
      matchedPairs: matchedPairs,
      totalPairs: totalPairs,
      hintsUsed: hintsUsed,
      client_session_id: clientSessionId,
      startedAt: gameStartTime ? gameStartTime.toISOString() : null,
      completedAt: gameEndTime.toISOString()
    };

    console.log("==========================================");
    console.log("MINDBLOOM — GAME PERFORMANCE DATA (PHASE 5)");
    console.log("==========================================");
    console.log(JSON.stringify(performanceData, null, 2));

    // Populate and open result modal
    if (resScore) resScore.textContent = score;
    if (resAccuracy) resAccuracy.textContent = `${finalAccuracy}%`;
    if (resTime) resTime.textContent = `${secondsElapsed}s (${formatTime(secondsElapsed)})`;
    if (resDifficulty) resDifficulty.textContent = DIFFICULTY_SETTINGS[currentDifficulty].name;
    if (resAttempts) resAttempts.textContent = attempts;
    if (resMistakes) resMistakes.textContent = mistakes;
    if (resMatched) resMatched.textContent = `${matchedPairs} / ${totalPairs}`;
    if (resHints) resHints.textContent = hintsUsed;

    openResultModal();
    announceStatus(`Game complete! Final score: ${score}, Accuracy: ${finalAccuracy}%.`);

    // Asynchronously query ML prediction and record session in database
    try {
      const recommended = await fetchAIRecommendation(performanceData);
      performanceData.recommended_difficulty = recommended;
      await saveGameSessionToBackend(performanceData);
    } catch (e) {
      console.warn('MindBloom: Async processing error in endGame:', e);
      await saveGameSessionToBackend(performanceData);
    }
  }

  /**
   * Asynchronously submits completed game-session data to FastAPI backend.
   * Handles deduplication and offline fallback safely.
   */
  async function saveGameSessionToBackend(data) {
    const saveStatusEl = document.getElementById('res-save-status');
    if (saveStatusEl) {
      saveStatusEl.style.display = 'block';
      saveStatusEl.className = 'res-save-status saving';
      saveStatusEl.textContent = '💾 Saving performance to database...';
    }

    const payload = {
      user_id: data.user_id,
      game_name: data.gameName,
      difficulty: data.difficulty,
      score: data.score,
      accuracy: data.accuracy,
      response_time: data.timeTakenSeconds,
      total_attempts: data.attempts,
      mistakes: data.mistakes,
      hints_used: data.hintsUsed,
      matched_pairs: data.matchedPairs,
      total_pairs: data.totalPairs,
      recommended_difficulty: data.recommended_difficulty || null,
      client_session_id: data.client_session_id,
      started_at: data.startedAt,
      completed_at: data.completedAt
    };

    try {
      const response = await fetch(`${API_BASE_URL}/game-sessions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      if (response.ok) {
        const resData = await response.json();
        if (saveStatusEl) {
          saveStatusEl.className = 'res-save-status success';
          if (resData.is_duplicate) {
            saveStatusEl.textContent = `✓ Already saved in database (Session #${resData.session_id})`;
          } else {
            saveStatusEl.textContent = `✓ Stored in database (Session #${resData.session_id})`;
          }
        }
        console.log('MindBloom: Game session successfully recorded in MySQL:', resData);
        // Sync any previous offline sessions in the background
        syncOfflineSessions();
      } else {
        const errorData = await response.json().catch(() => ({}));
        saveSessionToOfflineQueue(payload);
        if (saveStatusEl) {
          saveStatusEl.className = 'res-save-status notice';
          saveStatusEl.textContent = 'ℹ️ Performance saved locally in browser (will sync when online).';
        }
        console.warn('MindBloom: Backend responded with error:', response.status, errorData);
      }
    } catch (networkError) {
      // Graceful offline fallback: if backend is temporarily unreachable
      saveSessionToOfflineQueue(payload);
      if (saveStatusEl) {
        saveStatusEl.className = 'res-save-status notice';
        saveStatusEl.textContent = 'ℹ️ Note: Backend is offline. Performance saved locally in browser.';
      }
      console.info('MindBloom: Backend currently offline. Session queued in browser.');
    }
  }

  function openResultModal() {
    if (resultModal) {
      resultModal.style.display = 'flex';
      // Focus on recommended play button if available, else play again
      if (btnModalPlayRecommended && btnModalPlayRecommended.style.display !== 'none') {
        btnModalPlayRecommended.focus();
      } else if (btnModalPlayAgain) {
        btnModalPlayAgain.focus();
      }
    }
  }

  function closeResultModal() {
    if (resultModal) {
      resultModal.style.display = 'none';
    }
  }

  function announceStatus(message) {
    if (gameSrStatus) {
      gameSrStatus.textContent = message;
    }
  }

  // Event Listeners for Game Controls
  if (btnStartGame) {
    btnStartGame.addEventListener('click', () => {
      initGame();
      startGame();
    });
  }

  if (btnRestartGame) {
    btnRestartGame.addEventListener('click', () => {
      initGame();
    });
  }

  if (btnHintGame) {
    btnHintGame.addEventListener('click', () => {
      provideHint();
    });
  }

  // Difficulty selection with active-game confirmation guard
  diffButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const diff = btn.getAttribute('data-difficulty');
      if (diff === currentDifficulty) return;

      // Prevent accidental difficulty shift during an active round
      if (gameStarted && matchedPairs < totalPairs) {
        const targetName = DIFFICULTY_SETTINGS[diff] ? DIFFICULTY_SETTINGS[diff].name : diff;
        const currentName = DIFFICULTY_SETTINGS[currentDifficulty].name;
        const confirmChange = window.confirm(
          `A game is currently active on ${currentName} difficulty (${matchedPairs}/${totalPairs} pairs found).\n\nWould you like to restart on ${targetName} difficulty?`
        );
        if (!confirmChange) return;
      }

      setDifficulty(diff);
    });
  });

  // "Start Next Round (Recommended Level)" button
  if (btnModalPlayRecommended) {
    btnModalPlayRecommended.addEventListener('click', () => {
      closeResultModal();
      if (recommendedDifficulty && DIFFICULTY_SETTINGS[recommendedDifficulty]) {
        setDifficulty(recommendedDifficulty);
      }
      startGame();
    });
  }

  // "Replay Current Level" button
  if (btnModalPlayAgain) {
    btnModalPlayAgain.addEventListener('click', () => {
      closeResultModal();
      initGame();
      startGame();
    });
  }

  if (btnModalClose) {
    btnModalClose.addEventListener('click', () => {
      closeResultModal();
    });
  }

  // Close modal on Escape key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && resultModal && resultModal.style.display === 'flex') {
      closeResultModal();
    }
  });

  // Attempt to sync any pending offline sessions on initial page load
  syncOfflineSessions();

  // Initialize Game on page load (starts in Easy mode, ready to play)
  initGame();

  console.log('MindBloom Phase 1, 2, 3, 4 & 5 Initialized successfully.');
});

