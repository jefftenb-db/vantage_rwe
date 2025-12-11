# Branch Navigation Guide

## 📌 Current Status

You now have **three separate branches** that can be independently managed and rolled back:

```
main (baseline)
├── feature/prescriber-analytics (Prescriber Analytics)
│   └── feature/market-share-analysis (Prescriber + Market Share)
```

## 🌳 Branch Overview

### `main` Branch
**Contents**: Original OMOP Cohort Builder
- Cohort building with inclusion/exclusion criteria
- Natural language search (GenAI)
- Database statistics
- No commercial analytics

**When to use**: If you want the baseline application without any new features

### `feature/prescriber-analytics` Branch
**Contents**: `main` + Prescriber Analytics
- ✅ All features from `main`
- ✅ Prescriber search and profiling
- ✅ Drug prescriber analytics (top prescribers, market concentration)
- ✅ Prescriber targeting (identify high-value HCPs)
- ✅ Treatment pathway analysis
- ❌ No market share analytics

**When to use**: If you want prescriber analytics but not market share

### `feature/market-share-analysis` Branch (CURRENT)
**Contents**: `main` + Prescriber Analytics + Market Share Analytics
- ✅ All features from `main`
- ✅ All prescriber analytics features
- ✅ Market share overview with concentration metrics
- ✅ Market share trend analysis
- ✅ Competitive positioning
- ✅ New-to-brand (NBx) analysis

**When to use**: Full commercial intelligence suite

## 🔄 How to Switch Between Branches

### Switch to main (baseline only)
```bash
git checkout main
```
**Result**: No prescriber or market share features

### Switch to prescriber-analytics only
```bash
git checkout feature/prescriber-analytics
```
**Result**: Prescriber analytics available, no market share

### Switch to full suite (prescriber + market share)
```bash
git checkout feature/market-share-analysis
```
**Result**: All commercial analytics features

### Check current branch
```bash
git branch
# or
git status
```

## 🧪 Testing Each Configuration

After switching branches, restart your services:

```bash
# Backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# Frontend (new terminal)
cd frontend
npm start
```

Then navigate to http://localhost:3000 and check available tabs.

## 📊 Feature Comparison Table

| Feature | main | prescriber-analytics | market-share-analysis |
|---------|------|---------------------|----------------------|
| Cohort Builder | ✅ | ✅ | ✅ |
| GenAI Query | ✅ | ✅ | ✅ |
| Database Stats | ✅ | ✅ | ✅ |
| Prescriber Search | ❌ | ✅ | ✅ |
| Drug Prescriber Analytics | ❌ | ✅ | ✅ |
| Prescriber Targeting | ❌ | ✅ | ✅ |
| Treatment Pathways | ❌ | ✅ | ✅ |
| Market Share Overview | ❌ | ❌ | ✅ |
| Market Share Trends | ❌ | ❌ | ✅ |
| Competitive Positioning | ❌ | ❌ | ✅ |
| NBx Analysis | ❌ | ❌ | ✅ |

## 🔀 Merging Features (When Ready)

### Option 1: Keep features separate
Stay on current branches. Switch between them as needed.

### Option 2: Merge prescriber analytics to main
```bash
git checkout main
git merge feature/prescriber-analytics
```
This makes prescriber analytics permanent in `main`.

### Option 3: Merge everything to main
```bash
git checkout main
git merge feature/market-share-analysis
```
This makes both prescriber and market share analytics permanent in `main`.

## ⚠️ Important Notes

### If you want to ONLY keep market share (not prescriber):
Currently, `feature/market-share-analysis` builds on top of `feature/prescriber-analytics`, so you get both. If you only want market share, you would need to:
1. Checkout `main`
2. Create a new branch
3. Cherry-pick just the market share commits

### Recommended Approach:
Keep the current structure. Both features are complementary and valuable for pharma commercial teams.

## 🎯 Rollback Scenarios

### "I don't like market share analytics"
```bash
git checkout feature/prescriber-analytics
```
You keep prescriber analytics, lose market share.

### "I don't like either new feature"
```bash
git checkout main
```
You're back to the original application.

### "I like it all!"
Stay on `feature/market-share-analysis` or merge it to `main`:
```bash
git checkout main
git merge feature/market-share-analysis
```

## 📝 Branch Documentation

- **Main app**: See `README.md`, `QUICKSTART.md`
- **Prescriber analytics**: See `PRESCRIBER_ANALYTICS.md`
- **Market share**: See `MARKET_SHARE_ANALYTICS.md`

## 🚀 Recommended Next Steps

1. **Test the full suite** (stay on `feature/market-share-analysis`)
   - Use sample drug IDs from your database
   - Try all four tabs in each analytics module

2. **If satisfied, merge to main**:
   ```bash
   git checkout main
   git merge feature/market-share-analysis
   git push origin main  # If you have a remote
   ```

3. **If you need rollback**, just switch branches as shown above

## 🆘 Help

### I'm confused which branch I'm on
```bash
git branch
# The branch with * is your current branch
```

### I made changes and want to switch branches
```bash
# Save your work first
git add .
git commit -m "WIP: my changes"

# Then switch
git checkout <branch-name>
```

### I want to see differences between branches
```bash
# Compare main vs. prescriber-analytics
git diff main feature/prescriber-analytics

# Compare prescriber-analytics vs. market-share-analysis
git diff feature/prescriber-analytics feature/market-share-analysis
```

## 📞 Quick Reference

| Goal | Command |
|------|---------|
| See current branch | `git branch` or `git status` |
| Switch to baseline | `git checkout main` |
| Switch to prescriber only | `git checkout feature/prescriber-analytics` |
| Switch to full suite | `git checkout feature/market-share-analysis` |
| Merge prescriber to main | `git checkout main && git merge feature/prescriber-analytics` |
| Merge everything to main | `git checkout main && git merge feature/market-share-analysis` |

---

**You have complete control over which features to use!** 🎮

