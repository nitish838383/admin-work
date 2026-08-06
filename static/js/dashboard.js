/**
 * MistriPoint Admin – Dashboard Logic
 * Animated Counters, Live Stats Simulation
 */

(function () {
  'use strict';

  /* ---------- Animated Counter ---------- */
  function animateCounter(el, target, duration = 1800, prefix = '', suffix = '') {
    const isCurrency = prefix === '₹' || el.textContent.includes('₹');
    let start = 0;
    const startTime = performance.now();

    function update(currentTime) {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      // Ease out cubic
      const ease = 1 - Math.pow(1 - progress, 3);
      const value = Math.floor(ease * target);

      if (isCurrency || prefix === '₹') {
        el.textContent = '₹' + value.toLocaleString('en-IN');
      } else {
        el.textContent = prefix + value.toLocaleString('en-IN') + suffix;
      }

      if (progress < 1) {
        requestAnimationFrame(update);
      } else {
        if (isCurrency || prefix === '₹') {
          el.textContent = '₹' + target.toLocaleString('en-IN');
        } else {
          el.textContent = prefix + target.toLocaleString('en-IN') + suffix;
        }
      }
    }

    requestAnimationFrame(update);
  }

  function initCounters() {
    document.querySelectorAll('[data-counter]').forEach(el => {
      const target = parseInt(el.dataset.counter, 10);
      if (isNaN(target)) return;

      // Detect currency from initial content or nearby
      const isRupee = el.textContent.includes('₹') || el.closest('.kpi-card')?.querySelector('.kpi-label')?.textContent.toLowerCase().includes('revenue') ||
        el.closest('.kpi-card')?.querySelector('.kpi-label')?.textContent.toLowerCase().includes('wallet');

      // Observe when in viewport
      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            animateCounter(el, target, 1800, isRupee ? '₹' : '');
            observer.unobserve(el);
          }
        });
      }, { threshold: 0.3 });

      observer.observe(el);
    });
  }

  /* ---------- Live Stats Simulation (subtle updates) ---------- */
  function simulateLiveStats() {
    // Occasionally update a KPI slightly to feel alive
    setInterval(() => {
      const onlineWorkers = document.querySelector('.kpi-card:nth-child(4) .kpi-value');
      // Keep it subtle – no aggressive changes
    }, 30000);
  }

  /* ---------- Init ---------- */
  document.addEventListener('DOMContentLoaded', () => {
    initCounters();
    simulateLiveStats();

  });

})();
