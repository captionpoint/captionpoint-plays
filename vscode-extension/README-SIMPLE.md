# Remark.js Preview - Simple Guide

## What is This?

This extension lets you create slide presentations using simple text files. Think PowerPoint, but simpler!

## Do I Need to Know Anything Technical?

Nope! If you can write an email, you can create presentations with this tool.

## How Do I Use It?

### Step 1: Create a file

Create a new file ending in `.md` (like `my-presentation.md`)

### Step 2: Write your slides

Type something like this:

```
title: My Presentation

---

# My First Slide

Hello everyone!

---

# My Second Slide

- Point 1
- Point 2
- Point 3
```

### Step 3: See the preview

Press `Cmd+Shift+V` (Mac) or `Ctrl+Shift+V` (Windows/Linux)

That's it! Your presentation appears on the right side.

## What Does `---` Mean?

The three dashes (`---`) create a new slide. That's how you separate slides.

## How Do I...?

### Make a heading?

Use `#` symbols:

```
# Big Heading
## Medium Heading
### Small Heading
```

### Make a list?

Use dashes:

```
- First item
- Second item
- Third item
```

### Make text bold?

Use two stars:

```
**This is bold**
```

### Make text italic?

Use one star:

```
*This is italic*
```

## Can I Add Images?

Yes! Just type:

```
![Description](path/to/your/image.jpg)
```

## How Do I Present?

1. Open your preview (`Cmd+Shift+V` or `Ctrl+Shift+V`)
2. Click in the preview window
3. Use arrow keys or spacebar to advance slides
4. Press `F` for fullscreen
5. Press `P` for presenter mode (shows notes)

## Do I Need Internet?

No! Everything works offline.

## Can I Share My Presentation?

Yes! You can:
1. Share the `.md` file (they need this extension)
2. Export to PDF (print from browser)
3. Send screenshots

## I Want to Learn More

See the USER_GUIDE.md file for complete instructions and advanced features.

## Help! It's Not Working

1. Make sure your file ends in `.md`
2. Make sure you saved the file (`Cmd+S` or `Ctrl+S`)
3. Try closing the preview and opening it again
4. Try closing VS Code and reopening it

## Quick Reference

| I Want To... | I Type... |
|--------------|-----------|
| New slide | `---` |
| Big heading | `# Text` |
| Medium heading | `## Text` |
| Bullet list | `- Item` |
| Bold | `**Text**` |
| Italic | `*Text*` |
| Link | `[Text](URL)` |
| Image | `![Alt](path)` |

## Example

Here's a complete mini-presentation:

```markdown
title: Team Meeting

---

class: center, middle

# Weekly Team Update

March 15, 2024

---

# Last Week's Wins

- Completed project A
- Got 5 new clients
- Fixed the bug!

---

# This Week's Goals

- Start project B
- Plan the launch
- Team building event

---

class: center, middle

# Questions?

---

class: center, middle

# Thank You!
```

Copy and paste this into a `.md` file, press `Cmd+Shift+V`, and see it come to life!

---

**You're ready to create presentations!** Start simple and experiment. You can't break anything - it's just text! 😊
