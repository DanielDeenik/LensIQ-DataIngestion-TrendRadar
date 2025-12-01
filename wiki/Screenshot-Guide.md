# Screenshot Guide for LensIQ Wiki

This guide provides detailed instructions for capturing, editing, and adding screenshots to the LensIQ wiki.

## Table of Contents
- [Screenshot Requirements](#screenshot-requirements)
- [Capturing Screenshots](#capturing-screenshots)
- [Editing Screenshots](#editing-screenshots)
- [Optimizing Images](#optimizing-images)
- [Adding to Wiki](#adding-to-wiki)
- [Screenshot Checklist](#screenshot-checklist)
- [Tools and Resources](#tools-and-resources)

---

## Screenshot Requirements

### Technical Requirements
- **Resolution:** Minimum 1920x1080 (Full HD)
- **Format:** PNG for UI screenshots, JPG for photos
- **File Size:** Maximum 500KB per image
- **Color Depth:** 24-bit color (16.7 million colors)
- **Aspect Ratio:** 16:9 preferred

### Content Requirements
- **Clean UI:** No debug messages, errors, or console output
- **Professional:** Use realistic, professional data
- **Privacy:** No sensitive or confidential information
- **Consistency:** Use the same theme/styling across screenshots
- **Context:** Show enough context to understand the feature

---

## Capturing Screenshots

### Preparation

1. **Set Up Environment**
   ```bash
   # Start the application
   python app.py
   
   # Navigate to http://localhost:5000
   ```

2. **Configure Browser**
   - Use Chrome or Firefox for consistency
   - Set browser zoom to 100%
   - Use full-screen mode (F11)
   - Clear browser cache and cookies
   - Disable browser extensions that modify UI

3. **Prepare Data**
   - Load sample data if needed
   - Ensure data is realistic and professional
   - Remove any test or dummy data
   - Verify all UI elements are visible

### Capture Methods

#### macOS
```bash
# Full screen
Cmd + Shift + 3

# Selected area
Cmd + Shift + 4

# Specific window
Cmd + Shift + 4, then Space, then click window
```

#### Windows
```bash
# Full screen
PrtScn or Windows + PrtScn

# Active window
Alt + PrtScn

# Snipping Tool
Windows + Shift + S
```

#### Linux
```bash
# Full screen
PrtScn

# Selected area
Shift + PrtScn

# Use GNOME Screenshot or similar tool
```

### Browser Developer Tools

For precise screenshots:

1. Open Developer Tools (F12)
2. Toggle device toolbar (Cmd/Ctrl + Shift + M)
3. Set device to "Responsive"
4. Set dimensions to 1920x1080
5. Capture screenshot using browser's built-in tool

---

## Editing Screenshots

### Required Edits

1. **Crop to Content**
   - Remove unnecessary browser chrome
   - Focus on the relevant UI area
   - Maintain aspect ratio

2. **Annotate (if needed)**
   - Add arrows to highlight features
   - Add text boxes for explanations
   - Use consistent colors (LensIQ brand colors)
   - Keep annotations minimal and clear

3. **Redact Sensitive Data**
   - Blur or remove personal information
   - Replace real company names with examples
   - Remove API keys, tokens, or credentials
   - Anonymize user data

### Editing Tools

#### Free Tools
- **GIMP** (Windows, macOS, Linux) - Full-featured image editor
- **Paint.NET** (Windows) - Simple and effective
- **Preview** (macOS) - Built-in, basic editing
- **Krita** (All platforms) - Professional-grade

#### Online Tools
- **Photopea** (photopea.com) - Photoshop-like, browser-based
- **Pixlr** (pixlr.com) - Quick edits
- **Canva** (canva.com) - Design and annotation

#### Professional Tools
- **Adobe Photoshop** - Industry standard
- **Sketch** (macOS) - UI/UX focused
- **Figma** - Collaborative design tool

### Annotation Guidelines

**Colors to Use:**
- Primary: `#3B82F6` (Blue)
- Secondary: `#10B981` (Green)
- Accent: `#F59E0B` (Orange)
- Text: `#1F2937` (Dark Gray)

**Annotation Style:**
- Arrow thickness: 3-4px
- Text size: 14-16px
- Font: Inter, Roboto, or system default
- Background: Semi-transparent white (80% opacity)

---

## Optimizing Images

### Compression

1. **PNG Compression**
   ```bash
   # Using pngquant (recommended)
   pngquant --quality=65-80 input.png -o output.png
   
   # Using ImageOptim (macOS)
   # Drag and drop images into ImageOptim
   
   # Using TinyPNG (online)
   # Upload to tinypng.com
   ```

2. **JPG Compression**
   ```bash
   # Using ImageMagick
   convert input.jpg -quality 85 output.jpg
   
   # Using jpegoptim
   jpegoptim --max=85 input.jpg
   ```

### Resize if Needed

```bash
# Using ImageMagick
convert input.png -resize 1920x1080 output.png

# Maintain aspect ratio
convert input.png -resize 1920x1080\> output.png
```

### Batch Processing

```bash
# Optimize all PNGs in directory
for file in *.png; do
    pngquant --quality=65-80 "$file" -o "optimized/$file"
done

# Resize all images to max width 1920px
for file in *.png; do
    convert "$file" -resize 1920x\> "resized/$file"
done
```

---

## Adding to Wiki

### File Naming Convention

Use descriptive, lowercase names with hyphens:

```
✅ Good:
- lensiq-storytelling-dashboard.png
- strategy-hub-swot-analysis.png
- trendradar-ml-insights.png

❌ Bad:
- Screenshot1.png
- IMG_2024.png
- dashboard.png
```

### Directory Structure

```
wiki/
└── images/
    ├── lensiq-logo.png
    ├── [feature]-[component]-[detail].png
    └── ...
```

### Adding to Markdown

```markdown
# Basic image
![Alt Text](images/filename.png)

# Image with caption
![Dashboard Overview](images/dashboard.png)
*The main dashboard showing key metrics*

# Image with link
[![Click to enlarge](images/thumbnail.png)](images/full-size.png)
```

### Alt Text Guidelines

Write descriptive alt text for accessibility:

```markdown
✅ Good:
![LensIQ storytelling dashboard showing three AI-generated stories with metrics](images/storytelling-dashboard.png)

❌ Bad:
![Dashboard](images/storytelling-dashboard.png)
```

---

## Screenshot Checklist

### Before Capturing

- [ ] Application is running without errors
- [ ] Browser is at 100% zoom
- [ ] Sample data is loaded and realistic
- [ ] UI is clean and professional
- [ ] No sensitive data is visible
- [ ] All UI elements are properly rendered

### After Capturing

- [ ] Screenshot is high resolution (1920x1080+)
- [ ] Image is cropped appropriately
- [ ] Sensitive data is redacted
- [ ] Annotations are clear and minimal
- [ ] Image is optimized (<500KB)
- [ ] Filename is descriptive and lowercase
- [ ] File is saved in `wiki/images/` directory

### Adding to Wiki

- [ ] Image is referenced in markdown
- [ ] Alt text is descriptive
- [ ] Caption is added if needed
- [ ] Image displays correctly in preview
- [ ] Links are working
- [ ] Page is updated in table of contents

---

## Tools and Resources

### Screenshot Tools

| Tool | Platform | Type | Cost |
|------|----------|------|------|
| Snagit | All | Professional | Paid |
| Greenshot | Windows | Screenshot | Free |
| Lightshot | All | Screenshot | Free |
| Monosnap | All | Screenshot | Free |
| ShareX | Windows | Screenshot | Free |
| Skitch | macOS | Annotation | Free |

### Image Optimization

| Tool | Platform | Purpose | Cost |
|------|----------|---------|------|
| TinyPNG | Web | PNG compression | Free |
| ImageOptim | macOS | Optimization | Free |
| Squoosh | Web | Compression | Free |
| pngquant | CLI | PNG compression | Free |
| jpegoptim | CLI | JPG compression | Free |

### Image Editing

| Tool | Platform | Level | Cost |
|------|----------|-------|------|
| GIMP | All | Advanced | Free |
| Photopea | Web | Advanced | Free |
| Paint.NET | Windows | Basic | Free |
| Pixlr | Web | Basic | Free |
| Photoshop | All | Professional | Paid |

---

## Screenshot Templates

### Dashboard Screenshot
- Show full dashboard with navigation
- Include key metrics and visualizations
- Capture at 1920x1080
- Ensure all data is visible

### Detail View Screenshot
- Focus on specific feature or component
- Crop to relevant area
- Show enough context
- Highlight key elements if needed

### Workflow Screenshot
- Capture multiple steps if needed
- Number steps clearly
- Show progression
- Keep consistent styling

### Mobile Screenshot
- Use device emulation (375x667 for iPhone)
- Show responsive design
- Capture both portrait and landscape
- Test on actual devices if possible

---

## Best Practices

### Do's ✅
- Use consistent browser and theme
- Capture at high resolution
- Optimize file sizes
- Use descriptive filenames
- Add helpful alt text
- Keep UI clean and professional
- Show realistic data
- Update screenshots when UI changes

### Don'ts ❌
- Don't include sensitive data
- Don't use low-resolution images
- Don't leave debug messages visible
- Don't use generic filenames
- Don't skip optimization
- Don't forget alt text
- Don't use outdated screenshots
- Don't include browser chrome unless necessary

---

## Examples

### Good Screenshot Example

```markdown
![LensIQ Strategy Hub showing Porter's Five Forces analysis with interactive radar chart and detailed metrics for each force](images/strategy-porters-analysis.png)
*Porter's Five Forces analysis interface with real-time data visualization*
```

**Why it's good:**
- Descriptive filename
- Detailed alt text
- Helpful caption
- Shows feature clearly
- Professional appearance

### Screenshot Workflow

1. **Prepare** → Set up environment and data
2. **Capture** → Take high-resolution screenshot
3. **Edit** → Crop, annotate, redact as needed
4. **Optimize** → Compress to <500KB
5. **Name** → Use descriptive filename
6. **Add** → Place in wiki/images/
7. **Reference** → Add to markdown with alt text
8. **Verify** → Check display and links

---

## Support

For questions about screenshots:

- 📧 Email: docs@lensiq.com
- 💬 Slack: #documentation channel
- 📖 Wiki: [Home](Home.md)

---

*Last Updated: November 14, 2025*

