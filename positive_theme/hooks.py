app_name = "positive_theme"
app_title = "Positive Theme"
app_publisher = "Ibrahem"
app_description = "Positive brand theme for ERPNext: tokens, fonts, login page, desk, print and email"
app_email = "ibrahemkhalsharif@gmail.com"
app_license = "mit"

# Everything below is injected through hooks; nothing in frappe, erpnext or hrms is changed.

# Assets
# ------
# Built by Frappe's esbuild pipeline (bench build --app positive_theme) from public/*.bundle.*

app_include_css = "positive_theme.bundle.css"
app_include_js = "positive_theme.bundle.js"
web_include_css = "positive_theme.bundle.css"
web_include_js = "positive_theme.bundle.js"

# Brand images
# ------------

app_logo_url = "/assets/positive_theme/images/positive-horizontal-indigo-on-dark.svg"

website_context = {
	"favicon": "/assets/positive_theme/images/positive-icon-indigo-dark.svg",
	"splash_image": "/assets/positive_theme/images/positive-icon-indigo-dark.svg",
}

# Email
# -----
# Email clients do not render SVG, so email uses the PNG export. `embed` makes Frappe attach the
# image inline (cid:) instead of linking to the site.

email_brand_image = "assets/positive_theme/images/positive-horizontal-indigo.png"

default_mail_footer = """
	<div class="positive-mail-footer">
		<img embed="assets/positive_theme/images/positive-horizontal-indigo.png"
			alt="Positive" width="140" height="46">
		<div>Simply Smarter</div>
	</div>
"""

# Print
# -----
# Print and PDF cannot read CSS variables, so templates get the brand values from the tokens file.

jinja = {
	"methods": ["positive_theme.utils.brand_tokens"],
}

# Install / uninstall
# -------------------

after_install = "positive_theme.install.after_install"
before_uninstall = "positive_theme.install.before_uninstall"
