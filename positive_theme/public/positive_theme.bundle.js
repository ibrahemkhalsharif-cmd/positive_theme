// Positive theme for ERPNext: small behaviour hooks for desk and website pages.
// Rules for this file: no inline styles, no polling or interval-based DOM patching. It only
// sets attributes and passes options; all visuals live in the SCSS.

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
