# Job Search Pipeline - Configuration Customization Guide

**Last Updated:** November 22, 2025
**For:** David Shaevel - Senior DevOps Engineer Job Search
**Target Roles:** DevOps Engineer, Platform Engineer, SRE, Infrastructure Engineer
**Location:** Austin, TX (Hybrid/Remote)
**Salary Target:** $150,000 - $170,000 base

---

## Overview

This guide shows you how to customize both configuration files to match your specific job search criteria based on your background and requirements.

**Your Profile:**
- **Experience:** 20+ years in software engineering, 10+ years DevOps/Infrastructure
- **Key Skills:** AWS, Terraform, Docker, Kubernetes, CI/CD, Python, Ansible
- **Target Salary:** $150,000 - $170,000 base (competitive with Aravo actual: $170K)
- **Location:** Austin, TX (prefer hybrid 2-3 days, acceptable 3-4 days)
- **Experience Level:** Senior, Staff, Lead (not Principal yet, not Junior)
- **Work-Life Balance:** Important - prefer 40-45 hrs/week, limited on-call

---

## File 1: `search-criteria.yaml` - What to Search For

**Purpose:** Tell the API what jobs to find
**Used by:** SearchOrchestrator (builds API query)
**Impact:** Determines what jobs come back from JSearch

### Your Customized Configuration

```yaml
# Search Criteria - API Query Parameters
# Purpose: Tell JSearch what jobs to find
# Used BEFORE filtering - casts the net

search:
  # Keywords - Match your target roles
  # Tip: Use broad terms here, filter specifically later
  keywords:
    - "DevOps Engineer"
    - "Platform Engineer"
    - "Infrastructure Engineer"
    - "Site Reliability Engineer"
    - "Cloud Engineer"
    - "DevOps Lead"
    - "Senior DevOps"
    - "Staff DevOps"
    # Consider adding:
    # - "Infrastructure Lead"
    # - "Platform Lead"
    # - "SRE Lead"

  # Location - Your primary target
  location: "Austin, TX"

  # Optional: Remote filter
  # Uncomment if you ONLY want remote jobs
  # remote: true

  # Optional: Employment type
  # Uncomment if you ONLY want full-time
  # employment_type: "FULLTIME"
```

### Keyword Strategy Explained

**Current Keywords (Broad):**
- Cast wide net to catch all variations
- JSearch will find anything matching these terms
- You'll filter specifically in `search-criteria-complex.yaml`

**Why These Keywords:**
1. **"DevOps Engineer"** - Your primary target (like Aravo role)
2. **"Platform Engineer"** - Alternative title, same work
3. **"Infrastructure Engineer"** - Common variation
4. **"Site Reliability Engineer"** - SRE roles overlap heavily with DevOps
5. **"Cloud Engineer"** - Cloud-focused DevOps
6. **"DevOps Lead"** / **"Senior DevOps"** / **"Staff DevOps"** - Level-specific

**What NOT to Include:**
- ❌ "Junior DevOps" - You're beyond junior level
- ❌ "DevOps Intern" - Not relevant
- ❌ Specific technologies (AWS, Terraform) - Filter these later
- ❌ Company names - That's for blacklisting

### Location Strategy

**Option 1: Austin-focused (Current)**
```yaml
location: "Austin, TX"
```
- **Pro:** Highly targeted, local opportunities
- **Con:** Misses remote opportunities elsewhere

**Option 2: Remote-first**
```yaml
location: "Remote"
```
- **Pro:** Catches all remote jobs nationwide
- **Con:** May include jobs requiring some travel to non-Austin offices

**Option 3: Hybrid approach (Recommended)**
```yaml
# Run search twice with different configs
# Search 1: Local Austin
location: "Austin, TX"

# Search 2: Remote nationwide (separate run)
# location: "Remote"
```

### Testing Your Search Criteria

```bash
# Test current configuration
python scripts/test_jsearch_adapter.py

# Expected: ~10 jobs matching "DevOps" in "Austin, TX"
```

---

## File 2: `search-criteria-complex.yaml` - What to Keep

