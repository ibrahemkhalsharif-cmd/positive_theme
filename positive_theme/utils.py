"""Brand values for places that cannot use CSS variables (print, PDF, email, letter head).

The values are read from public/scss/_tokens.scss so that file stays the single source of
every colour in the app.
"""

import base64
import re
from functools import cache

import frappe

TOKEN_RE = re.compile(r"--pt-([a-z0-9-]+):\s*(#[0-9a-fA-F]{3,8})\s*;")

PRINT_FONTS = (
	# family, weight, file in public/fonts
	("Poppins", 400, "poppins-latin-regular.ttf"),
	("Poppins", 600, "poppins-latin-semibold.ttf"),
	("Poppins", 700, "poppins-latin-bold.ttf"),
	("Tajawal", 400, "tajawal-arabic-regular.ttf"),
	("Tajawal", 700, "tajawal-arabic-bold.ttf"),
)


@cache
def _read_tokens() -> dict:
	path = frappe.get_app_path("positive_theme", "public", "scss", "_tokens.scss")
	with open(path, encoding="utf-8") as f:
		return {name.replace("-", "_"): value for name, value in TOKEN_RE.findall(f.read())}


@cache
def _data_uri(relative_path: str, mime: str) -> str:
	path = frappe.get_app_path("positive_theme", "public", *relative_path.split("/"))
	with open(path, "rb") as f:
		return f"data:{mime};base64,{base64.b64encode(f.read()).decode()}"


def brand_tokens() -> frappe._dict:
	"""Brand colours plus print helpers, exposed to Jinja as brand_tokens()."""
	tokens = frappe._dict(_read_tokens())
	tokens.logo_data_uri = _data_uri("images/positive-horizontal-indigo.png", "image/png")
	tokens.font_face_css = print_font_face_css()
	return tokens


@cache
def print_font_face_css() -> str:
	"""@font-face rules with the fonts inlined, so wkhtmltopdf needs no network or file access."""
	rules = []
	for family, weight, file in PRINT_FONTS:
		src = _data_uri(f"fonts/{file}", "font/ttf")
		rules.append(
			f'@font-face{{font-family:"{family}";font-weight:{weight};font-style:normal;'
			f'src:url("{src}") format("truetype");}}'
		)
	return "\n".join(rules)
