title: Welcome to Remark.js!
class: animation-fade

---

class: center, middle

# Welcome to Remark.js!

## Creating Beautiful Presentations with Markdown

Press `→` or `Space` to advance

???
These are presenter notes. Press 'P' to see them during your presentation.

---

# What is Remark.js?

Remark.js turns simple markdown text into beautiful slide presentations.

--

**Benefits:**

--

- Write slides in plain text

--

- Focus on content, not formatting

--

- Version control friendly (it's just text!)

--

- Works offline

???
Remind audience that they can use their favorite text editor.

---

# Getting Started

Creating slides is easy. Just separate them with three dashes:

```markdown
---
```

That's it! Each `---` creates a new slide.

---

# Formatting Text

You can use standard markdown formatting:

**Bold text** with `**bold**`

*Italic text* with `*italic*`

`Code` with backticks

> Blockquotes with >

---

# Lists

## Unordered Lists

- First item
- Second item
  - Nested item
  - Another nested item
- Third item

## Ordered Lists

1. First step
2. Second step
3. Third step

---

# Code Highlighting

Remark.js has built-in syntax highlighting:

```javascript
function greet(name) {
  console.log(`Hello, ${name}!`);
  return `Welcome to Remark.js`;
}

greet('World');
```

```python
def greet(name):
    print(f"Hello, {name}!")
    return "Welcome to Remark.js"

greet("World")
```

---

# Two Column Layout

.col-6[
### Left Column

- Point one
- Point two
- Point three

Perfect for comparisons!
]

.col-6[
### Right Column

- Different point
- Another point
- Yet another

Side by side content is easy!
]

---

# Incremental Reveals

Start with this content visible...

--

Then reveal this when you click...

--

Then this appears...

--

And finally this!

--

Great for building suspense or explaining step-by-step!

???
Use incremental reveals to control the pace of your presentation.

---

class: center, middle

# Special Slide Styles

You can add classes to slides for different effects

---

class: center

# Centered Content

This slide is horizontally centered

Perfect for title slides or important announcements

---

class: middle

# Vertically Centered

This content is vertically centered

Great for quotes or single points

---

class: inverse

# Dark Background

This slide has a dark background (inverse class)

Perfect for dramatic effect or visual breaks

---

# Presenter Notes

Every slide can have hidden notes that only you see.

Press `P` during your presentation to enter **Presenter Mode**.

You'll see:
- Current slide
- Next slide
- Your private notes
- A timer

???
This is a presenter note! It won't show on the main slide.

Remember to:
- Make eye contact
- Speak clearly
- Engage the audience

---

# Keyboard Shortcuts

| Action | Key |
|--------|-----|
| Next slide | `→`, `Space`, `Page Down` |
| Previous slide | `←`, `Page Up` |
| First slide | `Home` |
| Last slide | `End` |
| Presenter mode | `P` |
| Clone window | `C` |
| Help | `H` or `?` |

---

# Links and Images

You can include links:

[Visit the Remark.js Wiki](https://github.com/gnab/remark/wiki)

And images:

```markdown
![Alt text](path/to/image.jpg)
```

Images can be local files or URLs!

---

# Advanced: Custom CSS Classes

You can create custom styles:

.red[This text is red]

.large[This text is large]

.center[This text is centered]

Define these in your CSS:

```css
.red { color: red; }
.large { font-size: 2em; }
.center { text-align: center; }
```

---

# Tips for Great Presentations

1. **One idea per slide** - Keep it focused

2. **Use big fonts** - Make it readable

3. **Images over text** - Show, don't tell

4. **Practice** - Use presenter mode

5. **Engage** - Ask questions, tell stories

6. **Time it** - Don't rush or drag

---

# Exporting Your Presentation

Want to share your presentation?

**Options:**

1. **Share the markdown file** - Others can view with this extension

2. **Export to PDF** - Press `P` for presenter mode, then print to PDF

3. **Share live** - Press `C` to clone window, then share your screen

4. **Host online** - Export as HTML and host on a website

---

class: center, middle

# Ready to Create?

## Just three steps:

1. Create a `.md` file
2. Write some markdown
3. Press `Cmd+Shift+V` (Mac) or `Ctrl+Shift+V` (Windows)

---

class: center, middle

# Questions?

Press `H` for help

Press `?` to see all keyboard shortcuts

---

class: center, middle, inverse

# Thank You!

## Now go create something amazing!

Press `Home` to return to the first slide

???
Remember to share your presentations with others!

Happy presenting!
