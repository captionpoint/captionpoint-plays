#!/usr/bin/env python3
"""
Custom CaptionPoint converter for Goodnight Moon.

Handles the show's gotchas:
  * Songs in ALL CAPS that masquerade as character lines.
  * Call/response parentheticals inside songs that must be PRESERVED
    (e.g. HEY DIDDLE DIDDLE / (HEY DIDDLE DIDDLE)).
  * Stage-direction parentheticals that must be REMOVED
    (e.g. BUNNY (Sings), OLD LADY (Evenly), (He runs in...)).
  * Character names on their own line WITHOUT a trailing colon.
  * Inline "CHARACTER: dialogue" and "CHARACTER: (action)" lines.
  * Pagination filler, song labels, scene/act markers, front matter.
  * Compound speakers (BUNNY & MOUSE, CAT, DOG & DISH/SPOON, etc.).
"""

import re
import sys
from pathlib import Path

# --- known characters --------------------------------------------------------

PRIMARY = [
    'BUNNY', 'OLD LADY', 'MOUSE', 'CAT', 'DOG', 'DISH/SPOON', 'DISH', 'SPOON',
    'CLARABELLE', 'COW', 'MOON', 'MANTLE CLOCK', 'CLOCK', 'TELEPHONE', 'BALLOON',
    'FIRE', 'LAMP', 'BEARS', 'TOOTH FAIRY', 'FAIRY', 'FAIRIES', 'KITTENS',
    'CHORUS', 'ALL', 'BOTH', 'COMPANY', 'ENSEMBLE', 'VOICEOVERS',
]
# Sort longer-first so e.g. "TOOTH FAIRY" wins over "FAIRY".
PRIMARY_SORTED = sorted(PRIMARY, key=len, reverse=True)

NAME_PIECE = r'(?:' + '|'.join(re.escape(p) for p in PRIMARY_SORTED) + r')'
COMPOUND   = NAME_PIECE + r'(?:\s*(?:&|,|/| AND )\s*' + NAME_PIECE + r')*'
SPEAKER_RE = re.compile(
    r'^\s*(?P<who>' + COMPOUND + r')\s*'
    r'(?:\([^)]*\))?'                  # optional stage-direction paren
    r'\s*[:.]?\s*$'                    # optional trailing : or .
)
INLINE_SPEAKER_RE = re.compile(
    r'^\s*(?P<who>' + COMPOUND + r')\s*'
    r'(?:\([^)]*\))?'                  # optional stage-direction paren
    r'\s*[:.]\s*(?P<rest>.+)$'         # MUST have trailing text after :/.
)
# A line like "OLD LADY (Retrieves each doll and brings it to the bed.) All right."
# — speaker, paren(s), dialogue. Same as INLINE_SPEAKER_RE but no colon required.
PAREN_THEN_LINE_RE = re.compile(
    r'^\s*(?P<who>' + COMPOUND + r')\s*'
    r'\((?P<paren>[^)]*)\)\s*'
    r'(?P<rest>.+)$'
)

# --- junk patterns -----------------------------------------------------------

