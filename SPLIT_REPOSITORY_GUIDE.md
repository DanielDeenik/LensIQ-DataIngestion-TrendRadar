# Guide: Split LensIQ Data Ingestion & TrendRadar into Dedicated Repository

This guide will help you split the `LensIQ_DataIngestion_TrendRadar` branch into a standalone GitHub repository.

---

## 📋 Overview

**Current State:**
- Branch: `LensIQ_DataIngestion_TrendRadar` in `TrendSense` repository
- URL: https://github.com/DanielDeenik/TrendSense/tree/LensIQ_DataIngestion_TrendRadar

**Target State:**
- New Repository: `LensIQ-DataIngestion-TrendRadar`
- URL: https://github.com/DanielDeenik/LensIQ-DataIngestion-TrendRadar
- Independent repository with full history

---

## 🎯 Method 1: Create New Repository and Push Branch (Recommended)

This method creates a clean new repository with only the branch content.

### Step 1: Create New Repository on GitHub

1. Go to https://github.com/new
2. Fill in the details:
   - **Repository name:** `LensIQ-DataIngestion-TrendRadar`
   - **Description:** `AI-Powered Data Ingestion and Trend Analysis Platform - Multi-source data ingestion (Reddit, Discord, LinkedIn, SQL, MongoDB) with ML/AI-powered TrendRadar`
   - **Visibility:** Public (or Private if preferred)
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
3. Click "Create repository"

### Step 2: Push Current Branch to New Repository

```bash
# Navigate to your current repository
cd /Users/danieldeenik/Documents/GitHub/TrendSense

# Ensure you're on the correct branch
git checkout LensIQ_DataIngestion_TrendRadar

# Add the new repository as a remote
git remote add lensiq-repo https://github.com/DanielDeenik/LensIQ-DataIngestion-TrendRadar.git

# Push the branch to the new repository as 'main'
git push lensiq-repo LensIQ_DataIngestion_TrendRadar:main

# Verify the push
git ls-remote lensiq-repo
```

### Step 3: Clone the New Repository Locally

```bash
# Navigate to your GitHub directory
cd /Users/danieldeenik/Documents/GitHub

# Clone the new repository
git clone https://github.com/DanielDeenik/LensIQ-DataIngestion-TrendRadar.git

# Navigate into the new repository
cd LensIQ-DataIngestion-TrendRadar

# Verify the content
ls -la
git log --oneline -5
```

### Step 4: Set Up the New Repository

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Test the application
./start_lensiq.sh
```

---

## 🎯 Method 2: Use GitHub CLI (Fastest)

If you have GitHub CLI installed, this is the fastest method.

### Step 1: Install GitHub CLI (if not installed)

```bash
brew install gh
gh auth login
```

### Step 2: Create Repository and Push

```bash
# Navigate to your current repository
cd /Users/danieldeenik/Documents/GitHub/TrendSense

# Ensure you're on the correct branch
git checkout LensIQ_DataIngestion_TrendRadar

# Create new repository using GitHub CLI
gh repo create LensIQ-DataIngestion-TrendRadar \
  --public \
  --description "AI-Powered Data Ingestion and Trend Analysis Platform" \
  --source=. \
  --remote=lensiq-repo

# Push the branch
git push lensiq-repo LensIQ_DataIngestion_TrendRadar:main

# Clone to a new directory
cd /Users/danieldeenik/Documents/GitHub
gh repo clone DanielDeenik/LensIQ-DataIngestion-TrendRadar
```

---

## 🎯 Method 3: Filter Branch History (Advanced)

This method creates a new repository with only the files and history from this branch.

### Step 1: Create a Clean Clone

```bash
# Create a new directory for the filtered repository
cd /Users/danieldeenik/Documents/GitHub
git clone --branch LensIQ_DataIngestion_TrendRadar --single-branch \
  https://github.com/DanielDeenik/TrendSense.git \
  LensIQ-DataIngestion-TrendRadar

cd LensIQ-DataIngestion-TrendRadar
```

### Step 2: Remove Old Remote and Create New Repository

```bash
# Remove the old remote
git remote remove origin

# Create new repository on GitHub (via web or CLI)
# Then add it as the new remote
git remote add origin https://github.com/DanielDeenik/LensIQ-DataIngestion-TrendRadar.git

# Rename branch to main
git branch -M main

