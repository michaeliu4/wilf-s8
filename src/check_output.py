#!/usr/bin/env python3
"""Retain command output and require a literal marker (optional final \\b)."""
import re, sys
if len(sys.argv)!=2:raise SystemExit('usage: check_output.py MARKER < output')
text=sys.stdin.read(); marker=sys.argv[1]
sys.stdout.write(text)
pattern=re.escape(marker[:-2])+r'\b' if marker.endswith(r'\b') else re.escape(marker)
if re.search(pattern,text) is None:
    print('ERROR: expected output marker missing: '+repr(marker),file=sys.stderr)
    raise SystemExit(1)
