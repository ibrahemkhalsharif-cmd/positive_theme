## Positive Theme

A Frappe app that gives ERPNext v15 the Positive visual identity: login page, desk (navbar,
sidebar, workspaces), list views, forms, reports, print and email. Everything is injected through
`hooks.py`; nothing in `frappe`, `erpnext` or `hrms` is changed, and uninstalling the app returns
the site to stock.

### Design (P1)

The approved design (login, desk home, list and form, in light and dark, plus the Arabic login)
is in Claude Design: https://claude.ai/artifact/3dVgWQXVhc7htyUnsFU9LK

### What it does

| Area | Where |
|---|---|
| Design tokens (the only raw colours) | `positive_theme/public/scss/_tokens.scss` |
| Light / dark semantic tokens | `positive_theme/public/scss/_theme.scss` |
| Frappe variables mapped to the tokens | `positive_theme/public/scss/_frappe.scss` |
| Self-hosted Poppins and Tajawal (woff2, subset) | `positive_theme/public/fonts/`, `_fonts.scss` |
| Login page (English and Arabic) | `positive_theme/www/login.html`, `login.py`, `_login.scss` |
| Desk shell: navbar, sidebar, search | `_shell.scss` |
| Workspaces, number cards, charts | `_workspace.scss`, chart palette in `positive_theme.bundle.js` |
| Lists, forms, status indicators | `_list.scss`, `_form.scss`, `_indicators.scss` |
| Print format and Letter Head | `templates/print_formats/sales_invoice_positive.html`, `install.py` |
| Email footer and brand image | `hooks.py` (`default_mail_footer`, `email_brand_image`) |

The two bundles, `public/positive_theme.bundle.scss` and `public/positive_theme.bundle.js`, are
built by Frappe's esbuild pipeline and injected with `app_include_css` / `app_include_js` (desk)
and `web_include_css` / `web_include_js` (website pages, including the login page).

### Install

On a **development** site only:

```bash
cd ~/frappe-bench
bench get-app https://github.com/<your-account>/positive_theme
bench --site <dev-site> install-app positive_theme
bench build --app positive_theme
bench --site <dev-site> clear-cache
```

Then restart the web server (`bench restart`, or restart `bench start`).

Installing also sets the Navbar Settings logo and creates the **Positive** Letter Head (made the
default only if the site had no default Letter Head). The **Sales Invoice Positive** print format
is a standard print format of the app.

### Uninstall

```bash
bench --site <dev-site> uninstall-app positive_theme
bench --site <dev-site> clear-cache
bench restart
```

The restart matters: running web workers keep the app's hooks in memory until they restart.

Uninstalling restores the previous Navbar Settings logo, deletes the Positive Letter Head, and
removes the print format with the app's module. The bundles are no longer injected, so the site
looks exactly like stock ERPNext. Remove the code with `bench remove-app positive_theme`.

### Updates

The theme overrides Frappe's CSS variables rather than its class names, adds no patches and
changes no core files, so `bench update` and `bench migrate` need no manual steps. Run
`bench build --app positive_theme` if assets are ever missing.

### Design rules in the code

- **One file holds every colour.** `_tokens.scss` defines the brand palette; everything else uses
  `var(--pt-*)` or `color-mix()` on those tokens. Print and email cannot use CSS variables, so
  `positive_theme/utils.py` reads the same file and exposes the values to Jinja as `brand_tokens()`.
- **Colour set.** The indigo set from the Positive colour-set sheet (accent `#7361E5`), approved
  by the trainer in place of the green set in the original task. The logo files are the brand
  pack SVGs with only their fills swapped to the indigo set; replace them with official indigo
  files when the brand team supplies them.
- **One accent.** Indigo marks actions, the active menu item, the focus ring, links and the one
  key number on a dashboard. Body text is deep on light surfaces and tint on ink.
- **Error signal.** A single red is kept for errors, Overdue and Cancelled only, so those statuses
  stay recognisable. It is not a brand colour and never decorates.
- **Status indicators differ in lightness, not only hue:** hollow dashed Draft, tinted Unpaid,
  accent-tinted Partly Paid, solid accent Paid, solid deep Submitted, tinted red Overdue, and a
  hollow struck-through Cancelled.
- **Layers.** Tokens and per-theme tokens live in `@layer pt.tokens` and `@layer pt.theme`. Rules
  that override Frappe are deliberately unlayered: Frappe's CSS is unlayered, and an unlayered
  rule beats any layered rule regardless of specificity.
- **RTL.** Layout uses logical properties (`margin-inline-start`, `inset-inline`), so Frappe's
  RTL build needs no duplicate rules. Arabic uses Tajawal; the logo always stays left to right.
- **Dark mode.** The desk follows Frappe's Light / Dark / Automatic switch through
  `[data-theme]`; the login page follows the operating system setting.
- **Motion.** Transitions are 150-250 ms and switched off under `prefers-reduced-motion`.
- **JavaScript** only sets attributes and passes chart options; there are no inline styles and no
  interval-based DOM patching. `!important` is used four times, each with a comment explaining why.

### Fonts and licences

Poppins (from the brand pack) and Tajawal (from the official google/fonts repository) are both
under the SIL Open Font License; see `public/fonts/OFL-*.txt`. They are subset and self-hosted;
no external CDN is used.

### Development

This app uses `pre-commit` (ruff, eslint, prettier, pyupgrade):

```bash
cd apps/positive_theme
pre-commit install
```

### License

MIT
