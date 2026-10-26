"""Context for the Positive login page (www/login.html in this app).

Frappe looks up www pages in every installed app before frappe itself, so this page replaces
frappe/www/login.html without touching it. All of Frappe's login context (social logins, LDAP,
email link, signup, redirects for logged-in users) still comes from frappe.www.login; this only
adds what the new layout needs.
"""

from urllib.parse import urlencode

import frappe
from frappe.utils import nowdate
from frappe.utils.jinja_globals import is_rtl
from frappe.www import login as frappe_login

no_cache = True

LANGUAGE_SWITCH = {
	# current language -> (language to offer, its label in its own script)
	"ar": ("en", "English"),
	"en": ("ar", "العربية"),
}


def get_context(context):
	context = frappe_login.get_context(context) or context

	lang = (frappe.local.lang or "en").split("-")[0]
	other_lang, other_label = LANGUAGE_SWITCH.get(lang, LANGUAGE_SWITCH["en"])

	args = dict(frappe.local.request.args)
	args["_lang"] = other_lang

	context.pt_lang = lang
	context.pt_dir = "rtl" if is_rtl() else "ltr"
	context.pt_other_lang = other_lang
	context.pt_other_lang_label = other_label
	context.pt_lang_switch_url = "/login?" + urlencode(args)
	context.pt_year = nowdate()[:4]
	context.body_class = "pt-login-body"
	return context
