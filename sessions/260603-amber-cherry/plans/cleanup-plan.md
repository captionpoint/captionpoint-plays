# CaptionPoint Folder Cleanup Plan

Goal: consolidate three eras (old Backslide CLI, unfinished VS Code extension, new AI workflow) and separate live work from archives. Reclaim ~160MB.

## ⚠️ Pre-flight: commit existing work first

Your git tree has an **uncommitted in-progress reorg** (GASLIGHT/MIDSUMMER/MY-FAIR-LADY already moved to `!archives/`, `caption_toolkit.py` modified). I'll commit that as-is first so the cleanup is a clean, separate, reversible commit.

```
git add -A && git commit -m "Snapshot before folder cleanup"
```

---

## 1. Delete (reproducible / cruft — all already gitignored)

| Target | Size | Why safe |
|--------|------|----------|
| `dist/` | 90MB | Old exported HTML, regenerable |
| `venv/` | 68MB | Python virtualenv, rebuild via `setup.sh` |
| `__pycache__/` | — | Python cache |
| `.tmp/` | 60KB | Build temp |
| `.DS_Store` (all) | — | macOS cruft |
| `ANGEL-NEXT-DOOR.md.bak` | — | Stray backup |
| `vscode-extension/node_modules` | ~55MB | `npm install` rebuilds |
| `vscode-extension/out` | — | Compiled output, `npm run compile` rebuilds |
| `vscode-extension/test-*.html` | — | Debug scratch files |

## 2. Legacy — move old Backslide CLI to `legacy/backslide/`

Kept (not deleted) since you may want it later:
`backslide.js`, `bin/`, `starter/`, `template/`, `package.json`, `package-lock.json`, `yarn.lock`, `README.md`, `CHANGELOG.md`, `LICENSE`, `.prettierignore`, `.github/`

## 3. VS Code extension — keep, just clean

Stays at `vscode-extension/` (its own folder, ready to return to). Only build artifacts removed (see §1). Source, docs, `.vsix`, and `resources/` preserved.

## 4. Tools — consolidate scattered scripts

```
tools/
├── scripts/        ← all .py from root + scripts/ folder
└── boilerplates/   ← BOILERPLATE.md, PLAY-worksheet.md, theater-templates/*
```
- Root scripts moving in: `caption_toolkit.py`, `chunk_gaslight.py`, `format_fair_lady.py`, `format_gaslight.py`, `format_play_script.py`
- `scripts/` folder contents (6 .py) moving in
- `theater-templates/` (4 boilerplates) → `tools/boilerplates/`

## 5. Archive loose root plays into `!archives/`

| Files | Destination |
|-------|-------------|
| `ANGEL-NEXT-DOOR*` (3, after .bak deleted) | `!archives/ANGEL-NEXT-DOOR/` |
| `GOODNIGHT-MOON*` (4) | `!archives/GOODNIGHT-MOON/` |
| `GUTENBERG.md`, `GUTENBERG.md.verify.md` | `!archives/GUTENBERG/` (joins existing `GUTENBERG-original-script.md`) |
| `aubuelita-broken.md`, `aubuelita-working.md` | `!archives/ABUELITA/` |
| `working-example.md` | `!archives/` |

## 6. Fold `mj-project-archive/` into `!archives/MARY-JANE/`

It's the MARY-JANE play's source material (74 scanned page PNGs + OCR + comparison scripts/reports). Goes alongside the existing `MARY-JANE-chunked.md` / `MARY-JANE-working.md`:
```
!archives/MARY-JANE/
├── MARY-JANE-chunked.md      (existing)
├── MARY-JANE-working.md      (existing)
├── source-files/             (from mj-project-archive)
├── scripts/                  (from mj-project-archive)
└── reports/                  (from mj-project-archive)
```

## 7. Docs cleanup

- Move `How to Run Captions Using CaptionPoint.pdf` → `docs/`
- **Dedup `CLAUDE.md`**: it currently contains two full copies (lines 1–318 and 319–755). Remove the duplicate, keep one clean copy, and update script paths to `tools/scripts/`.

---

## Resulting root

```
captionpoint-plays/
├── !archives/            ← all play scripts (archive)
├── tools/                ← scripts + boilerplates
├── legacy/backslide/     ← old CLI, parked
├── vscode-extension/     ← cleaned, ready to resume
├── docs/                 ← guides + PDF
├── CLAUDE.md             ← deduped
└── [Craft Agent files: sessions/, skills/, sources/, etc. — untouched]
```

## Notes
- All moves via `git mv` so history is preserved.
- Deletions are gitignored/reproducible — nothing tracked is lost.
- Done as one cleanup commit, easy to revert if anything looks off.
- `.gitignore` already covers the deleted dirs; no changes needed there.
