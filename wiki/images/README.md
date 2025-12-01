# LensIQ Wiki Images

This directory contains all screenshots and images used in the LensIQ wiki documentation.

## Image Inventory

### Required Screenshots

Below is a complete list of screenshots needed for the wiki. Check off items as they are added.

#### Branding
- [ ] `lensiq-logo.png` - LensIQ platform logo

#### 1. Storytelling (LensIQ)
- [ ] `lensiq-storytelling-dashboard.png` - Main storytelling dashboard
- [ ] `storytelling-main.png` - Storytelling interface
- [ ] `storytelling-insights.png` - AI insights panel
- [ ] `storytelling-narratives.png` - Narrative builder

#### 2. Strategy Hub
- [ ] `strategy-hub-dashboard.png` - Strategy Hub main page
- [ ] `strategy-porters.png` - Porter's Five Forces analysis
- [ ] `strategy-swot.png` - SWOT analysis interface
- [ ] `strategy-bcg.png` - BCG Matrix visualization
- [ ] `strategy-mckinsey.png` - McKinsey 9-Box Matrix
- [ ] `strategy-pyramid.png` - Strategy Pyramid
- [ ] `strategy-frameworks.png` - Framework selection page
- [ ] `strategy-execution.png` - Strategy execution dashboard

#### 3. Trends (TrendRadar)
- [ ] `trendradar-dashboard.png` - TrendRadar main dashboard
- [ ] `trendradar-main.png` - Interactive trend radar
- [ ] `trendradar-details.png` - Trend details panel
- [ ] `trendradar-ml.png` - ML insights visualization

#### 4. VC Lens
- [ ] `vc-lens-dashboard.png` - VC Lens main dashboard
- [ ] `vc-lens-portfolio.png` - Portfolio overview
- [ ] `vc-lens-company.png` - Company analysis view
- [ ] `vc-lens-esg.png` - ESG scorecard

#### 5. Graph Analytics
- [ ] `graph-analytics-dashboard.png` - Graph Analytics main page
- [ ] `graph-impact.png` - Impact graph visualization
- [ ] `graph-network.png` - Network graph
- [ ] `graph-supply-chain.png` - Supply chain graph
- [ ] `graph-venture-signal.png` - Venture signal graph

#### 6. Data Management
- [ ] `data-management-dashboard.png` - Data Management dashboard
- [ ] `data-management-upload.png` - Data upload interface
- [ ] `data-management-collections.png` - Collection browser
- [ ] `data-management-quality.png` - Data quality dashboard

#### 7. Lookthrough
- [ ] `lookthrough-dashboard.png` - Lookthrough main dashboard
- [ ] `lookthrough-fund.png` - Fund view
- [ ] `lookthrough-company.png` - Company view
- [ ] `lookthrough-project.png` - Project view

#### 8. Lifecycle Management
- [ ] `lifecycle-dashboard.png` - Lifecycle dashboard
- [ ] `lifecycle-timeline.png` - Lifecycle timeline
- [ ] `lifecycle-stages.png` - Stage details view

#### 9. AI Copilot
- [ ] `copilot-interface.png` - Copilot main interface
- [ ] `copilot-chat.png` - Chat interface
- [ ] `copilot-insights.png` - AI insights panel

## Image Specifications

### Technical Requirements
- **Format:** PNG (preferred) or JPG
- **Resolution:** Minimum 1920x1080
- **File Size:** Maximum 500KB
- **Color:** 24-bit RGB
- **Compression:** Optimized with pngquant or similar

### Naming Convention
- Use lowercase letters
- Use hyphens for spaces
- Be descriptive
- Format: `[module]-[component]-[detail].png`

### Examples
```
✅ Good:
- strategy-hub-dashboard.png
- trendradar-ml-insights.png
- vc-lens-portfolio-overview.png

❌ Bad:
- Screenshot1.png
- IMG_2024.png
- dashboard.png
```

## Adding New Images

1. **Capture Screenshot**
   - Follow [Screenshot-Guide.md](../Screenshot-Guide.md)
   - Ensure high resolution (1920x1080+)
   - Use clean, professional UI

2. **Edit and Optimize**
   - Crop to relevant area
   - Redact sensitive information
   - Compress to <500KB
   - Save as PNG

3. **Add to Directory**
   - Place file in this directory
   - Use descriptive filename
   - Update this README checklist

4. **Reference in Wiki**
   - Add to appropriate wiki page
   - Use descriptive alt text
   - Add caption if needed

## Image Guidelines

### Content
- ✅ Show realistic, professional data
- ✅ Ensure UI is clean and error-free
- ✅ Include enough context
- ✅ Highlight key features
- ❌ No sensitive or confidential data
- ❌ No debug messages or errors
- ❌ No personal information

### Quality
- ✅ High resolution (1920x1080+)
- ✅ Properly cropped
- ✅ Optimized file size
- ✅ Clear and readable
- ❌ Blurry or pixelated
- ❌ Too large (>500KB)
- ❌ Poor contrast

### Consistency
- ✅ Same browser and theme
- ✅ Consistent styling
- ✅ Similar data format
- ✅ Matching color scheme
- ❌ Mixed browsers
- ❌ Different themes
- ❌ Inconsistent UI

## Placeholder Images

Until actual screenshots are captured, you can use placeholder images:

```markdown
![Placeholder](https://via.placeholder.com/1920x1080/3B82F6/FFFFFF?text=LensIQ+Dashboard)
```

Or create simple placeholder files:

```bash
# Create placeholder with ImageMagick
convert -size 1920x1080 xc:#3B82F6 \
  -pointsize 72 -fill white -gravity center \
  -annotate +0+0 "LensIQ Dashboard" \
  placeholder-dashboard.png
```

## Image Optimization

### Batch Optimization

```bash
# Optimize all PNGs in this directory
cd wiki/images
for file in *.png; do
    pngquant --quality=65-80 "$file" --ext .png --force
done

# Or use ImageOptim (macOS)
open -a ImageOptim *.png
```

### Individual Optimization

```bash
# PNG
pngquant --quality=65-80 input.png -o output.png

# JPG
jpegoptim --max=85 input.jpg
```

## File Organization

```
wiki/images/
├── README.md                           # This file
├── lensiq-logo.png                     # Branding
├── [module]-[component].png            # Feature screenshots
└── [module]-[component]-[detail].png   # Detailed views
```

## Maintenance

### Regular Tasks
- [ ] Review screenshots monthly
- [ ] Update outdated screenshots
- [ ] Remove unused images
- [ ] Optimize new additions
- [ ] Verify all links work

### When UI Changes
- [ ] Identify affected screenshots
- [ ] Recapture updated views
- [ ] Replace old images
- [ ] Update wiki references
- [ ] Archive old versions

## Tools

### Recommended Tools
- **Capture:** Snagit, Greenshot, or built-in OS tools
- **Edit:** GIMP, Photopea, or Paint.NET
- **Optimize:** TinyPNG, ImageOptim, or pngquant
- **Batch:** ImageMagick or custom scripts

### Quick Commands

```bash
# Check image dimensions
identify *.png

# Check file sizes
ls -lh *.png

# Find large files (>500KB)
find . -name "*.png" -size +500k

# Resize to max width 1920px
mogrify -resize 1920x\> *.png
```

## Support

For questions about images:

- 📖 See [Screenshot-Guide.md](../Screenshot-Guide.md)
- 💬 Slack: #documentation channel
- 📧 Email: docs@lensiq.com

---

*Last Updated: November 14, 2025*

