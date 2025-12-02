#!/bin/bash

# ============================================
# LensIQ Data Ingestion & TrendRadar
# Repository Split Automation Script
# ============================================

set -e  # Exit on error

echo "🚀 LensIQ Data Ingestion & TrendRadar - Repository Split"
echo "=========================================================="
echo ""

# Configuration
CURRENT_REPO="TrendSense"
CURRENT_BRANCH="LensIQ_DataIngestion_TrendRadar"
NEW_REPO_NAME="LensIQ-DataIngestion-TrendRadar"
NEW_REPO_URL="https://github.com/DanielDeenik/${NEW_REPO_NAME}.git"
GITHUB_USER="DanielDeenik"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# ============================================
# Step 1: Verify Current State
# ============================================

echo "📋 Step 1: Verifying current state..."
echo ""

# Check if we're in the right directory
if [ ! -d ".git" ]; then
    echo -e "${RED}❌ Error: Not in a git repository${NC}"
    exit 1
fi

# Check if we're on the right branch
CURRENT_BRANCH_NAME=$(git branch --show-current)
if [ "$CURRENT_BRANCH_NAME" != "$CURRENT_BRANCH" ]; then
    echo -e "${YELLOW}⚠️  Not on $CURRENT_BRANCH branch. Switching...${NC}"
    git checkout $CURRENT_BRANCH
fi

echo -e "${GREEN}✅ On branch: $CURRENT_BRANCH${NC}"
echo ""

# ============================================
# Step 2: Check for Uncommitted Changes
# ============================================

echo "📋 Step 2: Checking for uncommitted changes..."
echo ""

if ! git diff-index --quiet HEAD --; then
    echo -e "${YELLOW}⚠️  You have uncommitted changes.${NC}"
    echo "Please commit or stash them before continuing."
    echo ""
    git status --short
    echo ""
    read -p "Do you want to continue anyway? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Exiting..."
        exit 1
    fi
else
    echo -e "${GREEN}✅ No uncommitted changes${NC}"
fi
echo ""

# ============================================
# Step 3: Create New Repository on GitHub
# ============================================

echo "📋 Step 3: Creating new repository on GitHub..."
echo ""

# Check if GitHub CLI is installed
if command -v gh &> /dev/null; then
    echo "Using GitHub CLI to create repository..."
    echo ""
    
    # Check if already logged in
    if ! gh auth status &> /dev/null; then
        echo "Please log in to GitHub CLI:"
        gh auth login
    fi
    
    # Create repository
    echo "Creating repository: ${NEW_REPO_NAME}..."
    gh repo create ${NEW_REPO_NAME} \
        --public \
        --description "AI-Powered Data Ingestion and Trend Analysis Platform - Multi-source data ingestion (Reddit, Discord, LinkedIn, SQL, MongoDB) with ML/AI-powered TrendRadar" \
        --confirm || echo "Repository may already exist"
    
    echo -e "${GREEN}✅ Repository created (or already exists)${NC}"
else
    echo -e "${YELLOW}⚠️  GitHub CLI not found${NC}"
    echo ""
    echo "Please create the repository manually:"
    echo "1. Go to: https://github.com/new"
    echo "2. Repository name: ${NEW_REPO_NAME}"
    echo "3. Description: AI-Powered Data Ingestion and Trend Analysis Platform"
    echo "4. Visibility: Public"
    echo "5. DO NOT initialize with README, .gitignore, or license"
    echo "6. Click 'Create repository'"
    echo ""
    read -p "Press Enter when you've created the repository..."
fi
echo ""

# ============================================
# Step 4: Add New Remote
# ============================================

echo "📋 Step 4: Adding new remote..."
echo ""

# Remove remote if it already exists
if git remote | grep -q "lensiq-repo"; then
    echo "Removing existing lensiq-repo remote..."
    git remote remove lensiq-repo
fi

# Add new remote
git remote add lensiq-repo ${NEW_REPO_URL}
echo -e "${GREEN}✅ Remote added: lensiq-repo${NC}"
echo ""

# ============================================
# Step 5: Push Branch to New Repository
# ============================================

echo "📋 Step 5: Pushing branch to new repository..."
echo ""

echo "Pushing ${CURRENT_BRANCH} to lensiq-repo as 'main'..."
git push lensiq-repo ${CURRENT_BRANCH}:main

echo -e "${GREEN}✅ Branch pushed successfully${NC}"
echo ""

# ============================================
# Step 6: Verify Push
# ============================================

echo "📋 Step 6: Verifying push..."
echo ""

git ls-remote lensiq-repo

echo -e "${GREEN}✅ Push verified${NC}"
echo ""

# ============================================
# Step 7: Clone New Repository
# ============================================

echo "📋 Step 7: Cloning new repository..."
echo ""

# Navigate to parent directory
cd ..

# Check if directory already exists
if [ -d "${NEW_REPO_NAME}" ]; then
    echo -e "${YELLOW}⚠️  Directory ${NEW_REPO_NAME} already exists${NC}"
    read -p "Do you want to remove it and re-clone? (y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf ${NEW_REPO_NAME}
    else
        echo "Skipping clone..."
        cd ${CURRENT_REPO}
        echo ""
        echo "=========================================================="
        echo -e "${GREEN}✅ Repository split complete!${NC}"
        echo "=========================================================="
        exit 0
    fi
fi

# Clone the new repository
echo "Cloning ${NEW_REPO_URL}..."
git clone ${NEW_REPO_URL}

echo -e "${GREEN}✅ Repository cloned${NC}"
echo ""

# ============================================
# Step 8: Set Up New Repository
# ============================================

echo "📋 Step 8: Setting up new repository..."
echo ""

cd ${NEW_REPO_NAME}

# Verify content
echo "Repository contents:"
ls -la
echo ""

# Show recent commits
echo "Recent commits:"
git log --oneline -5
echo ""

echo -e "${GREEN}✅ New repository ready${NC}"
echo ""

# ============================================
# Success!
# ============================================

echo "=========================================================="
echo -e "${GREEN}✅ Repository split complete!${NC}"
echo "=========================================================="
echo ""
echo "📍 New Repository:"
echo "   https://github.com/${GITHUB_USER}/${NEW_REPO_NAME}"
echo ""
echo "📁 Local Path:"
echo "   $(pwd)"
echo ""
echo "🎯 Next Steps:"
echo "   1. cd ${NEW_REPO_NAME}"
echo "   2. python3 -m venv venv"
echo "   3. source venv/bin/activate"
echo "   4. pip install -r requirements.txt"
echo "   5. cp .env.example .env"
echo "   6. Edit .env with your API keys"
echo "   7. ./start_lensiq.sh"
echo ""
echo "📚 Documentation:"
echo "   - README.md"
echo "   - SPLIT_REPOSITORY_GUIDE.md"
echo "   - docs/DataIngestion_TrendRadar_Branch.md"
echo ""
echo "🎉 Happy coding!"
echo ""

