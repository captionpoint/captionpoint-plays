# CaptionPoint Verification Report

**Overall:** FAIL
**PDF:** `/private/tmp/claude-501/-Users-macnab-Projects-CaptionPoint-captionpoint-plays/7319fcb2-c0c9-4515-b2ee-a757b3732a9c/scratchpad/front-page-prepped.md`
**Markdown:** `/private/tmp/claude-501/-Users-macnab-Projects-CaptionPoint-captionpoint-plays/7319fcb2-c0c9-4515-b2ee-a757b3732a9c/scratchpad/FRONT-PAGE.md`

---

## multiset_diff — PASS

- **total_pdf_words:** `14734`
- **total_md_words:** `14903`
- **real_pdf_words:** `11824`
- **real_words_dropped:** `1`
- **ocr_noise_dropped:** `1`
- **real_drop_ratio:** `8e-05`
- **tolerance:** `0.005`
- **top_real_missing:**
    - `('gold', 1)`
- **top_noise_missing:**
    - `('darlingbrad', 1)`

## phrase_anchors — FAIL

- **sampled_count:** `20`
- **missing_count:** `1`
- **missing_phrases:**
    - `not kidding hartman gave`

## turn_count_sanity — PASS

- **pdf_turns:** `1174`
- **md_turns:** `1318`
- **ratio:** `1.123`
- **tolerance_floor:** `0.9`