**Purpose:** Filter the jobs that came back from the API
**Used by:** FilterEngine (post-processing)
**Impact:** Determines which jobs actually get saved to files

### Your Customized Configuration

```yaml
# Complex Search Criteria - Post-API Filtering
# Purpose: Filter jobs AFTER they come back from JSearch
# Used AFTER API call - quality control filter

search:
  # Keywords - Not used for API filtering currently
  # Kept for future multi-board support
  keywords:
    primary:
      - "DevOps Engineer"
      - "Platform Engineer"
      - "Infrastructure Engineer"
      - "Site Reliability Engineer"
    secondary:
      - "Cloud Engineer"
      - "Backend Engineer"
      - "Software Engineer Infrastructure"

  # Location preferences
  location:
    preferred:
      - "Austin, TX"
      - "Remote"
      - "United States"
    acceptable:
      - "Texas"
      - "Hybrid"

  # Salary Range - CRITICAL FILTER
  # Based on Aravo actual: $170K base + 10% bonus
  # Your target: $150K-$240K
  salary_range:
    min: 150000   # Your minimum acceptable ($150K)
    max: 240000   # Upper bound (allows for Staff/Lead roles)

  # Experience Level - Match your seniority
  # You're Senior→Staff level (20+ years experience)
  experience_level:
    - "Senior"      # Primary target (like Aravo)
    - "Staff"       # Stretch goal
    - "Lead"        # Acceptable
    - "Principal"   # Reach (if interested)
    # NOT included:
    # - "Junior" - Too junior
    # - "Mid-level" - Below your level

  # Company Stage - Based on your evaluations
  # You prefer stability (Aravo: 25 years, profitable)
  company_stage:
    exclude:
      - "Pre-seed"     # Too risky
      - "Idea stage"   # No product yet
      - "Stealth"      # Unknown
    prefer:
      - "Series A+"    # Has traction
      - "Series B+"    # Scaling
      - "Profitable"   # Best case (like Aravo)
      - "Established"  # 5+ years
      - "Public"       # Very stable

  # Tech Stack - Match your core skills
  # Based on your background: AWS, Terraform, Docker, K8s, CI/CD
  tech_stack:
    required:
      # Core DevOps skills you have
      - "AWS"          # Your primary cloud (Walmart, Zello)
      - "Terraform"    # Your IaC tool of choice
      # Note: Requiring BOTH filters heavily
      # Consider making one "preferred" instead

    preferred:
      # Nice-to-haves that match your background
      - "Python"       # Your scripting language
      - "Kubernetes"   # K8s experience (Zello)
      - "Docker"       # Container experience
      - "CI/CD"        # Jenkins, GitHub Actions
      - "Ansible"      # Config management (Walmart)
      - "Prometheus"   # Monitoring (recent davidshaevel.com project!)
      - "Grafana"      # Observability
      # Note: "preferred" doesn't filter out, just nice to have

  # Exclude specific companies
  exclude_companies:
    # Add companies you DON'T want to work for
    - "Current Employer"           # Replace with actual if needed
    - "Companies Already Evaluated" # Placeholder
    # Examples you might add:
    # - "Revature"  # If you don't want contracting firms
    # - "Amazon"    # If on-call culture concerns you

  # Posted date filter - Get fresh jobs
  date_range:
    posted_within_days: 14  # Last 2 weeks (increased from 7 for more results)
    # Options:
    # - 7 days = Very fresh, fewer results
    # - 14 days = Fresh, more results (recommended)
    # - 30 days = Includes older posts, maximum results
```

### Salary Range Decision Matrix

Your target is **$150K-$170K** based on:
- Aravo actual: $170K base + 10% bonus + ~3K options
- Your evaluation criteria: "Competitive with market"

**Option 1: Strict (Current)**
```yaml
salary_range:
  min: 150000
  max: 240000
```
- **Filters out:** Jobs under $150K (too low)
- **Keeps:** $150K-$240K (your target + room for negotiation)
- **Risk:** May filter out good jobs that don't disclose salary

