#!/usr/bin/env bash
# Build the single-source manuscript and check semantic cross-reference types.
set -euo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
# Freeze the TeX date metadata for reproducible builds of this release.
export SOURCE_DATE_EPOCH=1790006400
export FORCE_SOURCE_DATE=1
cd "$root/manuscript"
if command -v latexmk >/dev/null 2>&1; then
  latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
else
  # Minimal TeX installations may have pdfLaTeX but not latexmk.
  # Three passes settle the bibliography, contents and cross-references.
  for pass in 1 2 3; do
    pdflatex -interaction=nonstopmode -halt-on-error main.tex
  done
fi
python3 "$root/src/check_latex_references.py"
if grep -Eq 'undefined references|undefined citations|multiply defined|Rerun to get cross-references right' main.log; then
  echo 'FAIL: unresolved LaTeX diagnostics' >&2
  exit 1
fi
