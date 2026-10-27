// Positive theme for ERPNext: small behaviour hooks for desk and website pages.
// Rules for this file: no inline styles, no polling or interval-based DOM patching. It only
// sets attributes and passes options; all visuals live in the SCSS.

// Theme picker -------------------------------------------------------------------------------
// A navbar button left of the notifications bell with three choices. Light and Dark are Frappe's
// own desk theme (saved on the user by switch_theme); Red is the red colour set on the light
// theme, saved per user by positive_theme.api.set_palette and sent back in the desk boot.

const pt_root = document.documentElement;
const PT_THEMES = [
	{ id: "light", label: "Light", theme: "light", palette: "" },
	{ id: "dark", label: "Dark", theme: "dark", palette: "" },
	{ id: "red", label: "Red", theme: "light", palette: "red" },
];

function pt_set_palette(palette) {
	if (palette) pt_root.setAttribute("data-pt-palette", palette);
	else pt_root.removeAttribute("data-pt-palette");
}

// Apply the saved colour set as soon as the bundle runs, before the desk renders.
if (window.frappe && frappe.boot && frappe.boot.pt_palette !== undefined) {
	pt_set_palette(frappe.boot.pt_palette);
}

function pt_current_theme() {
	if (pt_root.getAttribute("data-pt-palette") === "red") return "red";
	return pt_root.getAttribute("data-theme") === "dark" ? "dark" : "light";
}

function pt_sync_picker() {
	const current = pt_current_theme();
	document.querySelectorAll(".pt-theme-picker [data-pt-theme]").forEach((item) => {
		item.setAttribute("aria-checked", String(item.dataset.ptTheme === current));
	});
}

function pt_choose_theme(option) {
	const apply = () => {
		pt_root.setAttribute("data-theme-mode", option.theme);
		pt_root.setAttribute("data-theme", option.theme);
		pt_set_palette(option.palette);
		pt_sync_picker();
	};
	// A short cross-fade between the old and new look (skipped for reduced motion).
	const calm = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
	if (document.startViewTransition && !calm) document.startViewTransition(apply);
	else apply();

	const desk_theme = option.theme === "dark" ? "Dark" : "Light";
	frappe.xcall("frappe.core.doctype.user.user.switch_theme", { theme: desk_theme });
	frappe.xcall("positive_theme.api.set_palette", { palette: option.palette });
	frappe.boot.pt_palette = option.palette;
}

function pt_build_picker() {
	const bell = document.querySelector("header.navbar .dropdown-notifications");
	if (!bell || document.querySelector(".pt-theme-picker")) return;

	const items = PT_THEMES.map(
		(option) => `
		<button type="button" class="dropdown-item pt-theme-picker__item" role="menuitemradio"
			aria-checked="false" data-pt-theme="${option.id}">
			<span class="pt-swatch pt-swatch--${option.id}" aria-hidden="true"></span>
			<span>${frappe.utils.escape_html(__(option.label, null, "Positive theme picker"))}</span>
			<svg class="pt-theme-picker__check" width="16" height="16" viewBox="0 0 24 24" fill="none"
				stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"
				aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5"></path></svg>
		</button>`
	).join("");
	const label = frappe.utils.escape_html(__("Theme", null, "Positive theme picker"));

	const picker = document.createElement("li");
	picker.className = "nav-item dropdown pt-theme-picker";
	picker.innerHTML = `
		<button type="button" class="btn-reset nav-link pt-theme-picker__toggle" data-toggle="dropdown"
			aria-haspopup="true" aria-expanded="false" aria-label="${label}" title="${label}">
			<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor"
				stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
				<circle cx="12" cy="12" r="8.5"></circle><path d="M12 3.5v17"></path>
				<path d="M12 6.5a5.5 5.5 0 0 1 0 11" fill="currentColor" stroke="none"></path>
			</svg>
		</button>
		<div class="dropdown-menu dropdown-menu-right pt-theme-picker__menu" role="menu" aria-label="${label}">
			${items}
		</div>`;
	bell.before(picker);

	picker.querySelectorAll("[data-pt-theme]").forEach((item) => {
		item.addEventListener("click", () => {
			pt_choose_theme(PT_THEMES.find((option) => option.id === item.dataset.ptTheme));
		});
	});
	// Frappe's own Toggle Theme can change the theme too; refresh the ticks whenever the menu opens.
	jQuery(picker).on("show.bs.dropdown", pt_sync_picker);
	pt_sync_picker();
}