# Whole-line junk to drop.
JUNK_LINE_RE = re.compile(
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

# Whole-line parenthetical (pure stage direction). Tolerates trailing
# punctuation like `(...).` or `(...)?` since scripts often have a final
# period outside the closing paren.
WHOLE_PAREN_RE = re.compile(r'^\s*\([^()]*\)\s*[.,;:!?]*\s*$')

# Mid-line parenthetical (for dialogue lines, not song lines).
PAREN_RE = re.compile(r'\s*\([^)]*\)')

# --- song detection ----------------------------------------------------------

def is_song_line(line: str) -> bool:
    """True iff the line looks like a song lyric (predominantly uppercase)."""
    letters = re.sub(r'[^A-Za-z]', '', line)
    if len(letters) < 3:
        return False
    upper = sum(1 for c in letters if c.isupper())
    return (upper / len(letters)) >= 0.85


def is_song_block_line(idx: int, lines: list[str]) -> bool:
    """A song block line is all-caps AND has another all-caps line as its
    nearest non-blank neighbor. Excludes isolated all-caps lines (which are
    almost always speaker names, not lyrics)."""
    if not is_song_line(lines[idx].strip()):
        return False
    for i in range(idx - 1, -1, -1):
        if lines[i].strip():
            if is_song_line(lines[i].strip()):
                return True
            break
    for i in range(idx + 1, len(lines)):
        if lines[i].strip():
            if is_song_line(lines[i].strip()):
                return True
            break
    return False


def strip_multiline_parens(text: str) -> str:
    """Remove parenthetical content that SPANS lines. Single-line
    balanced parens pass through untouched so downstream handlers can
    decide whether they're stage direction (drop), short vocalization
    like `(Growl.)` (keep as `[Growl.]`), or song echo (keep verbatim).
    A known speaker line resets paren depth — defends against authorial
    sloppiness where a closing ')' was forgotten."""
    lines = text.splitlines()
    out: list[str] = []
    depth = 0
    for idx, raw in enumerate(lines):
        stripped = raw.strip()
        if SPEAKER_RE.match(stripped):
            depth = 0
        if depth == 0 and is_song_block_line(idx, lines):
            out.append(raw)
            continue
        start_depth = depth
        opens = raw.count('(')
        closes = raw.count(')')
        end_depth = max(0, depth + opens - closes)
        if start_depth == 0 and end_depth == 0:
            # Self-contained line; let downstream decide.
            out.append(raw)
            continue
        # Crossing a line boundary — strip chars inside open parens.
        result = []
        for ch in raw:
            if ch == '(':
                depth += 1
            elif ch == ')':
                if depth > 0:
                    depth -= 1
            elif depth == 0:
                result.append(ch)
        out.append(''.join(result).rstrip())
    return '\n'.join(out)


# --- preprocessing -----------------------------------------------------------

def preprocess(text: str) -> list[dict]:
    """
    Walk the raw script, return a flat list of slides:
      {'type': 'header', 'who': 'BUNNY'}                — character speaker
      {'type': 'dialogue', 'text': '...'}               — spoken text
      {'type': 'lyric',    'text': '...'}               — sung lyric (keeps parens)
    Caller assembles slides per CaptionPoint conventions.
    """
    # First: clean up multi-line stage-direction blocks. The Goodnight Moon
    # script has several unclosed `(` blocks spanning multiple paragraphs.
    text = strip_multiline_parens(text)

    lines = text.splitlines()
    slides: list[dict] = []
    current_speaker: str | None = None

    # Skip front matter: find the first line that is a known character speaker.
    known = ('BUNNY', 'OLD LADY', 'MOUSE', 'CAT', 'DOG', 'CLARABELLE', 'BEARS')
    start = 0
    for i, raw in enumerate(lines):
        s = raw.strip().rstrip(':.').strip()
        s = re.sub(r'\s*\([^)]*\)\s*$', '', s).strip()
        if s in known:
            start = i
            break

    for raw in lines[start:]:
        line = raw.rstrip()
        stripped = line.strip()

        if not stripped:
            continue
        if JUNK_LINE_RE.match(stripped):
            continue
        if WHOLE_PAREN_RE.match(stripped):
            inner = re.sub(r'^\s*\(|\)\s*[.,;:!?]*\s*$', '', stripped).strip()
            # If inner content is all-caps, it's a sung call/response echo
            # — keep the parens intact as a lyric line.
            if is_song_line(inner):
                if current_speaker and inner:
                    slides.append({'type': 'lyric', 'text': f'({inner})'})
                continue
            # Short non-song parens under a speaker (Growl., Squeak,
            # Moo) are vocalizations to caption.
            if current_speaker and inner and len(inner.split()) <= 6:
                slides.append({'type': 'stage', 'text': inner})
            # Otherwise pure stage direction — drop.
            continue

        # Speaker on its own line (possibly with parenthetical action).
        m = SPEAKER_RE.match(stripped)
        if m:
            who = normalize_who(m.group('who'))
            slides.append({'type': 'header', 'who': who})
            current_speaker = who
            continue

        # Inline "CHARACTER: dialogue" or "CHARACTER. dialogue".
        m = INLINE_SPEAKER_RE.match(stripped)
        if m:
            who = normalize_who(m.group('who'))
            rest = m.group('rest').strip()
            slides.append({'type': 'header', 'who': who})
            current_speaker = who
            # Treat the rest as dialogue or lyric based on caps ratio.
            slides.append({
                'type': 'lyric' if is_song_line(rest) else 'dialogue',
                'text': clean_text(rest, is_song_line(rest)),
            })
            continue

        # "CHARACTER (stage direction) dialogue" inline.
        m = PAREN_THEN_LINE_RE.match(stripped)
        if m and m.group('rest').strip() and not is_song_line(stripped):
            who = normalize_who(m.group('who'))
            rest = m.group('rest').strip()
            slides.append({'type': 'header', 'who': who})
            current_speaker = who
            slides.append({
                'type': 'lyric' if is_song_line(rest) else 'dialogue',
                'text': clean_text(rest, is_song_line(rest)),
            })
            continue

        # Otherwise: continuation of the current speaker. Decide song vs dialogue.
        song = is_song_line(stripped)
        cleaned = clean_text(stripped, song)
        if not cleaned:
            continue
        if current_speaker is None:
            # Orphan line before any speaker — skip (probably stage direction).
            continue
        slides.append({
            'type': 'lyric' if song else 'dialogue',
            'text': cleaned,
        })

    return slides


def normalize_who(raw: str) -> str:
    """Tidy speaker name: collapse whitespace, normalize separators."""
    s = re.sub(r'\s*&\s*', ' & ', raw)
    s = re.sub(r'\s*,\s*', ', ', s)
    s = re.sub(r'\s*/\s*', '/', s)
    s = re.sub(r'\s+AND\s+', ' & ', s, flags=re.IGNORECASE)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def clean_text(text: str, is_song: bool) -> str:
    """Strip stage-direction parens from dialogue. KEEP parens in songs."""
    if not is_song:
        text = PAREN_RE.sub('', text)
        # Collapse repeated punctuation orphans left by paren removal:
        # "telephone; ; and" -> "telephone; and", "stuff..." stays as-is.
        text = re.sub(r'\s+([,.;:!?])', r'\1', text)         # space-before-punct
        text = re.sub(r'([,;:!?])(?:\s*\1)+', r'\1', text)   # ;; -> ;
        text = re.sub(r'[,;:!?]+(?=[.])', '', text)          # ;.  -> .
    text = re.sub(r'\s+', ' ', text).strip()
    # Drop standalone bracket/paren orphans (e.g. ":)").
    text = re.sub(r'^[)\]]\s*', '', text)
    text = re.sub(r'\s*[(\[]$', '', text)
    # Drop a leading orphan period left over after the regex removed a
    # whole `(...)` from the start of a dialogue line.
    text = re.sub(r'^[.,;:!?\s]+', '', text)
    return text.strip()


WORDISH_RE = re.compile(r'[A-Za-z0-9]')


def has_words(text: str) -> bool:
    return bool(WORDISH_RE.search(text))


# --- slide assembly ----------------------------------------------------------

def split_sentences(text: str) -> list[str]:
    parts = re.split(r'(?<=[.!?])\s+(?=[A-Za-z"\'])', text)
    return [p.strip() for p in parts if p.strip()]


def chunk_dialogue(text: str, max_chars: int = 150) -> list[str]:
    sentences = split_sentences(text)
    if not sentences:
        return []
    chunks: list[str] = []
    cur: list[str] = []
    cur_len = 0
    for s in sentences:
        ls = len(s)
        if ls > max_chars and not cur:
            chunks.append(s)
            continue
        if cur and cur_len + ls + 1 > max_chars:
            chunks.append(' '.join(cur))
            cur = [s]
            cur_len = ls
        else:
            cur.append(s)
            cur_len += ls + (1 if cur else 0)
    if cur:
        chunks.append(' '.join(cur))
    return chunks


def chunk_lyric_block(lines: list[str], max_chars: int = 200) -> list[str]:
    """For a run of consecutive sung lyric lines, group by line-length budget."""
    if not lines:
        return []
    chunks: list[str] = []
    cur: list[str] = []
    cur_len = 0
    for ln in lines:
        ls = len(ln)
        if cur and cur_len + ls + 1 > max_chars:
            chunks.append('\n'.join(cur))
            cur = [ln]
            cur_len = ls
        else:
            cur.append(ln)
            cur_len += ls + (1 if cur else 0)
    if cur:
        chunks.append('\n'.join(cur))
    return chunks


def assemble(slides: list[dict], max_dialogue: int = 150, max_lyric: int = 200) -> str:
    """Produce CaptionPoint markdown: ## CHAR: header, then dialogue/lyric slides."""
    out: list[str] = []
    i = 0
    n = len(slides)
    while i < n:
        s = slides[i]
        if s['type'] != 'header':
            i += 1
            continue
        who = s['who']
        # Collect contiguous dialogue/lyric run for this speaker, until next header.
        j = i + 1
        run: list[dict] = []
        while j < n and slides[j]['type'] != 'header':
            run.append(slides[j])
            j += 1

        if not run:
            # Speaker with nothing under it (their only content was a stage
            # direction that got stripped). Drop the orphan header entirely.
            i = j
            continue

        # Group consecutive lyrics together, dialogue together.
        group: list[dict] = [run[0]]
        for item in run[1:]:
            if item['type'] == group[-1]['type']:
                group.append(item)
            else:
                _emit_group(out, who, group, max_dialogue, max_lyric)
                group = [item]
        _emit_group(out, who, group, max_dialogue, max_lyric)
        i = j

    body = '\n\n---\n\n'.join(out)
    if body:
        body += '\n\n---\n'
    return body


def _emit_group(out: list[str], who: str, group: list[dict],
                max_dialogue: int, max_lyric: int) -> None:
    group = [g for g in group if has_words(g['text'])]
    if not group:
        return
    real = [g for g in group if g['type'] in ('dialogue', 'lyric')]
    if not real:
        # Speaker has only short stage vocalizations — render them in
        # brackets so the audience gets a sound cue (e.g. "[Growl.]").
        for s in group:
            out.append(f'## {who}:\n[{s["text"]}]')
        return
    # Drop stage cues when real dialogue/lyric exists — they're meta.
    group = real
    if group[0]['type'] == 'dialogue':
        joined = ' '.join(g['text'] for g in group)
        chunks = chunk_dialogue(joined, max_dialogue)
        if not chunks:
            chunks = [joined] if joined else []
        chunks = [c for c in chunks if has_words(c)]
        for c in chunks:
            out.append(f'## {who}:\n{c}')
    else:  # lyric
        chunks = chunk_lyric_block([g['text'] for g in group], max_lyric)
        chunks = [c for c in chunks if has_words(c)]
        for c in chunks:
            out.append(f'## {who}:\n{c}')


# --- main --------------------------------------------------------------------

CLOSING_SLIDE = """---
class: title
Open Captioning for this performance was made possible by CaptionPoint.
"""


def main():
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2])
    raw = src.read_text(encoding='utf-8')
    slides = preprocess(raw)
    header_count = sum(1 for s in slides if s['type'] == 'header')
    dialogue_count = sum(1 for s in slides if s['type'] == 'dialogue')
    lyric_count = sum(1 for s in slides if s['type'] == 'lyric')
    print(f'Preprocess: {header_count} speakers, '
          f'{dialogue_count} dialogue, {lyric_count} lyric chunks')

    body = assemble(slides)
    final = body + CLOSING_SLIDE
    dst.write_text(final)
    slide_count = final.count('\n---\n')
    print(f'Wrote {dst} ({len(final)} chars, ~{slide_count} slides)')


if __name__ == '__main__':
    main()