# Push to new repository
git push -u origin main
```

---

## 📝 Post-Setup Tasks

After creating the new repository, complete these tasks:

### 1. Update Repository Settings

On GitHub (https://github.com/DanielDeenik/LensIQ-DataIngestion-TrendRadar/settings):

- [ ] Add repository description
- [ ] Add topics: `data-ingestion`, `machine-learning`, `ai`, `trend-analysis`, `python`, `flask`, `mongodb`, `reddit`, `discord`
- [ ] Enable Issues
- [ ] Enable Discussions (optional)
- [ ] Set up branch protection for `main`

### 2. Create GitHub Project Board

```bash
# Link to existing project or create new one
# Existing: https://github.com/users/DanielDeenik/projects/4
```

### 3. Add Repository Badges

Add to README.md:

```markdown
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Flask 3.0.3](https://img.shields.io/badge/flask-3.0.3-green.svg)](https://flask.palletsprojects.com/)
[![MongoDB](https://img.shields.io/badge/mongodb-8.0+-green.svg)](https://www.mongodb.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
```

### 4. Set Up GitHub Actions (Optional)

Create `.github/workflows/ci.yml` for automated testing:

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        run: pytest tests/
```

### 5. Update Documentation Links

Update all documentation to reference the new repository:
- [ ] README.md
- [ ] docs/DataIngestion_TrendRadar_Branch.md
- [ ] README_DataIngestion_TrendRadar.md

### 6. Create Initial Release

```bash
# Tag the initial release
git tag -a v0.1.0 -m "Initial release - Phase 1 complete"
git push origin v0.1.0

# Create release on GitHub
gh release create v0.1.0 \
  --title "v0.1.0 - Initial Release" \
  --notes "Phase 1 complete: Reddit & Discord connectors, MongoDB integration, TrendRadar UI"
```

---

## 🔗 Update Original Repository

After creating the new repository, update the original `TrendSense` repository:

### Option A: Keep the Branch (Recommended)

Keep the branch in the original repository for reference:

```bash
cd /Users/danieldeenik/Documents/GitHub/TrendSense
git checkout master

# Add a note in the main README
echo "
## Related Projects

- **LensIQ Data Ingestion & TrendRadar:** https://github.com/DanielDeenik/LensIQ-DataIngestion-TrendRadar
  - Focused implementation for multi-source data ingestion and ML/AI-powered trend analysis
" >> README.md

git add README.md
git commit -m "Add link to LensIQ Data Ingestion & TrendRadar repository"
git push origin master
```

### Option B: Archive the Branch

If you want to remove the branch from the original repository:

```bash
cd /Users/danieldeenik/Documents/GitHub/TrendSense

# Delete the branch locally
git branch -D LensIQ_DataIngestion_TrendRadar

# Delete the branch remotely
git push origin --delete LensIQ_DataIngestion_TrendRadar
```

---

## ✅ Verification Checklist

After completing the split, verify:

- [ ] New repository created: https://github.com/DanielDeenik/LensIQ-DataIngestion-TrendRadar
- [ ] All files present in new repository
- [ ] README.md displays correctly
- [ ] .env.example is present
- [ ] start_lensiq.sh is executable
- [ ] Virtual environment can be created
- [ ] Dependencies install successfully
- [ ] Application launches without errors
- [ ] Repository settings configured
- [ ] Topics/tags added
- [ ] Documentation links updated
- [ ] Original repository updated (if keeping branch)

---

## 🎉 Success!

Your LensIQ Data Ingestion & TrendRadar is now a standalone repository!

**New Repository:** https://github.com/DanielDeenik/LensIQ-DataIngestion-TrendRadar

**Next Steps:**
1. Share the repository with collaborators
2. Continue development on Phase 2 (LinkedIn & SQL connectors)
3. Set up CI/CD pipelines
4. Create issues for planned features
5. Start building the ML/AI components

---

## 📧 Questions?

If you encounter any issues during the split, refer to:
- GitHub Docs: https://docs.github.com/en/repositories
- Git Documentation: https://git-scm.com/doc
- This guide: `SPLIT_REPOSITORY_GUIDE.md`

---

**Created:** 2025-12-02  
**Author:** LensIQ Development Team  
**Repository:** https://github.com/DanielDeenik/LensIQ-DataIngestion-TrendRadar

