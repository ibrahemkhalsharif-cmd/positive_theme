"""Install and uninstall steps for site settings the hooks cannot reach.

Everything set here is recorded first and put back in before_uninstall, so after
`bench --site <site> uninstall-app positive_theme` the site looks exactly like stock.
"""

import json

import frappe

from positive_theme.utils import brand_tokens

LOGO_URL = "/assets/positive_theme/images/positive-horizontal-indigo-on-dark.svg"
LETTER_HEAD = "Positive"
BRAND_NAME = "Positive"
PREV_LOGO_KEY = "positive_theme_previous_app_logo"
SET_DEFAULT_LH_KEY = "positive_theme_set_default_letter_head"
PREV_APP_NAMES_KEY = "positive_theme_previous_app_names"
HIDDEN_HELP_KEY = "positive_theme_hidden_help_items"
PALETTE_KEY = "pt_palette"  # per-user theme picker choice (positive_theme.bundle.js)

# Help menu entries that point at Frappe / ERPNext (their sites, or the About box listing them).
VENDOR_HELP = ("frappe.io", "erpnext.com", "discuss.frappe.io", "github.com/frappe", "show_about")


def after_install():
	set_navbar_logo()
	create_letter_head()
	apply_brand_settings()


def before_uninstall():
	restore_navbar_logo()
	remove_letter_head()
	restore_brand_settings()
	frappe.db.delete("DefaultValue", {"defkey": PALETTE_KEY})


def apply_brand_settings():
	"""Name the app "Positive" and hide Help menu entries that lead to Frappe / ERPNext."""
	if frappe.db.get_default(PREV_APP_NAMES_KEY) is None:
		previous = {
			"System Settings": frappe.db.get_single_value("System Settings", "app_name"),
			"Website Settings": frappe.db.get_single_value("Website Settings", "app_name"),
		}
		frappe.db.set_default(PREV_APP_NAMES_KEY, json.dumps(previous))
	for doctype in ("System Settings", "Website Settings"):
		frappe.db.set_single_value(doctype, "app_name", BRAND_NAME)

	settings = frappe.get_single("Navbar Settings")
	hidden = json.loads(frappe.db.get_default(HIDDEN_HELP_KEY) or "[]")
	for row in settings.help_dropdown:
		target = row.route or row.action or ""
		if not row.hidden and any(v in target for v in VENDOR_HELP):
			row.hidden = 1
			hidden.append(row.name)
	settings.save(ignore_permissions=True)
	frappe.db.set_default(HIDDEN_HELP_KEY, json.dumps(hidden))


def restore_brand_settings():
	previous = frappe.db.get_default(PREV_APP_NAMES_KEY)
	if previous is not None:
		for doctype, value in json.loads(previous).items():
			if frappe.db.get_single_value(doctype, "app_name") == BRAND_NAME:
				frappe.db.set_single_value(doctype, "app_name", value)
		frappe.defaults.clear_default(PREV_APP_NAMES_KEY)

	hidden = set(json.loads(frappe.db.get_default(HIDDEN_HELP_KEY) or "[]"))
	if hidden:
		settings = frappe.get_single("Navbar Settings")
		for row in settings.help_dropdown:
			if row.name in hidden:
				row.hidden = 0
		settings.save(ignore_permissions=True)
	frappe.defaults.clear_default(HIDDEN_HELP_KEY)


def set_navbar_logo():
	settings = frappe.get_single("Navbar Settings")
	frappe.db.set_default(PREV_LOGO_KEY, settings.app_logo or "")
	settings.app_logo = LOGO_URL
	settings.save(ignore_permissions=True)


def restore_navbar_logo():
	settings = frappe.get_single("Navbar Settings")
	if settings.app_logo == LOGO_URL:
		settings.app_logo = frappe.db.get_default(PREV_LOGO_KEY) or None
		settings.save(ignore_permissions=True)
	frappe.defaults.clear_default(PREV_LOGO_KEY)


def create_letter_head():
	if frappe.db.exists("Letter Head", LETTER_HEAD):
		return

	no_default_yet = not frappe.db.get_value("Letter Head", {"is_default": 1})
	frappe.get_doc(
		{
			"doctype": "Letter Head",
			"letter_head_name": LETTER_HEAD,
			"source": "HTML",
			"content": letter_head_html(),
			"footer_source": "HTML",
			"footer": letter_head_footer_html(),
			"is_default": 1 if no_default_yet else 0,
		}
	).insert(ignore_permissions=True)
	frappe.db.set_default(SET_DEFAULT_LH_KEY, "1" if no_default_yet else "")


def remove_letter_head():
	if frappe.db.exists("Letter Head", LETTER_HEAD):
		frappe.delete_doc("Letter Head", LETTER_HEAD, ignore_permissions=True, force=True)
	frappe.defaults.clear_default(SET_DEFAULT_LH_KEY)


def letter_head_html() -> str:
	# A float rather than flexbox (wkhtmltopdf predates flexbox) and no table: Frappe's print styles
	# force "td img { width: 100% !important }", which would stretch the logo out of proportion.
	t = brand_tokens()
	return f"""
<div style="overflow: hidden; padding-bottom: 10px; border-bottom: 2px solid {t.accent};" dir="ltr">
	<div style="float: right; padding-top: 18px; font-family: Poppins, Tajawal, sans-serif;
		font-size: 11px; color: {t.deep};">Simply Smarter</div>
	<img src="{t.logo_data_uri}" alt="Positive" width="159" height="52"
		style="display: block; width: 159px; height: 52px;">
</div>
"""


def letter_head_footer_html() -> str:
	t = brand_tokens()
	return f"""
<div style="border-top: 1px solid {t.deep}; padding-top: 6px; text-align: center;
	font-family: Poppins, Tajawal, sans-serif; font-size: 9px; color: {t.deep};">
	Positive · Simply Smarter
</div>
"""
