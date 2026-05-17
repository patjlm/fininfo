.PHONY: check check-links check-frontmatter

check: check-links check-frontmatter

check-links:
	uv run scripts/check-links.py

check-frontmatter:
	uv run scripts/check-frontmatter.py
