# Job Search Pipeline - Scripts

Automation and testing scripts for the job search pipeline.

---

## 📋 Available Scripts

### **Daily Workflow**

#### `my_daily_search.sh` ⭐ **RECOMMENDED**
**Purpose:** Automated daily job search with results summary

**Usage:**
```bash
./scripts/my_daily_search.sh
```

**What it does:**
- ✅ Runs full job search pipeline
- ✅ Shows count of jobs found
- ✅ Displays sample job preview
- ✅ Provides statistics and next steps
- ✅ Color-coded output
- ✅ Error handling

**Perfect for:** Daily routine (run every morning)

**Output:**
```
================================================================
🔍 Daily Job Search - Friday, November 22, 2025 at 9:00 AM
================================================================

✅ Found 5 new job(s)

📁 Location: jobs/pipeline/2025-11-22/

📄 Sample Job Preview
... [shows first job details]

💡 Next Steps
1. Review jobs: cat jobs/pipeline/2025-11-22/*.txt
```

---

### **Weekly Analysis**

#### `weekly_summary.sh`
**Purpose:** Comprehensive weekly analytics and trends

**Usage:**
```bash
./scripts/weekly_summary.sh      # Last 7 days
./scripts/weekly_summary.sh 14   # Last 14 days
./scripts/weekly_summary.sh 30   # Last month
```

**What it analyzes:**
- 📅 Jobs by day breakdown
- 📊 Summary statistics
- 🏢 Most common companies
- 💰 Salary insights
- 🎯 Filtering effectiveness
- 📁 Recent job files
- 💡 Personalized recommendations

**Perfect for:** Weekly review (recommended Sunday evening)

**Output:**
```
================================================================
📊 Weekly Job Search Summary - Last 7 Days
================================================================

📅 Jobs by Day
✓ Monday, November 18: 3 job(s)
✓ Wednesday, November 20: 5 job(s)
✓ Friday, November 22: 4 job(s)

📈 Summary Statistics
   Days searched: 3 / 7
   Total jobs found: 12
   Average per search day: 4 jobs

🏢 Most Common Companies
   3 - Tech Corp
   2 - Cloud Inc
   1 - Startup Co

🎯 Filtering Effectiveness
   Filter rate: 45%
   ✓ Good filter rate (balanced)
```

---

### **Testing & Validation**

#### `test_jsearch_adapter.py`
**Purpose:** Test JSearch adapter with basic search criteria

**Usage:**
```bash
python scripts/test_jsearch_adapter.py
```

**What it tests:**
- ✅ API connection
- ✅ Configuration loading
- ✅ Search execution
- ✅ Result parsing
- ✅ Basic filtering

**Uses:** `config/search-criteria.yaml` only

**Perfect for:** Quick validation, troubleshooting

---

#### `test_complex_criteria.py`
**Purpose:** Test JSearch with complex search criteria and filtering

**Usage:**
```bash
python scripts/test_complex_criteria.py
```

**What it tests:**
- ✅ Complex criteria loading
- ✅ Salary range filtering
- ✅ Experience level filtering
- ✅ Tech stack filtering
- ✅ Company stage filtering
- ✅ Posted date filtering

**Uses:** Both `search-criteria.yaml` AND `search-criteria-complex.yaml`

**Perfect for:** Validating filter configuration before daily runs

**Output:**
```
============================================================
JSearch Adapter Test - Complex Search Criteria
============================================================

📋 Complex Search Criteria Loaded:
   Salary Range: $150,000 - $200,000
   Experience Levels: Senior, Staff, Lead
   Required Tech: AWS, Terraform

✅ TEST SUCCESSFUL
Total jobs found after filtering: 3

1. Senior DevOps Engineer
   Company:     Tech Corp
   Salary:      $150,000 - $180,000
   ✅ Meets salary criteria
   ✅ Required tech found: AWS, Terraform
   ✅ Experience level: Senior
```

---

## 🔄 Recommended Workflow

### **Daily Routine** (5 minutes)
```bash
# Every morning at 9 AM
./scripts/my_daily_search.sh

# Review results
cat jobs/pipeline/$(date +%Y-%m-%d)/*.txt | less

# Apply to interesting jobs
```

### **Weekly Review** (15 minutes)
```bash
# Every Sunday evening
./scripts/weekly_summary.sh

# Adjust configuration based on recommendations
code config/search-criteria-complex.yaml

# Clear processed jobs if needed
rm data/processed_jobs.json
```

