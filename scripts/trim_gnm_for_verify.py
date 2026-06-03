#!/usr/bin/env python3
"""
Trim the Goodnight Moon source down to the lines that REPRESENT spoken or
sung text in performance. This lets Verify.py compare apples-to-apples: it
already knows how to strip parenthetical stage directions and ACT markers,
but it can't tell that the opening prose-paragraph scene description and
the "Song:"/"#1:" labels are non-dialogue text that should never be captioned.
"""

import re
import sys
from pathlib import Path

JUNK = re.compile(
    r'^\s*('
    r'Curtain\.?'
    r'|End of Act.*'
    r'|ACT\s+(I|II|III|IV|V|\d+|ONE|TWO|THREE|FOUR|FIVE).*'
    r'|Act\s+(I|II|III|IV|V|\d+|One|Two|Three|Four|Five).*'
    r'|Scene\s+.*'
    r'|Intentionally left blank.*'
    r'|Song:.*'
    r'|#\d+:.*'
    r'|copyright .*'
    r')\s*$',
    re.IGNORECASE,
)


def main():
    src = Path(sys.argv[1]).read_text(encoding='utf-8')
    lines = src.splitlines()
    # Find first speaker line (ALL-CAPS standalone) to skip front matter.
    # Hard-coded known characters to recognize the first speaker line
    # (avoids treating "GOODNIGHT MOON" or other front-matter all-caps lines
    # as speakers).
    known = (
        'BUNNY', 'OLD LADY', 'MOUSE', 'CAT', 'DOG', 'CLARABELLE', 'MOON',
        'CLOCK', 'TELEPHONE', 'BEARS', 'TOOTH FAIRY', 'FAIRY',
    )
    start = 0
    for i, l in enumerate(lines):
        stripped = l.strip().rstrip(':.').strip()
        # tolerate trailing "(Sings)" etc.
        stripped = re.sub(r'\s*\([^)]*\)\s*$', '', stripped).strip()
        if stripped in known:
            start = i
            break
    keep = [l for l in lines[start:] if not JUNK.match(l)]
    Path(sys.argv[2]).write_text('\n'.join(keep))
    print(f'Trimmed {len(lines)} -> {len(keep)} lines (dropped front matter & labels)')


if __name__ == '__main__':
    main()