if (window.jQuery) {
	jQuery(document).on("toolbar_setup", pt_build_picker);
}

// Charts -------------------------------------------------------------------------------------
// frappe-charts writes series colours as inline styles, so CSS cannot recolour them. Pass the
// brand palette in as the chart's own `colors` option instead: accent for the main series, then
// greys stepped from deep. The values come from --pt-chart-1..6, registered with @property in
// _tokens.scss so the browser hands back resolved rgb() colours.

function brand_chart_palette() {
	const style = getComputedStyle(document.documentElement);
	const palette = [];
	for (let i = 1; i <= 6; i++) {
		const hex = rgb_to_hex(style.getPropertyValue(`--pt-chart-${i}`).trim());
		if (!hex) return null;
		palette.push(hex);
	}
	return palette;
}

// Browsers report registered colours as rgb(0-255 ...) or, for color-mix() results,
// color(srgb 0-1 ...). frappe-charts needs #rrggbb.
function rgb_to_hex(value) {
	if (/^#[0-9a-f]{6}$/i.test(value)) return value;
	let channels;
	const rgb = value.match(/^rgba?\(\s*([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)/i);
	const srgb = value.match(/^color\(\s*srgb\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)/i);
	if (rgb) channels = rgb.slice(1, 4).map(Number);
	else if (srgb) channels = srgb.slice(1, 4).map((n) => Number(n) * 255);
	else return null;
	return "#" + channels.map((n) => Math.round(n).toString(16).padStart(2, "0")).join("");
}

function with_brand_colors(options = {}) {
	const palette = brand_chart_palette();
	if (!palette) return options;
	if (options.type === "heatmap") {
		// Five levels: an empty grey, then the accent at rising strength.
		const accent = palette[0];
		const base = palette[5];
		return { ...options, colors: [base, mix(accent, base, 0.3), mix(accent, base, 0.55), mix(accent, base, 0.8), accent] };
	}
	return { ...options, colors: palette };
}

// Mix two #rrggbb colours; weight is the share of the first.
function mix(a, b, weight) {
	const channel = (hex, i) => parseInt(hex.slice(1 + i * 2, 3 + i * 2), 16);
	return (
		"#" +
		[0, 1, 2]
			.map((i) => Math.round(channel(a, i) * weight + channel(b, i) * (1 - weight)))
			.map((n) => n.toString(16).padStart(2, "0"))
			.join("")
	);
}

if (window.frappe && frappe.Chart) {
	const FrappeChart = frappe.Chart;
	frappe.Chart = class PositiveChart extends FrappeChart {
		constructor(parent, options) {
			super(parent, with_brand_colors(options));
		}
	};
}

// Forms --------------------------------------------------------------------------------------
// Cancelled and Overdue share Frappe's red indicator. Expose the docstatus on the form page so
// _indicators.scss can give Cancelled its own struck-through style.
if (window.jQuery) {
	jQuery(document).on("form-refresh", (event, frm) => {
		if (frm && frm.page && frm.doc) {
			frm.page.wrapper.attr("data-pt-docstatus", frm.doc.docstatus);
		}
	});
}

// Login page (www/login.html) ----------------------------------------------------------------
// Frappe's login.js does the actual sign-in. These handlers only expose its state to CSS.
if (window.jQuery) {
	const $doc = jQuery(document);

	// Loading state on the submit button while the request is in flight; clear an old error.
	$doc.on("submit", ".pt-login form", (event) => {
		const $form = jQuery(event.currentTarget);
		$form.find(".page-card-body").removeClass("invalid");
		$form.find("button[type=submit]").attr("aria-busy", "true");
	});
	$doc.on("ajaxComplete", () => {
		jQuery(".pt-login [aria-busy=true]").removeAttr("aria-busy");
	});

	// Password show/hide: login.js swaps the input type; mirror it for assistive tech.
	$doc.on("click", ".pt-login .toggle-password", (event) => {
		const $toggle = jQuery(event.currentTarget);
		const shown = jQuery($toggle.attr("toggle")).attr("type") === "text";
		$toggle.attr("aria-pressed", String(shown));
	});
}
