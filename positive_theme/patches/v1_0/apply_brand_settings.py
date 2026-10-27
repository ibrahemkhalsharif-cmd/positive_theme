"""Sites that installed positive_theme before the brand settings existed get them on migrate."""

from positive_theme.install import apply_brand_settings


def execute():
	apply_brand_settings()
