# GitHub Projects Quick Start Guide

## 🚀 5-Minute Setup

### Step 1: Create the Project (2 minutes)

1. Go to: `https://github.com/danieldeenik/TrendSense`
2. Click **Projects** tab → **New project**
3. Select **Board** template
4. Name: `LensIQ Feature Development`
5. Click **Create project**

### Step 2: Add Columns (1 minute)

Add these columns in order:
1. 📋 Backlog
2. 🎯 Prioritized
3. 🔨 In Development
4. 🧪 Testing
5. ✅ Done
6. 🚫 Won't Do

### Step 3: Create Custom Fields (2 minutes)

Click **+ New field** and add:

**Priority** (Single select):
- 🔴 Critical
- 🟠 High
- 🟡 Medium
- 🟢 Low

**Module** (Single select):
- TrendRadar, Storytelling, Strategy Hub, VC Lens, Graph Analytics, Data Management, Lookthrough, Lifecycle, AI Copilot, Platform

**Effort** (Single select):
- XS (1-2 days), S (3-5 days), M (1-2 weeks), L (2-4 weeks), XL (1+ months)

---

## 📝 Creating Your First Feature

### Option 1: From GitHub Issues

1. Go to **Issues** → **New issue**
2. Choose **Feature Request** template
3. Fill in the details:
   - Title: `[FEATURE] Export reports to PDF`
   - Module: Check `Platform/Infrastructure`
   - Priority: Check `High`
   - Effort: Check `M (1-2 weeks)`
4. Click **Submit new issue**
5. Issue automatically appears in your project!

### Option 2: Directly in Project Board

1. Open your project board
2. Click **+ Add item** in Backlog column
3. Type feature name and press Enter
4. Click the item to add details
5. Fill in custom fields (Priority, Module, Effort)

---

## 🏷️ Labels to Create

Go to **Issues** → **Labels** → **New label**

Create these labels:

**Priority Labels:**
- `priority:critical` - Red (#d73a4a)
- `priority:high` - Orange (#ff9900)
- `priority:medium` - Yellow (#fbca04)
- `priority:low` - Green (#0e8a16)

**Module Labels:**
- `module:trendradar` - Blue (#0075ca)
- `module:storytelling` - Blue (#0075ca)
- `module:strategy` - Blue (#0075ca)
- `module:vc-lens` - Blue (#0075ca)
- `module:graph` - Blue (#0075ca)
- `module:data` - Blue (#0075ca)
- `module:lookthrough` - Blue (#0075ca)
- `module:lifecycle` - Blue (#0075ca)
- `module:copilot` - Blue (#0075ca)
- `module:platform` - Purple (#5319e7)

**Type Labels:**
- `enhancement` - Green (#a2eeef)
- `bug` - Red (#d73a4a)
- `documentation` - Blue (#0075ca)
- `technical-debt` - Gray (#d4c5f9)

---

## 📊 Sample Features to Add

Copy these into your backlog:

### High Priority

**1. Export & Reporting**
```
Title: [FEATURE] Export reports to PDF/PowerPoint/Excel
Module: Platform
Priority: High
Effort: M
Description: Allow users to export dashboards and reports to multiple formats
```

**2. Real-time Alerts**
```
Title: [FEATURE] Email alerts for ESG trend changes
Module: TrendRadar
Priority: High
Effort: M
Description: Send notifications when significant trends are detected
```

**3. Performance Optimization**
```
Title: [ENHANCEMENT] Optimize database queries and add caching
Module: Platform
Priority: High
Effort: M
Description: Implement Redis caching and optimize MongoDB queries
```

### Medium Priority

**4. Custom Dashboards**
```
Title: [FEATURE] Drag-and-drop dashboard builder
Module: Platform
Priority: Medium
Effort: L
Description: Allow users to create custom dashboards with widgets
```

**5. Advanced Graphs**
```
Title: [ENHANCEMENT] Interactive 3D network visualizations
Module: Graph Analytics
Priority: Medium
Effort: M
Description: Add force-directed layouts and 3D graph views
```

---

## 🔄 Workflow

### Moving Cards

**Backlog → Prioritized**
- Feature is approved and ready for development
- Assign to milestone/release

**Prioritized → In Development**
- Developer starts working on it
- Assign to developer
- Create feature branch

**In Development → Testing**
- Code complete, PR created
- Ready for QA/testing

**Testing → Done**
- Tests pass, PR merged
- Feature deployed

**Any → Won't Do**
- Feature rejected or deprioritized
- Add comment explaining why

---

## 🎯 Best Practices

### Daily
- [ ] Update card status as you work
- [ ] Move cards between columns
- [ ] Add comments on progress

### Weekly
- [ ] Review Backlog, prioritize top 5
- [ ] Limit "In Development" to 3-5 items
- [ ] Close completed items
- [ ] Update effort estimates

### Monthly
- [ ] Review and groom backlog
- [ ] Archive old "Won't Do" items
- [ ] Plan next milestone
- [ ] Update documentation

---

## 🔗 Quick Links

- **Project Board:** `https://github.com/users/danieldeenik/projects/1`
- **Issues:** `https://github.com/danieldeenik/TrendSense/issues`
- **New Feature:** `https://github.com/danieldeenik/TrendSense/issues/new?template=feature_request.md`
- **New Bug:** `https://github.com/danieldeenik/TrendSense/issues/new?template=bug_report.md`

---

## 📱 GitHub Mobile

Download GitHub Mobile app to:
- Review and update cards on the go
- Get notifications for new issues
- Comment and collaborate anywhere

---

## 🆘 Common Tasks

### Add a new feature
1. Click **Issues** → **New issue**
2. Choose **Feature Request**
3. Fill template and submit

### Prioritize a feature
1. Open the issue
2. Add `priority:high` label
3. Move to **Prioritized** column

### Start working on a feature
1. Assign yourself to the issue
2. Move to **In Development**
3. Create feature branch: `git checkout -b feature/issue-123`

### Complete a feature
1. Create PR with "Closes #123" in description
2. Move to **Testing**
3. After merge, auto-moves to **Done**

### Reject a feature
1. Add comment explaining why
2. Add `wontfix` label
3. Move to **Won't Do**
4. Close issue

---

## 🎓 Resources

- [GitHub Projects Docs](https://docs.github.com/en/issues/planning-and-tracking-with-projects)
- [Issue Templates Guide](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests)
- [GitHub Actions](https://docs.github.com/en/actions)

---

*Last Updated: December 1, 2025*