### **After Configuration Changes** (2 minutes)
```bash
# Test your changes
python scripts/test_complex_criteria.py

# If looks good, run full search
./scripts/my_daily_search.sh
```

---

## 🤖 Automation Setup

### **Option 1: Cron (Unix/Linux/macOS)**

Add to crontab:
```bash
crontab -e
```

Add this line (runs daily at 9 AM):
```
0 9 * * * /Users/dshaevel/workspace-ds/job-search-pipeline/scripts/my_daily_search.sh >> /Users/dshaevel/job-search-cron.log 2>&1
```

Weekly summary (Sundays at 6 PM):
```
0 18 * * 0 /Users/dshaevel/workspace-ds/job-search-pipeline/scripts/weekly_summary.sh >> /Users/dshaevel/job-search-weekly.log 2>&1
```

### **Option 2: macOS Launchd**

Create: `~/Library/LaunchAgents/com.davidshaevel.jobsearch.plist`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.davidshaevel.jobsearch</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/dshaevel/workspace-ds/job-search-pipeline/scripts/my_daily_search.sh</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>9</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>/Users/dshaevel/job-search.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/dshaevel/job-search-error.log</string>
</dict>
</plist>
```

Load it:
```bash
launchctl load ~/Library/LaunchAgents/com.davidshaevel.jobsearch.plist
```

---

## 🛠️ Troubleshooting

### Script Won't Run

**Problem:** `Permission denied`

**Solution:**
```bash
chmod +x scripts/*.sh
```

---

### No Jobs Found

**Problem:** `⚠️ No new jobs found today`

**Causes:**
1. All jobs previously processed
2. Filters too restrictive
3. No jobs matching criteria

**Solutions:**
```bash
# Clear processed jobs cache
rm data/processed_jobs.json

# Relax filters
code config/search-criteria-complex.yaml
# Increase salary max, decrease min
# Remove tech_stack requirements
# Extend date_range to 30 days

# Test again
python scripts/test_complex_criteria.py
```

---

### API Errors

**Problem:** `401 Unauthorized` or `429 Too Many Requests`

**Causes:**
1. Invalid RAPIDAPI_KEY
2. Exceeded free tier quota (50 requests / 7 days)

**Solutions:**
```bash
# Check API key
cat .env | grep RAPIDAPI_KEY

# Check quota on RapidAPI dashboard
open https://rapidapi.com/dashboard

# Wait for quota to reset
# Or upgrade to paid tier
```

---

## 📊 Understanding Output

### Filter Rate Interpretation

**Filter Rate = (Jobs discovered - Jobs saved) / Jobs discovered × 100%**

| Filter Rate | Meaning | Action |
|-------------|---------|--------|
| 70%+ | Too strict | Relax criteria |
| 30-70% | ✅ Balanced | Keep current |
| <30% | Too loose | Tighten criteria |

### Jobs Per Day Guide

| Jobs/Day | Interpretation | Action |
|----------|---------------|--------|
| 0-1 | Too few | Broaden search |
| 2-5 | ✅ Good | Keep current |
| 6-10 | Many | Review quality |
| 10+ | Too many | Tighten filters |

---

## 📚 Related Documentation

- **Configuration Guide:** [docs/CONFIGURATION_GUIDE.md](../docs/CONFIGURATION_GUIDE.md)
- **Testing Guide:** [docs/LOCAL_TESTING_GUIDE.md](../docs/LOCAL_TESTING_GUIDE.md)
- **Project README:** [README.md](../README.md)
- **Implementation Plan:** [PLAN.md](../PLAN.md)

---

## 🆘 Quick Help

**Need help?** Check these resources:

1. **Configuration issues:** `docs/CONFIGURATION_GUIDE.md`
2. **Testing problems:** `docs/LOCAL_TESTING_GUIDE.md`
3. **API errors:** Check `.env` and RapidAPI dashboard
4. **Filter tuning:** See CONFIGURATION_GUIDE.md "Common Adjustments"

**Still stuck?** Review the logs:
```bash
# See what happened in last run
cat /Users/dshaevel/job-search-cron.log

# Check processed jobs
cat data/processed_jobs.json | python -m json.tool | less
```

---

**Last Updated:** November 22, 2025
**Phase Status:** Phase 2 Complete (Deduplication & Filtering)
**Scripts Available:** 4 (2 automation, 2 testing)
