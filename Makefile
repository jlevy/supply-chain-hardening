.PHONY: format

# Auto-format Markdown with flowmark (semantic line breaks, smart quotes,
# diff-friendly output). Version pinned for supply-chain safety; bump
# deliberately, not via @latest.
#
# Passing `.` as the target (not a glob like `**/*.md`) lets flowmark-rs
# honor `.flowmarkignore` and `.gitignore`. Globs bypass those ignore
# files; do not switch to a glob without revisiting the ignore-file
# semantics first.
format:
	uvx flowmark-rs@0.2.6 --auto .
