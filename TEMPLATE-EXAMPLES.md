# Template Configuration Examples

This document shows how to use YAML frontmatter to configure different aspect ratios and font sizes in your CaptionPoint presentations.

## Example 1: Ultra-wide 58:9 ratio with smaller font

```markdown
---
title: My Ultra-Wide Play
ratio: 58:9
fontSize: 3rem
---

class: center, middle
## CHARACTER ONE:
This is dialogue for the ultra-wide screen.

---

## CHARACTER TWO:
More dialogue here.
```

## Example 2: Standard 16:9 ratio

```markdown
---
title: My Standard Play
ratio: 16:9
fontSize: 4rem
---

class: center, middle
## CHARACTER ONE:
Standard 16:9 aspect ratio.
```

## Example 3: 4:3 Classic ratio

```markdown
---
title: My Classic Play
ratio: 4:3
fontSize: 5rem
---

class: center, middle
## CHARACTER ONE:
Classic 4:3 aspect ratio.
```

## Example 4: Custom ratio (29:9)

```markdown
---
title: My Custom Play
ratio: 29:9
fontSize: 3.5rem
---

class: center, middle
## CHARACTER ONE:
Custom 29:9 aspect ratio.
```

## Available YAML Options

- `title`: The title of your presentation (required)
- `ratio`: The aspect ratio (e.g., '58:9', '16:9', '4:3', '29:9')
- `fontSize`: Custom font size (e.g., '3rem', '4rem', '5.3em')
- `template`: Future feature for pre-defined template sets

## Font Size Guidelines

Based on aspect ratio, here are recommended font sizes:

- **58:9 (ultra-wide)**: `3rem` - `3.5rem`
- **29:9 (wide)**: `3.5rem` - `4rem`
- **16:9 (standard)**: `4rem` - `5rem`
- **4:3 (classic)**: `5rem` - `6rem`

## Notes

- YAML frontmatter must be at the very top of your markdown file
- The ratio setting will override any ratio set in `template/index.html`
- Font size uses CSS units (rem, em, px, etc.)
- These settings work in both the VSCode preview and exported HTML
