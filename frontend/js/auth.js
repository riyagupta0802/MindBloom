
/**
 * ==============================================================================
 * MINDBLOOM — CLIENT-SIDE AUTHENTICATION LOGIC (Phase 8+)
 * Handles Sign In, Sign Up, JWT Token Storage, Role Routing & Accessibility
 * ==============================================================================
 */

document.addEventListener('DOMContentLoaded', () => {
  'use strict';

  /* --------------------------------------------------------------------------
   * 1. Configuration & API Base URL Discovery
   * -------------------------------------------------------------------------- */
  const API_BASE_URL =
    window.MINDBLOOM_API_URL || 'http://127.0.0.1:8002/api';

  /* --------------------------------------------------------------------------
   * 2. DOM Elements
   * -------------------------------------------------------------------------- */
  const tabSignIn = document.getElementById('tab-signin');
  const tabSignUp = document.getElementById('tab-signup');
  const formSignIn = document.getElementById('form-signin');
  const formSignUp = document.getElementById('form-signup');
  const switchPrompt = document.getElementById('switch-prompt');
  const btnSwitchAuth = document.getElementById('btn-switch-auth');
  const authAlert = document.getElementById('auth-alert');

  // Sign In inputs
  const signinEmail = document.getElementById('signin-email');
  const signinPassword = document.getElementById('signin-password');
  const btnSubmitSignIn = document.getElementById('btn-submit-signin');
  const btnToggleSignInPw = document.getElementById('btn-toggle-signin-pw');

  // Sign Up inputs
  const signupName = document.getElementById('signup-name');
  const signupEmail = document.getElementById('signup-email');
  const signupRole = document.getElementById('signup-role');
  const roleElderly = document.getElementById('role-opt-elderly');
  const roleCaregiver = document.getElementById('role-opt-caregiver');
  const signupPassword = document.getElementById('signup-password');
  const signupConfirmPw = document.getElementById('signup-confirm-password');
  const btnSubmitSignUp = document.getElementById('btn-submit-signup');
  const btnToggleSignUpPw = document.getElementById('btn-toggle-signup-pw');
  const btnToggleSignUpConfirmPw = document.getElementById(
    'btn-toggle-signup-confirm-pw'
  );

  // Quick-fill demo buttons
  const btnQuickAlice = document.getElementById('btn-quick-alice');
  const btnQuickDavid = document.getElementById('btn-quick-david');
  const btnQuickNew = document.getElementById('btn-quick-new');

  /* --------------------------------------------------------------------------
   * 3. Accessibility Controls (Text Sizing & High Contrast)
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
      const isHigh = body.classList.contains('high-contrast');
      enableHighContrast(!isHigh);
    });
  }

  /* --------------------------------------------------------------------------
   * 4. Session Pre-check: If Already Authenticated, Redirect
   * -------------------------------------------------------------------------- */
  async function checkExistingAuth() {
    const token = localStorage.getItem('mindbloom_token');
    if (!token) return;

    try {
      const res = await fetch(`${API_BASE_URL}/auth/me`, {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token}`
        },
        credentials: 'include'
      });

      if (res.ok) {
        const user = await res.json();
        localStorage.setItem('mindbloom_user', JSON.stringify(user));

        if (user.user_type === 'caregiver') {
          window.location.replace('dashboard.html');
        } else {
          window.location.replace('index.html');
        }
      } else {
        localStorage.removeItem('mindbloom_token');
        localStorage.removeItem('mindbloom_user');
      }
    } catch (err) {
      console.warn('Backend not reachable during auth check:', err);
    }
  }

  checkExistingAuth();

  /* --------------------------------------------------------------------------
   * 5. Tab Switching (Sign In <-> Sign Up)
   * -------------------------------------------------------------------------- */
  function switchTab(target) {
    clearAlert();

    if (target === 'signup') {
      tabSignUp.classList.add('active');
      tabSignUp.setAttribute('aria-selected', 'true');
      tabSignIn.classList.remove('active');
      tabSignIn.setAttribute('aria-selected', 'false');

      formSignUp.style.display = 'block';
      formSignIn.style.display = 'none';

      switchPrompt.textContent = 'Already have an account?';
      btnSwitchAuth.textContent = 'Sign in';
      window.location.hash = '#signup';
    } else {
      tabSignIn.classList.add('active');
      tabSignIn.setAttribute('aria-selected', 'true');
      tabSignUp.classList.remove('active');
      tabSignUp.setAttribute('aria-selected', 'false');

      formSignIn.style.display = 'block';
      formSignUp.style.display = 'none';

      switchPrompt.textContent = "Don't have an account?";
      btnSwitchAuth.textContent = 'Sign up';
      window.location.hash = '#signin';
    }
  }

  if (tabSignIn) {
    tabSignIn.addEventListener('click', () => switchTab('signin'));
  }

  if (tabSignUp) {
    tabSignUp.addEventListener('click', () => switchTab('signup'));
  }

  if (btnSwitchAuth) {
    btnSwitchAuth.addEventListener('click', () => {
      const isSignIn = formSignIn.style.display !== 'none';
      switchTab(isSignIn ? 'signup' : 'signin');
    });
  }

  if (window.location.hash === '#signup') {
    switchTab('signup');
  }

  /* --------------------------------------------------------------------------
   * 6. Role Selection Cards
   * -------------------------------------------------------------------------- */
  function selectRole(role) {
    if (role === 'caregiver') {
      if (roleCaregiver) {
        roleCaregiver.classList.add('selected');
        roleCaregiver.setAttribute('aria-checked', 'true');
      }

      if (roleElderly) {
        roleElderly.classList.remove('selected');
        roleElderly.setAttribute('aria-checked', 'false');
      }

      if (signupRole) signupRole.value = 'caregiver';
    } else {
      if (roleElderly) {
        roleElderly.classList.add('selected');
        roleElderly.setAttribute('aria-checked', 'true');
      }

      if (roleCaregiver) {
        roleCaregiver.classList.remove('selected');
        roleCaregiver.setAttribute('aria-checked', 'false');
      }

      if (signupRole) signupRole.value = 'elderly';
    }
  }

  if (roleElderly) {
    roleElderly.addEventListener('click', () => selectRole('elderly'));
  }

  if (roleCaregiver) {
    roleCaregiver.addEventListener('click', () => selectRole('caregiver'));
  }

  /* --------------------------------------------------------------------------
   * 7. Password Visibility Toggles
   * -------------------------------------------------------------------------- */
  function setupPasswordToggle(btn, input) {
    if (!btn || !input) return;

    btn.addEventListener('click', () => {
      const isPw = input.type === 'password';
      input.type = isPw ? 'text' : 'password';
      btn.textContent = isPw ? 'Hide' : 'Show';
      btn.setAttribute(
        'aria-label',
        isPw ? 'Hide password' : 'Show password'
      );
    });
  }

  setupPasswordToggle(btnToggleSignInPw, signinPassword);
  setupPasswordToggle(btnToggleSignUpPw, signupPassword);
  setupPasswordToggle(btnToggleSignUpConfirmPw, signupConfirmPw);

  /* --------------------------------------------------------------------------
   * 8. Alert Helper Functions
   * -------------------------------------------------------------------------- */
  function showAlert(message, type = 'error') {
    if (!authAlert) return;

    authAlert.className = `auth-alert ${type}`;
    authAlert.textContent = message;
    authAlert.style.display = 'block';
  }

  function clearAlert() {
    if (!authAlert) return;

    authAlert.className = 'auth-alert';
    authAlert.textContent = '';
    authAlert.style.display = 'none';
  }

  /* --------------------------------------------------------------------------
   * 9. Sign In Submission (POST /api/auth/login)
   * -------------------------------------------------------------------------- */
  if (formSignIn) {
    formSignIn.addEventListener('submit', async (e) => {
      e.preventDefault();
      clearAlert();

      const email = signinEmail.value.trim();
      const password = signinPassword.value;

      if (!email || !password) {
        showAlert('Please enter both your email and password.', 'error');
        return;
      }

      btnSubmitSignIn.disabled = true;
      btnSubmitSignIn.innerHTML = '<span>Signing in...</span>';

      try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          credentials: 'include',
          body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (response.ok && data.status === 'success') {
          localStorage.setItem('mindbloom_token', data.access_token);
          localStorage.setItem('mindbloom_user', JSON.stringify(data.user));
          localStorage.setItem('mindbloom_api_url', API_BASE_URL);

          showAlert(
            `Welcome back, ${data.user.name}! Redirecting...`,
            'success'
          );

          setTimeout(() => {
            if (data.user.user_type === 'caregiver') {
              window.location.href = 'dashboard.html';
            } else {
              window.location.href = 'index.html';
            }
          }, 600);
        } else {
          const errMsg =
            data.detail ||
            data.message ||
            'Incorrect email or password.';

          showAlert(`⚠️ ${errMsg}`, 'error');
          btnSubmitSignIn.disabled = false;
          btnSubmitSignIn.innerHTML = '<span>Sign In</span>';
        }
      } catch (err) {
        console.error('Sign in network error:', err);

        showAlert(
          '⚠️ Unable to connect to the backend server. Please verify that the server is running on port 8002.',
          'error'
        );

        btnSubmitSignIn.disabled = false;
        btnSubmitSignIn.innerHTML = '<span>Sign In</span>';
      }
    });
  }

  /* --------------------------------------------------------------------------
   * 10. Sign Up Submission (POST /api/auth/register)
   * -------------------------------------------------------------------------- */
  if (formSignUp) {
    formSignUp.addEventListener('submit', async (e) => {
      e.preventDefault();
      clearAlert();

      const name = signupName.value.trim();
      const email = signupEmail.value.trim();
      const user_type = signupRole.value;
      const password = signupPassword.value;
      const confirm_password = signupConfirmPw.value;

      if (!name || name.length < 2) {
        showAlert(
          'Please enter your full name (at least 2 characters).',
          'error'
        );
        return;
      }

      if (!email || !email.includes('@')) {
        showAlert('Please enter a valid email address.', 'error');
        return;
      }

      if (!password || password.length < 6) {
        showAlert('Password must be at least 6 characters long.', 'error');
        return;
      }

      if (password !== confirm_password) {
        showAlert(
          'Passwords do not match. Please re-enter your password.',
          'error'
        );
        return;
      }

      btnSubmitSignUp.disabled = true;
      btnSubmitSignUp.innerHTML = '<span>Creating Account...</span>';

      try {
        const response = await fetch(`${API_BASE_URL}/auth/register`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          credentials: 'include',
          body: JSON.stringify({
            name,
            email,
            user_type,
            password,
            confirm_password
          })
        });

        const data = await response.json();

        if (response.ok && data.status === 'success') {
          localStorage.setItem('mindbloom_token', data.access_token);
          localStorage.setItem('mindbloom_user', JSON.stringify(data.user));
          localStorage.setItem('mindbloom_api_url', API_BASE_URL);

          showAlert(
            `Account created successfully for ${data.user.name}! Redirecting...`,
            'success'
          );

          setTimeout(() => {
            if (data.user.user_type === 'caregiver') {
              window.location.href = 'dashboard.html';
            } else {
              window.location.href = 'index.html';
            }
          }, 700);
        } else {
          const errMsg =
            data.detail ||
            data.message ||
            'Registration failed. Email may already be registered.';

          showAlert(`⚠️ ${errMsg}`, 'error');
          btnSubmitSignUp.disabled = false;
          btnSubmitSignUp.innerHTML = '<span>Create Account</span>';
        }
      } catch (err) {
        console.error('Sign up network error:', err);

        showAlert(
          '⚠️ Unable to connect to the backend server. Please verify that the server is running on port 8002.',
          'error'
        );

        btnSubmitSignUp.disabled = false;
        btnSubmitSignUp.innerHTML = '<span>Create Account</span>';
      }
    });
  }

  /* --------------------------------------------------------------------------
   * 11. Quick-Fill Demo Helpers
   * -------------------------------------------------------------------------- */
  if (btnQuickAlice) {
    btnQuickAlice.addEventListener('click', () => {
      switchTab('signin');
      signinEmail.value = 'alice.test@mindbloom.local';
      signinPassword.value = 'SecurePassword123!';

      showAlert(
        'Demo credentials filled for Alice (Elderly Player). Click Sign In to continue.',
        'info'
      );
    });
  }

  if (btnQuickDavid) {
    btnQuickDavid.addEventListener('click', () => {
      switchTab('signin');
      signinEmail.value = 'demo.david@mindbloom.local';
      signinPassword.value = 'SecurePassword123!';

      showAlert(
        'Demo credentials filled for David (Caregiver). Click Sign In to open the Caregiver Dashboard.',
        'info'
      );
    });
  }

  if (btnQuickNew) {
    btnQuickNew.addEventListener('click', () => {
      switchTab('signup');

      const randNum = Math.floor(1000 + Math.random() * 9000);

      signupName.value = `Grandpa John ${randNum}`;
      signupEmail.value = `john${randNum}@mindbloom.local`;

      selectRole('elderly');

      signupPassword.value = 'SecurePass123!';
      signupConfirmPw.value = 'SecurePass123!';

      showAlert(
        'Random new user generated! Click Create Account to register and test the full flow.',
        'info'
      );
    });
  }
});