**Option 2: Permissive**
```yaml
salary_range:
  min: 140000  # Allow $10K below target
  max: 250000  # Allow higher for Lead/Principal
```
- **Filters out:** Only jobs clearly below market
- **Keeps:** More jobs (some may need negotiation)
- **Risk:** Includes jobs you'll need to negotiate up

**Option 3: No salary filter (Discovery mode)**
```yaml
# Comment out salary_range entirely
# salary_range:
#   min: 150000
#   max: 240000
```
- **Filters out:** Nothing based on salary
- **Keeps:** All jobs (you manually review salaries)
- **Risk:** Waste time on low-paying jobs

**Recommendation:** Start with Option 1 (strict), relax to Option 2 if too few results.

### Tech Stack Filter Strategy

**Current Configuration:**
```yaml
tech_stack:
  required:
    - "AWS"
    - "Terraform"
```

**Impact:** Job MUST mention both AWS AND Terraform to pass filter.

**Your Skills:**
- ✅ AWS (Walmart, Zello, davidshaevel.com platform)
- ✅ Terraform (Walmart, Zello, davidshaevel.com platform)
- ✅ Docker (Walmart, Zello)
- ✅ Kubernetes (Zello)
- ✅ Python (Primary scripting language)
- ✅ Ansible (Walmart)
- ✅ CI/CD (Jenkins, Azure DevOps, GitHub Actions)

**Filtering Options:**

**Option A: Strict Cloud + IaC (Current)**
```yaml
required:
  - "AWS"
  - "Terraform"
```
- **Best for:** Cloud-native DevOps roles
- **Filters out:** Azure/GCP-only, non-IaC roles
- **Risk:** Misses multi-cloud or CloudFormation shops

**Option B: Cloud-only**
```yaml
required:
  - "AWS"
# Terraform is preferred but not required
```
- **Best for:** Broader cloud roles
- **Filters out:** Non-AWS roles
- **Risk:** Includes roles without IaC (less appealing)

**Option C: Very permissive (Discovery)**
```yaml
required: []  # Nothing required
preferred:
  - "AWS"
  - "Terraform"
  - "Python"
  - "Kubernetes"
```
- **Best for:** Seeing all opportunities
- **Filters out:** Nothing
- **Risk:** Many irrelevant jobs

**Recommendation:** Start with Option A (AWS + Terraform), relax to Option B if too restrictive.

### Experience Level Filter

**Current Configuration:**
```yaml
experience_level:
  - "Senior"
  - "Staff"
  - "Lead"
  - "Principal"
```

**How it works:** Job title or description must mention one of these terms.

**Your Level:**
- 20+ years total experience
- Senior DevOps → Staff DevOps trajectory
- Aravo hired you as "Senior" at $170K

**Recommendations:**

**Conservative (Get offers first):**
```yaml
experience_level:
  - "Senior"  # Your current level
  - "Staff"   # Logical next step
  - "Lead"    # Alternative title
```

**Aggressive (Aim higher):**
```yaml
experience_level:
  - "Staff"      # Target this level
  - "Lead"       # Alternative
  - "Principal"  # Stretch goal
  # Exclude "Senior" to force higher-level roles
```

**Start with conservative**, prove your Staff-level capability in interviews, negotiate up.

---

## Complete Example Configurations

### Configuration Set 1: Balanced (Recommended Starting Point)

**search-criteria.yaml:**
```yaml
search:
  keywords:
    - "DevOps Engineer"
    - "Platform Engineer"
    - "Infrastructure Engineer"
    - "Site Reliability Engineer"
    - "Cloud Engineer"
  location: "Austin, TX"
```

**search-criteria-complex.yaml:**
```yaml
search:
  salary_range:
    min: 150000
    max: 240000

  experience_level:
    - "Senior"
    - "Staff"
    - "Lead"

  tech_stack:
    required:
      - "AWS"
      - "Terraform"
    preferred:
      - "Python"
      - "Kubernetes"
      - "Docker"
      - "CI/CD"

  exclude_companies: []

  date_range:
    posted_within_days: 14
```

**Expected Results:** 3-8 jobs per search, highly relevant

---

### Configuration Set 2: Discovery Mode (Maximum Results)

