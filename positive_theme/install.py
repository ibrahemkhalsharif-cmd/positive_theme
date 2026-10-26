"""Install and uninstall steps for site settings the hooks cannot reach.

Everything set here is recorded first and put back in before_uninstall, so after
`bench --site <site> uninstall-app positive_theme` the site looks exactly like stock.
"""

import frappe

from positive_theme.utils import brand_tokens

LOGO_URL = "/assets/positive_theme/images/positive-horizontal-indigo-on-dark.svg"
LETTER_HEAD = "Positive"
PREV_LOGO_KEY = "positive_theme_previous_app_logo"
SET_DEFAULT_LH_KEY = "positive_theme_set_default_letter_head"


def after_install():
	set_navbar_logo()
	create_letter_head()


def before_uninstall():
	restore_navbar_logo()
	remove_letter_head()


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
