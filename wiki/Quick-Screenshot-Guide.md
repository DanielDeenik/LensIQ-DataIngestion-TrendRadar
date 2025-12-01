# Quick Screenshot Guide

A fast reference for capturing screenshots for the LensIQ wiki.

## Quick Start (5 Steps)

1. **Start Application** → `python app.py`
2. **Navigate to Feature** → Open the page you want to capture
3. **Capture Screenshot** → Use keyboard shortcut
4. **Optimize Image** → Compress to <500KB
5. **Add to Wiki** → Save in `wiki/images/` and reference in markdown

---

## Keyboard Shortcuts

### macOS
```
Full Screen:     Cmd + Shift + 3
Selected Area:   Cmd + Shift + 4
Window:          Cmd + Shift + 4, then Space, then click
```

### Windows
```
Full Screen:     Windows + PrtScn
Selected Area:   Windows + Shift + S
Active Window:   Alt + PrtScn
```

### Linux
```
Full Screen:     PrtScn
Selected Area:   Shift + PrtScn
```

---

## Screenshot Checklist

### Before Capture
- [ ] App running at http://localhost:5000
- [ ] Browser zoom at 100%
- [ ] Sample data loaded
- [ ] No errors visible
- [ ] UI is clean

### After Capture
- [ ] Resolution ≥ 1920x1080
- [ ] File size < 500KB
- [ ] Saved as PNG
- [ ] Descriptive filename
- [ ] In `wiki/images/` directory

---

## File Naming

**Format:** `[module]-[component]-[detail].png`

**Examples:**
```
✅ strategy-hub-dashboard.png
✅ trendradar-ml-insights.png
✅ vc-lens-portfolio.png

❌ screenshot1.png
❌ IMG_2024.png
❌ dashboard.png
```

---

## Quick Optimization

### Using TinyPNG (Online)
1. Go to https://tinypng.com
2. Upload your PNG
3. Download optimized version

### Using Command Line
```bash
# PNG
pngquant --quality=65-80 input.png -o output.png

# JPG
jpegoptim --max=85 input.jpg
```

---

## Adding to Wiki

### Markdown Syntax
```markdown
![Descriptive alt text](images/filename.png)
*Optional caption explaining the screenshot*
```

### Example
```markdown
![LensIQ Strategy Hub dashboard showing five strategic frameworks](images/strategy-hub-dashboard.png)
*The Strategy Hub main page with framework selection*
```

---

## Common Issues

### Image Too Large
```bash
# Compress PNG
pngquant --quality=65-80 large-image.png -o optimized.png

# Resize if needed
convert large-image.png -resize 1920x1080 resized.png
```

### Wrong Format
```bash
# Convert JPG to PNG
convert image.jpg image.png

# Convert PNG to JPG
convert image.png -quality 85 image.jpg
```

### Sensitive Data Visible
- Use GIMP or Photoshop to blur/redact
- Or recapture with sample data

---

## Screenshot Locations

### Module URLs

| Module | URL |
|--------|-----|
| Home | http://localhost:5000/ |
| Storytelling | http://localhost:5000/storytelling |
| Strategy | http://localhost:5000/strategy |
| Trends | http://localhost:5000/trends |
| VC Lens | http://localhost:5000/vc-lens |
| Graph Analytics | http://localhost:5000/graph-analytics |
| Data Management | http://localhost:5000/data-management |
| Lookthrough | http://localhost:5000/lookthrough |
| Lifecycle | http://localhost:5000/lifecycle |
| Copilot | http://localhost:5000/copilot |

---

## Priority Screenshots

### High Priority (Capture First)
1. `lensiq-logo.png` - Platform logo
2. `strategy-hub-dashboard.png` - Strategy main page
3. `trendradar-dashboard.png` - TrendRadar main page
4. `vc-lens-dashboard.png` - VC Lens main page
5. `data-management-dashboard.png` - Data Management main page

### Medium Priority
6. `storytelling-main.png` - Storytelling interface
7. `graph-analytics-dashboard.png` - Graph Analytics main
8. `lookthrough-dashboard.png` - Lookthrough main
9. `lifecycle-dashboard.png` - Lifecycle main
10. `copilot-interface.png` - Copilot interface

### Low Priority (Detail Views)
11. Framework-specific screenshots
12. Detail panels and modals
13. API documentation screenshots
14. Settings and configuration screens

---

## Tips for Great Screenshots

### Do's ✅
- Use realistic, professional data
- Capture at high resolution
- Show key features clearly
- Keep UI clean and error-free
- Use consistent browser/theme
- Optimize file sizes

### Don'ts ❌
- Include sensitive data
- Show debug messages
- Use low resolution
- Skip optimization
- Use generic filenames
- Forget alt text

---

## Batch Processing

### Capture Multiple Screenshots
1. Open all pages in separate tabs
2. Capture each page systematically
3. Name files immediately
4. Optimize all at once

### Batch Optimize
```bash
# Navigate to images directory
cd wiki/images

# Optimize all PNGs
for file in *.png; do
    pngquant --quality=65-80 "$file" --ext .png --force
done
```

---

## Tools Quick Reference

### Free Screenshot Tools
- **macOS:** Built-in (Cmd+Shift+4)
- **Windows:** Snipping Tool (Win+Shift+S)
- **Linux:** GNOME Screenshot
- **Cross-platform:** Greenshot, Lightshot

### Free Optimization Tools
- **Online:** TinyPNG, Squoosh
- **macOS:** ImageOptim
- **CLI:** pngquant, jpegoptim
- **Cross-platform:** GIMP

---

## Need Help?

- 📖 Full guide: [Screenshot-Guide.md](Screenshot-Guide.md)
- 📋 Image list: [images/README.md](images/README.md)
- 🏠 Wiki home: [Home.md](Home.md)
- 💬 Slack: #documentation

---

*Last Updated: November 14, 2025*

