# Remark.js Preview - User Guide

## For Complete Beginners

This extension lets you create beautiful slide presentations using simple markdown files. No configuration needed!

## Installation

1. Download the `.vsix` file
2. Open VS Code
3. Click the Extensions icon in the sidebar (or press `Cmd+Shift+X` on Mac, `Ctrl+Shift+X` on Windows)
4. Click the `...` menu at the top of the Extensions panel
5. Choose "Install from VSIX..."
6. Select the downloaded `.vsix` file
7. Reload VS Code when prompted

## Quick Start (No Setup Required!)

1. **Create a new file** with a `.md` extension (e.g., `my-slides.md`)

2. **Add this simple content**:
   ```markdown
   title: My First Presentation

   ---

   # Hello World!

   This is my first slide

   ---

   # Second Slide

   - Point one
   - Point two
   - Point three

   ---

   # That's it!

   Press `Cmd+Shift+V` (Mac) or `Ctrl+Shift+V` (Windows) to see the preview
   ```

3. **Press `Cmd+Shift+V`** (Mac) or **`Ctrl+Shift+V`** (Windows/Linux)

4. **See your presentation!** The preview appears on the right side

## How to Write Slides

### Slide Separator

Use three dashes (`---`) to create a new slide:

```markdown
---
```

### Headings

```markdown
# Big Heading (H1)
## Medium Heading (H2)
### Small Heading (H3)
```

### Lists

```markdown
- Bullet point
- Another point
  - Nested point

1. Numbered item
2. Another numbered item
```

### Bold and Italic

```markdown
**bold text**
*italic text*
***bold and italic***
```

### Links and Images

```markdown
[Link text](https://example.com)

![Image description](path/to/image.jpg)
```

### Code

Inline code: \`code here\`

Code blocks:
\`\`\`javascript
function hello() {
  console.log('Hello!');
}
\`\`\`

### Two Columns

```markdown
.col-6[
  Left column content here
]

.col-6[
  Right column content here
]
```

## Advanced Features

### Incremental Content

Use `--` to reveal content step by step:

```markdown
# My Slide

First, this appears

--

Then this appears when you click

--

Finally this appears
```

### Slide Classes

Add special effects to slides:

```markdown
class: center, middle

# Centered Content
```

```markdown
class: inverse

# Dark Background Slide
```

### Presenter Notes

Add notes that won't show on slides:

```markdown
# My Slide

Visible content here

???
These are presenter notes - press 'P' during presentation to see them
```

## Keyboard Shortcuts

| Action | Mac | Windows/Linux |
|--------|-----|---------------|
| Open Preview | `Cmd+Shift+V` | `Ctrl+Shift+V` |

### During Presentation

| Action | Key |
|--------|-----|
| Next slide | `→`, `Space`, or `Page Down` |
| Previous slide | `←` or `Page Up` |
| First slide | `Home` |
| Last slide | `End` |
| Presenter mode | `P` |
| Clone presentation | `C` |
| Help | `H` or `?` |

## Customization (Optional!)

Want to customize the look? Create a `template` folder in your workspace:

```
my-presentations/
├── template/
│   ├── style.scss       # Your custom styles
│   ├── index.html       # Your custom template
│   └── remark.min.js    # Local remark.js (optional)
└── my-slides.md
```

If no `template` folder exists, the extension uses beautiful default styles automatically!

## Common Questions

### Q: Do I need to install anything else?

**A:** Nope! Just install the extension and start writing markdown.

### Q: Where are my presentations saved?

**A:** They're just `.md` files in your folder. You can edit them in any text editor!

### Q: Can I export to PDF?

**A:** Yes! During presentation, press `P` for presenter mode, then use your browser's "Print to PDF" feature.

### Q: Can I use images?

**A:** Yes! Just use markdown image syntax: `![Description](path/to/image.jpg)`

### Q: The preview isn't updating

**A:** Make sure you've saved the file (`Cmd+S` / `Ctrl+S`)

### Q: Can I share my presentation?

**A:** Yes! You can:
1. Share the `.md` file (others need this extension)
2. Export to PDF (works anywhere)
3. Export to HTML (advanced - see documentation)

## Tips for Better Presentations

1. **Keep it simple** - One main idea per slide
2. **Use big fonts** - Headings show up well
3. **Images speak** - A picture is worth 1000 words
4. **Practice** - Use presenter mode (`P` key) to rehearse
5. **Less text** - Bullet points, not paragraphs

## Example Presentation

Here's a complete example:

```markdown
title: Amazing Product Launch
class: animation-fade
layout: true

---

class: center, middle

# Amazing Product Launch

## The Future is Here

---

# Why This Matters

--

- Revolutionary technology

--

- Solves real problems

--

- Available today!

---

# Key Features

.col-6[
### For Users
- Easy to use
- Fast
- Reliable
]

.col-6[
### For Business
- Cost effective
- Scalable
- Secure
]

---

class: inverse, center, middle

# Thank You!

Questions?

???
Remember to mention the special launch pricing
```

## Getting Help

- Check the [Remark.js Wiki](https://github.com/gnab/remark/wiki) for more markdown syntax
- Look at the example presentations included with the extension
- Experiment! You can't break anything - it's just text files

## Share Your Presentations!

Made something cool? Share it with others by sending them:
1. Your `.md` file
2. A link to install this extension
3. Any images you used

---

**Happy Presenting!** 🎉

Now go create something amazing!
