// Positive theme for ERPNext: small behaviour hooks for desk and website pages.
// Rules for this file: no inline styles, no polling or interval-based DOM patching. It only
// sets attributes and passes options; all visuals live in the SCSS.

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
