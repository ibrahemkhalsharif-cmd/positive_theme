"""Server side of the navbar theme picker (positive_theme.bundle.js)."""

import frappe

PALETTE_KEY = "pt_palette"
PALETTES = ("", "red")


@frappe.whitelist()
def set_palette(palette: str = ""):
	"""Save the signed-in user's colour set: "" for the brand default (indigo) or "red"."""
	if palette not in PALETTES:
		frappe.throw(frappe._("Unknown colour set"))
	frappe.defaults.set_user_default(PALETTE_KEY, palette)
	return palette


def boot_session(bootinfo):
	"""Send the user's colour set with the desk boot, so it applies before the desk renders."""
	if frappe.session.user != "Guest":
		bootinfo.pt_palette = frappe.defaults.get_user_default(PALETTE_KEY) or ""
