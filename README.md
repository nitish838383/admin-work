# MistriPoint – Premium Admin Dashboard

A modern, production-ready SaaS Admin Dashboard for a service marketplace (home services, handyman, on-demand workers).

Inspired by high-end products such as Stripe, Linear, Notion, Vercel, and premium ThemeForest templates.

## Features

- **Sticky collapsible sidebar** with full navigation (Dashboard, Bookings, Customers, Workers, Finance, Analytics, System)
- **Sticky top navbar** with global search, live clock, notifications, messages, language, dark mode, fullscreen, profile
- **KPI cards** with animated counters, trend badges, gradient icons, mini sparklines
- **Interactive charts** (Chart.js): Revenue area, Category doughnut, Bookings stacked bar, Worker performance
- **Data tables** with search, status badges, avatars, pagination, actions
- **Widgets**: Activity timeline, Latest reviews, Quick actions, System health, Top workers, Upcoming bookings, Latest payments
- **AI Assistant banner**
- **Command Palette** (`Ctrl/Cmd + K`)
- **Dark / Light mode** with preference persistence
- **Toast notifications**, modals, dropdowns
- **Floating chat FAB** + mobile bottom navigation
- **Fully responsive** (320px → 1920px+)
- **AOS animations**, micro-interactions, glassmorphism accents
- **Accessible**: semantic HTML, ARIA labels, keyboard support, focus states

## Tech Stack

| Layer        | Technology                          |
|--------------|-------------------------------------|
| Markup       | HTML5                               |
| Styling      | CSS3 (Variables, Grid, Flexbox)     |
| Framework    | Bootstrap 5                         |
| Charts       | Chart.js 4 + ApexCharts (ready)     |
| Icons        | Font Awesome 6                      |
| Fonts        | Inter + Poppins (Google Fonts)      |
| Animation    | AOS + Custom CSS                    |
| Scripting    | Vanilla ES6 (no frameworks)         |

## Project Structure

```
project/
├── index.html
├── css/
│   ├── style.css          # Core design system & components
│   ├── responsive.css     # All breakpoints
│   └── animations.css     # Keyframes & micro-interactions
├── js/
│   ├── script.js          # Sidebar, theme, dropdowns, command palette, toasts
│   ├── dashboard.js       # Animated counters & live stats
│   └── charts.js          # All Chart.js instances + dark-mode support
├── assets/
│   ├── images/
│   ├── icons/
│   ├── illustrations/
│   └── avatars/
└── README.md
```

## Getting Started

1. Open `index.html` in a modern browser (or serve via any static server).
2. No build step required – pure HTML/CSS/JS + CDNs.

```bash
# Optional: quick local server
npx serve .
# or
python -m http.server 8000
```

## Keyboard Shortcuts

| Shortcut       | Action                  |
|----------------|-------------------------|
| `Ctrl/Cmd + K` | Open Command Palette    |
| `Esc`          | Close modals / palette  |

## Customization

- **Colors**: Edit CSS variables in `css/style.css` (`:root`)
- **Sidebar width**: `--sidebar-width` / `--sidebar-collapsed`
- **Charts**: Modify data and options in `js/charts.js`
- **Theme**: Toggle via navbar icon; preference saved in `localStorage`

## Browser Support

Chrome, Firefox, Safari, Edge (latest two versions).

## License

For demonstration / internal use. Customize freely for your product.

---

Built with attention to detail for a premium SaaS experience.