**search-criteria.yaml:**
```yaml
search:
  keywords:
    - "DevOps"
    - "Platform"
    - "Infrastructure"
    - "SRE"
    - "Cloud"
  location: "Austin, TX"
```

**search-criteria-complex.yaml:**
```yaml
search:
  salary_range:
    min: 140000  # Relaxed
    max: 250000  # Very permissive

  experience_level:
    - "Senior"
    - "Staff"
    - "Lead"
    - "Principal"
    - "Mid-level"  # Included for broader search

  tech_stack:
    required: []  # Nothing required
    preferred:
      - "AWS"
      - "Terraform"
      - "Python"

  exclude_companies: []

  date_range:
    posted_within_days: 30  # Last month
```

**Expected Results:** 10-20 jobs per search, some irrelevant

---

### Configuration Set 3: Highly Targeted (Quality over Quantity)

**search-criteria.yaml:**
```yaml
search:
  keywords:
    - "Senior DevOps Engineer"
    - "Staff Platform Engineer"
    - "Lead Infrastructure Engineer"
  location: "Austin, TX"
```

**search-criteria-complex.yaml:**
```yaml
search:
  salary_range:
    min: 150000  # Only premium roles
    max: 240000

  experience_level:
    - "Senior"
    - "Staff"
    - "Lead"

  tech_stack:
    required:
      - "AWS"
      - "Terraform"
      - "Kubernetes"  # Triple requirement - very strict
    preferred:
      - "Python"
      - "CI/CD"
      - "Prometheus"

  company_stage:
    exclude:
      - "Pre-seed"
      - "Seed"
      - "Idea stage"
    prefer:
      - "Series B+"
      - "Profitable"
      - "Established"

  date_range:
    posted_within_days: 7  # Very fresh
```

**Expected Results:** 1-5 jobs per search, very high quality

---

## Testing Your Configurations

### Step 1: Start with Balanced Configuration

```bash
cd /Users/dshaevel/workspace-ds/job-search-pipeline
source venv/bin/activate

# Copy balanced config
# (edit the files as shown in "Configuration Set 1" above)

# Clear cache to see fresh results
rm data/processed_jobs.json

# Run search
python src/main.py

# Note the count
```

### Step 2: Adjust Based on Results

**If you get 0-2 jobs:**
- Salary range too narrow → Increase max to $250K
- Tech stack too strict → Remove "Terraform" from required
- Experience level too narrow → Add "Mid-level"
- Date range too fresh → Increase to 30 days

**If you get 10+ jobs:**
- Salary range too wide → Increase min to $160K
- Tech stack too loose → Add "Kubernetes" to required
- Experience level too broad → Remove "Mid-level"
- Keywords too generic → Use "Senior DevOps" instead of "DevOps"

**If you get 3-8 jobs:**
- ✅ Perfect! Review the jobs for quality

### Step 3: Refine Over Time

```bash
# Week 1: Discovery mode (see everything)
# Edit configs to be permissive
python src/main.py

# Week 2: Add blacklists based on Week 1 results
# Edit config/filters.yaml:
#   blacklist:
#     companies: ["Company X", "Company Y"]
python src/main.py

# Week 3: Tighten criteria based on Week 2 quality
# Edit search-criteria-complex.yaml:
#   salary_range.min: 150000  # Raise minimum
python src/main.py
```

---

## Common Adjustments

### Adjustment 1: Not Enough Results

**Problem:** Only getting 1-2 jobs per search

**Solution 1 - Relax Salary:**
```yaml
salary_range:
  min: 140000  # Down from 150000
  max: 250000  # Up from 200000
```

**Solution 2 - Relax Tech Stack:**
```yaml
tech_stack:
  required:
    - "AWS"  # Only AWS required (remove Terraform)
  preferred:
    - "Terraform"  # Make it preferred instead
```

**Solution 3 - Extend Date Range:**
```yaml
date_range:
  posted_within_days: 30  # Up from 14
```

### Adjustment 2: Too Many Low-Quality Results

**Problem:** Getting 20+ jobs but most are irrelevant

