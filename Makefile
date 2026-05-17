.PHONY: check check-links check-frontmatter check-readmes readmes etfs

check: check-readmes check-frontmatter check-links

check-links:
	uv run scripts/check-links.py

check-frontmatter:
	uv run scripts/check-frontmatter.py

check-readmes:
	uv run scripts/generate-readmes.py --check

readmes:
	uv run scripts/generate-readmes.py

etfs:
	uv run skills/justetf/scripts/justetf_etfs.py bulk-update
