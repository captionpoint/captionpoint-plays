# MJ Script Comparison Plan

## Current Status

### Files in Repository
1. **MJ-script.pdf** - Original scanned PDF (image-based, no extractable text)
2. **MJ Script.txt** - OCR'd text export from the PDF (88KB, 3,600 lines)
3. **MJ-clean.txt** - Partially edited output with CaptionPoint markdown formatting (4,456 lines)
4. **MJ-test.md** - Early test conversion (can be deleted)

### What's Been Done
- Created `txt_to_clean_dialogue.py` script that:
  - Skips front matter (copyright, cast list)
  - Removes stage directions in parentheses
  - Removes scene headers
  - Formats character dialogue into clean paragraphs
  - Fixes OCR errors (like "1ARY JANE" → "MARY JANE")
  - Successfully found all 9 characters

### The Problem
- User has manually edited `MJ-clean.txt` with additional cleanup
- Some dialogue sections may be missing from the conversion
- Need to compare original PDF source with cleaned output to identify gaps

## Comparison Strategy

### Option 1: PDF → Text → Compare (Recommended)

If you have the original PDF with extractable text (not the scanned version):

1. **Export fresh text from PDF**:
   ```bash
   # Use Adobe Acrobat or another tool to export text
   # Save as: MJ-Script-OCR-fresh.txt
   ```

2. **Run converter on fresh export**:
   ```bash
   python3 txt_to_clean_dialogue.py MJ-Script-OCR-fresh.txt MJ-raw-fresh.txt
   ```

3. **Compare with your edited version**:
   ```bash
   diff MJ-raw-fresh.txt MJ-clean.txt > differences.txt
   ```

4. **Or use visual diff tool**:
   - VS Code: Right-click files → "Select for Compare" → "Compare with Selected"
   - Command line: `code --diff MJ-raw-fresh.txt MJ-clean.txt`

### Option 2: Manual Section-by-Section Verification

1. **Read through MJ-clean.txt** and note any obvious gaps
2. **Search for specific phrases** in both files:
   ```bash
   # Example: search for a line you remember
   grep -i "specific phrase" "MJ Script.txt"
   grep -i "specific phrase" MJ-clean.txt
   ```

3. **Check character dialogue counts**:
   ```bash
   # Count each character's appearances
   for char in "MARY JANE" "RUTHIE" "SHERRY" "BRIANNE" "AMELIA" "DR. TOROS" "CHAYA" "KAT" "TENKEI"; do
       echo -n "$char source: "
       grep -c "$char\." "MJ Script.txt"
       echo -n "$char cleaned: "
       grep -c "^## $char:" MJ-clean.txt
   done
   ```

### Option 3: Scene Structure Comparison

1. **Extract scene/act markers from source**:
   ```bash
   grep -n -i "scene\|part\|act" "MJ Script.txt" > source-structure.txt
   ```

2. **Check which scenes exist in cleaned file**:
   - Manually verify each scene has corresponding dialogue
   - Look for large gaps in line numbers

## Tools Available

### Python Scripts Created
1. **`txt_to_clean_dialogue.py`** - Main converter (source → clean dialogue)
2. **`find_missing_dialogue.py`** - Comparison tool (may have false positives)
3. **`debug_pdf.py`** - PDF text extraction checker
4. **`chunk_dialogue.py`** - Splits long monologues (for later use)

### Useful Commands

**Search for specific dialogue:**
```bash
grep -i "search phrase" "MJ Script.txt"
grep -i "search phrase" MJ-clean.txt
```

**View specific line ranges:**
```bash
sed -n '100,200p' "MJ Script.txt"  # Lines 100-200
sed -n '100,200p' MJ-clean.txt
```

**Character statistics:**
```bash
# Count dialogue blocks per character
grep -c "^## MARY JANE:" MJ-clean.txt
grep -c "^## RUTHIE:" MJ-clean.txt
# etc.
```

## Next Steps for New Chat

### 1. Clarify Source File
Ask yourself:
- Do I have the PDF with extractable text, or just the scanned PDF?
- Is "MJ Script.txt" (3,600 lines) the complete OCR output?
- Should we re-run conversion on this file to create a fresh baseline?

### 2. Identify Missing Sections
Choose approach:
- **Specific search**: "I know the line about X is missing"
- **Section-based**: "The Brianne scene seems shorter than expected"
- **Complete re-compare**: Generate fresh output and diff with your edits

### 3. Verification Strategy
```bash
# Generate fresh conversion for comparison
python3 txt_to_clean_dialogue.py "MJ Script.txt" MJ-baseline.txt

# Compare with your edited version
code --diff MJ-baseline.txt MJ-clean.txt
```

## Key Questions to Answer

1. **Is "MJ Script.txt" complete?**
   - 3,600 lines seems right for a full play script
   - Does it end with "End of Play" or similar?

2. **What edits did you make to MJ-clean.txt?**
   - Manual cleanup of OCR errors?
   - Removed duplicate lines?
   - Combined split dialogue?

3. **Which sections feel incomplete?**
   - Beginning (Ruthie scene)?
   - Middle (Sherry/Amelia/Brianne)?
   - End (Dr. Toros/Chaya/Kat/Tenkei)?

## Recommended Action

**For your next chat, start with:**

```
I have three files:
1. MJ Script.txt (original OCR export, 3,600 lines)
2. MJ-clean.txt (edited version with CaptionPoint formatting, 4,456 lines)
3. MJ-script.pdf (original scanned PDF)

I need to verify that MJ-clean.txt has all dialogue from the source.
Can you help me:
1. Generate a fresh baseline from MJ Script.txt
2. Do a visual diff with my edited MJ-clean.txt
3. Identify any missing dialogue sections

[Attach: MJ Script.txt, MJ-clean.txt]
```

## Files to Keep

Essential files:
- ✅ `MJ Script.txt` - Source OCR text
- ✅ `MJ-clean.txt` - Your edited version
- ✅ `txt_to_clean_dialogue.py` - Conversion script
- ✅ `chunk_dialogue.py` - For later use
- ✅ `BOILERPLATE.md` - For final CaptionPoint formatting

Can delete:
- ❌ `MJ-test.md` - Early test, superseded
- ❌ `MJ.md` - Empty file from first attempt
- ❌ `find_missing_dialogue.py` - Creates too many false positives

## Final Workflow (Once Verified)

After confirming all dialogue is present:

1. **Add CaptionPoint boilerplate** (from BOILERPLATE.md)
2. **Assign character colors**
3. **Run chunking** if needed:
   ```bash
   python chunk_dialogue.py MJ-clean.txt MJ-final.md 4
   ```
4. **Preview**:
   ```bash
   bs serve
   ```
5. **Export**:
   ```bash
   bs export MJ-final.md
   ```