**Solution 1 - Raise Salary Floor:**
```yaml
salary_range:
  min: 160000  # Up from 150000
```

**Solution 2 - Add Company Stage Filter:**
```yaml
company_stage:
  exclude:
    - "Pre-seed"
    - "Seed"
```

**Solution 3 - Stricter Tech Requirements:**
```yaml
tech_stack:
  required:
    - "AWS"
    - "Terraform"
    - "Kubernetes"  # Add third requirement
```

### Adjustment 3: Exclude Specific Types of Jobs

**Problem:** Getting consulting firms, contract-only, or specific companies you don't want

**Solution - Edit `config/filters.yaml`:**
```yaml
filters:
  blacklist:
    companies:
      - "Revature"        # Consulting firm
      - "Cognizant"       # Consulting firm
      - "InfoSys"         # Consulting firm
      - "TCS"             # Consulting firm
      - "Current Employer Name"  # Your current company

    titles:
      - "Junior"
      - "Intern"
      - "Entry Level"
      - "Contract"        # If you don't want contract roles

    keywords:
      - "Contract Only"
      - "No Benefits"
      - "Commission"
      - "Unpaid"
```

---

## Monitoring and Iteration

### Daily Workflow

```bash
#!/bin/bash
# Save as: scripts/my_daily_search.sh

cd /Users/dshaevel/workspace-ds/job-search-pipeline
source venv/bin/activate

# Run search
echo "🔍 Running daily job search..."
python src/main.py

# Show results
TODAY=$(date +%Y-%m-%d)
echo ""
echo "📊 Results saved to: jobs/pipeline/$TODAY/"
ls -1 jobs/pipeline/$TODAY/ | wc -l | xargs echo "   Jobs found:"

# Show example
echo ""
echo "📄 Sample job:"
ls jobs/pipeline/$TODAY/ | head -1 | xargs -I {} head -20 "jobs/pipeline/$TODAY/{}"
```

### Weekly Review

Every Sunday:
1. Review jobs from past week
2. Identify patterns in rejections/interests
3. Adjust configurations accordingly
4. Update blacklists based on companies to avoid

### Monthly Calibration

Every month:
1. Compare actual offers to salary range
2. Adjust salary_range based on market feedback
3. Update tech_stack based on trending requirements
4. Review experience_level if you get promoted/certified

---

## Quick Reference

### Files to Edit

| File | Purpose | What to Change |
|------|---------|----------------|
| `config/search-criteria.yaml` | API query | keywords, location |
| `config/search-criteria-complex.yaml` | Post-filter | salary, tech_stack, experience_level |
| `config/filters.yaml` | Blacklists | companies, titles, keywords |

### Test Commands

```bash
# Test with basic criteria
python scripts/test_jsearch_adapter.py

# Test with complex criteria
python scripts/test_complex_criteria.py

# Run full pipeline
python src/main.py

# Clear cache and re-run
rm data/processed_jobs.json && python src/main.py
```

---

## Your Personalized Starting Point

Based on your Aravo evaluation and job search profile:

**Recommended Initial Configuration:**

**search-criteria.yaml:**
```yaml
search:
  keywords:
    - "Senior DevOps Engineer"
    - "Staff DevOps Engineer"
    - "DevOps Lead"
    - "Platform Engineer"
    - "Infrastructure Engineer"
  location: "Austin, TX"
```

**search-criteria-complex.yaml:**
```yaml
search:
  salary_range:
    min: 150000  # Your minimum
    max: 240000  # Room for negotiation

  experience_level:
    - "Senior"
    - "Staff"
    - "Lead"

  tech_stack:
    required:
      - "AWS"
      - "Terraform"
    preferred:
      - "Python"
      - "Kubernetes"
      - "Docker"
      - "CI/CD"
      - "Ansible"
      - "Prometheus"

  date_range:
    posted_within_days: 14
```

This matches your Aravo profile:
- ✅ $170K actual vs $150K-200K range
- ✅ Senior/Staff level
- ✅ AWS + Terraform core requirements
- ✅ Hybrid Austin location

**Ready to customize? Let me know if you want help with any specific adjustments!**
