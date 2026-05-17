.PHONY: check check-links check-frontmatter check-readmes readmes

check: check-readmes check-frontmatter check-links

check-links:
	uv run scripts/check-links.py

check-frontmatter:
	uv run scripts/check-frontmatter.py

check-readmes:
	uv run scripts/generate-readmes.py --check

readmes:
	uv run scripts/generate-readmes.py
