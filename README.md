# AI‑Powered Personal Finance Manager

A professional, client-side personal finance dashboard built with HTML, CSS and JavaScript. It works as a static site and stores data locally in the browser, so it can be deployed easily on GitHub Pages, Render Static Sites, Netlify or any simple static host.

## Features

- User registration and login with hashed passwords.
- Demo two-factor authentication after login.
- Income and expense tracking.
- Custom categories and category management.
- Multi-currency display support for INR, USD and EUR.
- Monthly budget progress with visual alerts.
- Savings goals with contribution tracking.
- Upcoming bill reminders and mark-as-paid flow.
- Interactive monthly calendar with transaction totals.
- Searchable transaction history.
- Chart.js spending summary.
- CSV import/export.
- PDF report generation.
- Dark mode.
- Progressive Web App support through `manifest.json` and `sw.js`.

## Deployment

This is a static web application. No build command is required.

For GitHub Pages:

1. Go to repository Settings.
2. Open Pages.
3. Select the `main` branch and root directory.
4. Save and wait for GitHub Pages to finish building.

Live URL format:

```text
https://<username>.github.io/finance-ai-app/
```

## Files

```text
index.html      Main app layout
style.css       Custom styling and dark mode
app.js          Dashboard, auth, charts, bills, goals and exports
manifest.json   PWA manifest
sw.js           Service worker
README.md       Project documentation
```

## Note

This demo stores data in `localStorage`. For production use, add a secure backend, real email/SMS two-factor delivery, and live currency rates.
