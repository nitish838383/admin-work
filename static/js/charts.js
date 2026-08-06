/**
 * MistriPoint Admin – Charts
 * Chart.js implementations with dark mode support
 */

(function () {
  'use strict';

  let charts = {};

  function getColors(theme) {
    const isDark = theme === 'dark';
    return {
      text: isDark ? '#9CA3AF' : '#6B7280',
      grid: isDark ? 'rgba(42, 49, 72, 0.6)' : 'rgba(229, 233, 245, 0.8)',
      primary: '#3B5BFF',
      secondary: '#6C63FF',
      success: '#00C853',
      warning: '#FFA726',
      info: '#00B8D9',
      purple: '#7C4DFF',
      surface: isDark ? '#1A2035' : '#FFFFFF'
    };
  }

  function baseOptions(theme) {
    const c = getColors(theme);
    return {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: {
            color: c.text,
            font: { family: 'Inter', size: 12 },
            usePointStyle: true,
            padding: 16
          }
        },
        tooltip: {
          backgroundColor: c.surface,
          titleColor: theme === 'dark' ? '#F3F4F6' : '#1A1D2E',
          bodyColor: c.text,
          borderColor: theme === 'dark' ? '#2A3148' : '#E5E9F5',
          borderWidth: 1,
          padding: 12,
          cornerRadius: 10,
          titleFont: { family: 'Inter', weight: '600' },
          bodyFont: { family: 'Inter' },
          displayColors: true,
          boxPadding: 4
        }
      },
      scales: {
        x: {
          ticks: { color: c.text, font: { family: 'Inter', size: 11 } },
          grid: { color: c.grid, drawBorder: false }
        },
        y: {
          ticks: { color: c.text, font: { family: 'Inter', size: 11 } },
          grid: { color: c.grid, drawBorder: false }
        }
      }
    };
  }

  /* ---------- Mini Sparkline Charts ---------- */
  function createSparkline(canvasId, data, color) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    return new Chart(ctx, {
      type: 'line',
      data: {
        labels: data.map((_, i) => i),
        datasets: [{
          data,
          borderColor: color,
          backgroundColor: color + '18',
          borderWidth: 2,
          fill: true,
          tension: 0.4,
          pointRadius: 0,
          pointHoverRadius: 0
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false }, tooltip: { enabled: false } },
        scales: {
          x: { display: false },
          y: { display: false }
        },
        elements: { line: { borderCapStyle: 'round' } }
      }
    });
  }

  /* ---------- Revenue Area Chart ---------- */
  function createRevenueChart(theme) {
    const ctx = document.getElementById('revenueChart');
    if (!ctx) return;
    if (charts.revenue) charts.revenue.destroy();

    const c = getColors(theme);
    const opts = baseOptions(theme);
    opts.plugins.legend.display = true;
    opts.plugins.legend.position = 'top';
    opts.scales.y.ticks.callback = (v) => '₹' + (v / 1000) + 'k';

    charts.revenue = new Chart(ctx, {
      type: 'line',
      data: {
        labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        datasets: [
          {
            label: 'Revenue',
            data: [42000, 58000, 51000, 72000, 68000, 89000, 78000],
            borderColor: c.primary,
            backgroundColor: (context) => {
              const chart = context.chart;
              const { ctx: cctx, chartArea } = chart;
              if (!chartArea) return c.primary + '20';
              const gradient = cctx.createLinearGradient(0, chartArea.top, 0, chartArea.bottom);
              gradient.addColorStop(0, c.primary + '40');
              gradient.addColorStop(1, c.primary + '05');
              return gradient;
            },
            borderWidth: 2.5,
            fill: true,
            tension: 0.4,
            pointBackgroundColor: c.primary,
            pointBorderColor: '#fff',
            pointBorderWidth: 2,
            pointRadius: 4,
            pointHoverRadius: 6
          },
          {
            label: 'Expenses',
            data: [28000, 32000, 29000, 35000, 31000, 38000, 34000],
            borderColor: c.warning,
            backgroundColor: 'transparent',
            borderWidth: 2,
            borderDash: [6, 4],
            fill: false,
            tension: 0.4,
            pointRadius: 3,
            pointHoverRadius: 5
          }
        ]
      },
      options: opts
    });
  }

  /* ---------- Category Doughnut ---------- */
  function createCategoryChart(theme) {
    const ctx = document.getElementById('categoryChart');
    if (!ctx) return;
    if (charts.category) charts.category.destroy();

    const c = getColors(theme);

    charts.category = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['Plumbing', 'Electrical', 'AC Repair', 'Others'],
        datasets: [{
          data: [420000, 310000, 280000, 240000],
          backgroundColor: [c.primary, c.secondary, c.success, c.warning],
          borderWidth: 0,
          hoverOffset: 8
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '68%',
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: c.surface,
            titleColor: theme === 'dark' ? '#F3F4F6' : '#1A1D2E',
            bodyColor: c.text,
            borderColor: theme === 'dark' ? '#2A3148' : '#E5E9F5',
            borderWidth: 1,
            padding: 12,
            cornerRadius: 10,
            callbacks: {
              label: (ctx) => {
                const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                const pct = ((ctx.raw / total) * 100).toFixed(1);
                return ` ₹${(ctx.raw / 100000).toFixed(1)}L (${pct}%)`;
              }
            }
          }
        }
      }
    });
  }

  /* ---------- Bookings Bar Chart ---------- */
  function createBookingsChart(theme) {
    const ctx = document.getElementById('bookingsChart');
    if (!ctx) return;
    if (charts.bookings) charts.bookings.destroy();

    const c = getColors(theme);
    const opts = baseOptions(theme);
    opts.plugins.legend.display = true;
    opts.plugins.legend.position = 'top';

    charts.bookings = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        datasets: [
          {
            label: 'Completed',
            data: [28, 35, 32, 41, 38, 52, 45],
            backgroundColor: c.success,
            borderRadius: 6,
            borderSkipped: false,
            barPercentage: 0.6
          },
          {
            label: 'Pending',
            data: [8, 12, 9, 14, 11, 16, 10],
            backgroundColor: c.warning,
            borderRadius: 6,
            borderSkipped: false,
            barPercentage: 0.6
          },
          {
            label: 'Cancelled',
            data: [3, 2, 4, 1, 3, 2, 1],
            backgroundColor: '#FF4D4F',
            borderRadius: 6,
            borderSkipped: false,
            barPercentage: 0.6
          }
        ]
      },
      options: opts
    });
  }

  /* ---------- Worker Performance Radar / Bar ---------- */
  function createWorkerChart(theme) {
    const ctx = document.getElementById('workerChart');
    if (!ctx) return;
    if (charts.worker) charts.worker.destroy();

    const c = getColors(theme);
    const opts = baseOptions(theme);
    opts.indexAxis = 'y';
    opts.plugins.legend.display = false;
    opts.scales.x.ticks.callback = (v) => v + '%';

    charts.worker = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: ['Ramesh K.', 'Suresh P.', 'Vikram S.', 'Anita D.', 'Manoj R.'],
        datasets: [{
          data: [96, 91, 88, 94, 85],
          backgroundColor: [
            c.primary,
            c.secondary,
            c.info,
            c.success,
            c.purple
          ],
          borderRadius: 6,
          borderSkipped: false,
          barPercentage: 0.7
        }]
      },
      options: opts
    });
  }

  /* ---------- Init All Charts ---------- */
  function initCharts() {
    const theme = document.documentElement.getAttribute('data-theme') || 'light';

    // Sparklines
    createSparkline('miniRevenue', [12, 19, 15, 25, 22, 30, 28, 35, 32, 40], '#3B5BFF');
    createSparkline('miniBookings', [8, 12, 10, 15, 14, 18, 16, 20, 19, 22], '#00C853');
    createSparkline('miniCustomers', [5, 8, 7, 11, 10, 14, 13, 16, 15, 18], '#00B8D9');
    createSparkline('miniWorkers', [3, 5, 4, 6, 5, 7, 6, 8, 7, 9], '#FFA726');

    createRevenueChart(theme);
    createCategoryChart(theme);
    createBookingsChart(theme);
    createWorkerChart(theme);
  }

  /* ---------- Theme Update Hook ---------- */
  window.updateChartsTheme = function (theme) {
    createRevenueChart(theme);
    createCategoryChart(theme);
    createBookingsChart(theme);
    createWorkerChart(theme);
  };

  document.addEventListener('DOMContentLoaded', () => {
    // Small delay to ensure CSS variables are applied
    setTimeout(initCharts, 100);
  });

})();
