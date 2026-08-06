/**
 * MistriPoint Admin – Core Script
 * Sidebar, Theme, Clock, Dropdowns, Command Palette, Toasts, Modals
 */

(function () {
  'use strict';

  /* ---------- Page Loader ---------- */
  window.addEventListener('load', () => {
    const loader = document.getElementById('pageLoader');
    if (loader) {
      setTimeout(() => loader.classList.add('hidden'), 600);
    }
  });

  /* ---------- AOS Init ---------- */
  if (typeof AOS !== 'undefined') {
    AOS.init({
      duration: 600,
      easing: 'ease-out-cubic',
      once: true,
      offset: 40
    });
  }

  /* ---------- Sidebar Toggle ---------- */
  const sidebar = document.getElementById('sidebar');
  const sidebarToggle = document.getElementById('sidebarToggle');
  const sidebarOverlay = document.getElementById('sidebarOverlay');

  function toggleSidebar() {
    if (window.innerWidth <= 1023) {
      sidebar.classList.toggle('mobile-open');
      sidebarOverlay.classList.toggle('active');
    } else {
      sidebar.classList.toggle('collapsed');
      localStorage.setItem('sidebarCollapsed', sidebar.classList.contains('collapsed'));
    }
  }

  if (sidebarToggle) sidebarToggle.addEventListener('click', toggleSidebar);
  if (sidebarOverlay) {
    sidebarOverlay.addEventListener('click', () => {
      sidebar.classList.remove('mobile-open');
      sidebarOverlay.classList.remove('active');
    });
  }

  // Restore sidebar state
  if (localStorage.getItem('sidebarCollapsed') === 'true' && window.innerWidth > 1023) {
    sidebar.classList.add('collapsed');
  }

  /* ---------- Dark Mode ---------- */
  const themeToggle = document.getElementById('themeToggle');
  const html = document.documentElement;

  function setTheme(theme) {
    html.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    if (themeToggle) {
      themeToggle.innerHTML = theme === 'dark'
        ? '<i class="fas fa-sun"></i>'
        : '<i class="fas fa-moon"></i>';
    }
    // Update charts if available
    if (window.updateChartsTheme) window.updateChartsTheme(theme);
  }

  // Init theme
  const savedTheme = localStorage.getItem('theme') ||
    (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  setTheme(savedTheme);

  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      const next = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      setTheme(next);
      showToast('Theme switched to ' + next + ' mode', 'info');
    });
  }

  /* ---------- Live Clock ---------- */
  function updateClock() {
    const now = new Date();
    const timeEl = document.getElementById('liveClock');
    const dateEl = document.getElementById('liveDate');
    if (timeEl) {
      timeEl.textContent = now.toLocaleTimeString('en-IN', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: true
      });
    }
    if (dateEl) {
      dateEl.textContent = now.toLocaleDateString('en-IN', {
        weekday: 'short',
        day: 'numeric',
        month: 'short',
        year: 'numeric'
      });
    }
  }
  updateClock();
  setInterval(updateClock, 1000);

  /* ---------- Dropdowns ---------- */
  function setupDropdown(btnId, menuId) {
    const btn = document.getElementById(btnId);
    const menu = document.getElementById(menuId);
    if (!btn || !menu) return;

    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      // Close others
      document.querySelectorAll('.dropdown-menu.show').forEach(m => {
        if (m !== menu) m.classList.remove('show');
      });
      menu.classList.toggle('show');
    });
  }

  setupDropdown('notifBtn', 'notifMenu');
  setupDropdown('msgBtn', 'msgMenu');
  setupDropdown('profileBtn', 'profileMenu');
  setupDropdown('langBtn', 'langMenu');

  document.addEventListener('click', () => {
    document.querySelectorAll('.dropdown-menu.show').forEach(m => m.classList.remove('show'));
  });

  /* ---------- Fullscreen ---------- */
  const fullscreenBtn = document.getElementById('fullscreenBtn');
  if (fullscreenBtn) {
    fullscreenBtn.addEventListener('click', () => {
      if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch(() => {});
        fullscreenBtn.innerHTML = '<i class="fas fa-compress"></i>';
      } else {
        document.exitFullscreen();
        fullscreenBtn.innerHTML = '<i class="fas fa-expand"></i>';
      }
    });
  }

  /* ---------- Command Palette (Ctrl/Cmd + K) ---------- */
  const commandPalette = document.getElementById('commandPalette');
  const commandInput = document.getElementById('commandInput');

  function openCommandPalette() {
    if (commandPalette) {
      commandPalette.classList.add('active');
      if (commandInput) {
        commandInput.value = '';
        commandInput.focus();
      }
    }
  }

  function closeCommandPalette() {
    if (commandPalette) commandPalette.classList.remove('active');
  }

  document.addEventListener('keydown', (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
      e.preventDefault();
      openCommandPalette();
    }
    if (e.key === 'Escape') {
      closeCommandPalette();
      closeBookingModal();
    }
  });

  // Also open from search shortcut click
  const searchBox = document.querySelector('.search-shortcut');
  if (searchBox) searchBox.addEventListener('click', openCommandPalette);

  if (commandPalette) {
    commandPalette.addEventListener('click', (e) => {
      if (e.target === commandPalette) closeCommandPalette();
    });
  }

  // Command items
  document.querySelectorAll('.command-item').forEach(item => {
    item.addEventListener('click', () => {
      const text = item.textContent.trim();
      closeCommandPalette();
      if (text.includes('Dark Mode')) {
        themeToggle?.click();
      } else if (text.includes('New Booking')) {
        openBookingModal();
      } else {
        showToast('Action: ' + text, 'info');
      }
    });
  });

  /* ---------- Toast Notifications ---------- */
  window.showToast = function (message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const icons = {
      success: 'fa-check',
      error: 'fa-times',
      info: 'fa-info'
    };

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
      <div class="toast-icon"><i class="fas ${icons[type] || icons.info}"></i></div>
      <div class="fs-sm fw-500">${message}</div>
    `;
    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(40px)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 3500);
  };

  /* ---------- Quick Booking Modal ---------- */
  const bookingModal = document.getElementById('bookingModal');

  function openBookingModal() {
    if (bookingModal) bookingModal.classList.add('active');
  }

  function closeBookingModal() {
    if (bookingModal) bookingModal.classList.remove('active');
  }

  const quickBookingBtn = document.getElementById('quickBookingBtn');
  if (quickBookingBtn) quickBookingBtn.addEventListener('click', openBookingModal);

  document.getElementById('closeBookingModal')?.addEventListener('click', closeBookingModal);
  document.getElementById('cancelBooking')?.addEventListener('click', closeBookingModal);

  document.getElementById('submitBooking')?.addEventListener('click', () => {
    closeBookingModal();
    showToast('Booking created successfully!', 'success');
  });

  if (bookingModal) {
    bookingModal.addEventListener('click', (e) => {
      if (e.target === bookingModal) closeBookingModal();
    });
  }

  /* ---------- Quick Actions ---------- */
  document.querySelectorAll('.quick-action').forEach(el => {
    el.addEventListener('click', () => {
      const action = el.dataset.action;
      if (action === 'booking') openBookingModal();
      else showToast('Opening ' + action + '...', 'info');
    });
  });

  /* ---------- AI Assistant + Chat Panel ---------- */
  const AI_CHAT_API = '/auth/chat-ai';  // change if backend URL is different

  const aiChatPanel = document.getElementById('aiChatPanel');
  const aiChatMessages = document.getElementById('aiChatMessages');
  const aiChatForm = document.getElementById('aiChatForm');
  const aiChatInput = document.getElementById('aiChatInput');
  const aiChatSend = document.getElementById('aiChatSend');
  const fabChat = document.getElementById('fabChat');
  const aiChatClose = document.getElementById('aiChatClose');

  function openAiChat() {
    if (!aiChatPanel) return;
    aiChatPanel.classList.add('open');
    aiChatPanel.setAttribute('aria-hidden', 'false');
    if (fabChat) fabChat.classList.add('active');
    setTimeout(() => aiChatInput && aiChatInput.focus(), 200);
  }

  function closeAiChat() {
    if (!aiChatPanel) return;
    aiChatPanel.classList.remove('open');
    aiChatPanel.setAttribute('aria-hidden', 'true');
    if (fabChat) fabChat.classList.remove('active');
  }

  function toggleAiChat() {
    if (aiChatPanel && aiChatPanel.classList.contains('open')) closeAiChat();
    else openAiChat();
  }

  if (fabChat) fabChat.addEventListener('click', toggleAiChat);
  if (aiChatClose) aiChatClose.addEventListener('click', closeAiChat);

  document.getElementById('aiAssistBtn')?.addEventListener('click', () => {
    openAiChat();
  });

  function appendMsg(text, who) {
    if (!aiChatMessages) return null;
    const wrap = document.createElement('div');
    wrap.className = 'ai-msg ' + who;
    const bubble = document.createElement('div');
    bubble.className = 'ai-msg-bubble';
    // simple markdown-ish: **bold** and newlines
    let html = String(text)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/\n/g, '<br>');
    bubble.innerHTML = html;
    wrap.appendChild(bubble);
    aiChatMessages.appendChild(wrap);
    aiChatMessages.scrollTop = aiChatMessages.scrollHeight;
    return wrap;
  }

  function showTyping() {
    if (!aiChatMessages) return null;
    const wrap = document.createElement('div');
    wrap.className = 'ai-msg bot typing';
    wrap.id = 'aiTyping';
    wrap.innerHTML = '<div class="ai-msg-bubble"><span class="ai-typing-dots"><span></span><span></span><span></span></span></div>';
    aiChatMessages.appendChild(wrap);
    aiChatMessages.scrollTop = aiChatMessages.scrollHeight;
    return wrap;
  }

  function hideTyping() {
    document.getElementById('aiTyping')?.remove();
  }

  async function askAi(question) {
    const q = (question || '').trim();
    if (!q) return;

    appendMsg(q, 'user');
    if (aiChatInput) aiChatInput.value = '';
    if (aiChatSend) aiChatSend.disabled = true;

    showTyping();

    try {
      const url = AI_CHAT_API + '?message=' + encodeURIComponent(q);
      const res = await fetch(url, { method: 'GET', headers: { 'Accept': 'application/json' } });
      hideTyping();

      if (!res.ok) {
        appendMsg('Error ' + res.status + ': Could not reach AI. Check API is running on /auth/chat-ai', 'bot');
        return;
      }

      const data = await res.json();
      const reply = data.reply || data.message || JSON.stringify(data);
      appendMsg(reply, 'bot');
    } catch (err) {
      hideTyping();
      appendMsg('Network error. Make sure backend is running (e.g. http://127.0.0.1:8000) and CORS allows this page.', 'bot');
      console.error('AI chat error:', err);
    } finally {
      if (aiChatSend) aiChatSend.disabled = false;
      if (aiChatInput) aiChatInput.focus();
    }
  }

  if (aiChatForm) {
    aiChatForm.addEventListener('submit', function (e) {
      e.preventDefault();
      askAi(aiChatInput ? aiChatInput.value : '');
    });
  }

  document.querySelectorAll('.ai-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      const q = chip.getAttribute('data-q') || chip.textContent;
      askAi(q);
    });
  });

  /* ---------- Export / Print ---------- */
  document.getElementById('exportBtn')?.addEventListener('click', () => {
    showToast('Exporting dashboard data...', 'info');
  });

  document.getElementById('printBtn')?.addEventListener('click', () => {
    window.print();
  });

  /* ---------- Nav Active State ---------- */
  document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', (e) => {
      // For demo, just set active
      document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
      link.classList.add('active');
      // Close mobile sidebar
      if (window.innerWidth <= 1023) {
        sidebar.classList.remove('mobile-open');
        sidebarOverlay.classList.remove('active');
      }
    });
  });

  /* ---------- Table Search (simple filter) ---------- */
  const tableSearch = document.getElementById('tableSearch');
  if (tableSearch) {
    tableSearch.addEventListener('input', (e) => {
      const q = e.target.value.toLowerCase();
      document.querySelectorAll('#bookingsTable tbody tr').forEach(row => {
        row.style.display = row.textContent.toLowerCase().includes(q) ? '' : 'none';
      });
    });
  }

  /* ---------- Filter Tabs ---------- */
  document.querySelectorAll('.filter-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      tab.parentElement.querySelectorAll('.filter-tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      showToast('Showing ' + tab.textContent + ' data', 'info');
    });
  });

  /* ---------- Keyboard Navigation Hint ---------- */
  document.getElementById('globalSearch')?.addEventListener('focus', () => {
    // Optional: could open command palette
  });

})();