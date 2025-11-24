#!/bin/bash
#
# Weekly Job Search Summary
#
# Purpose: Generate weekly summary of job search results
# Usage: ./scripts/weekly_summary.sh [days]
#
# Arguments:
#   days - Number of days to summarize (default: 7)
#
# Example:
#   ./scripts/weekly_summary.sh      # Last 7 days
#   ./scripts/weekly_summary.sh 14   # Last 14 days

set -e  # Exit on any error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Get number of days (default 7)
DAYS=${1:-7}

# Get script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo ""
echo "================================================================"
echo "📊 Weekly Job Search Summary - Last $DAYS Days"
echo "================================================================"
echo ""
echo "Generated: $(date '+%A, %B %d, %Y at %I:%M %p')"
echo ""

# Change to project root
cd "$PROJECT_ROOT"

# Check if jobs directory exists
if [ ! -d "jobs/pipeline" ]; then
    echo -e "${YELLOW}⚠️  No job search results found${NC}"
    echo "   Run your first search: python src/main.py"
    exit 0
fi

# Find all job directories from the last N days
echo "================================================================"
echo "📅 Jobs by Day"
echo "================================================================"
echo ""

TOTAL_JOBS=0
DAYS_WITH_JOBS=0

# Generate date list for last N days
for i in $(seq 0 $((DAYS - 1))); do
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        DATE=$(date -v-${i}d +%Y-%m-%d)
    else
        # Linux
        DATE=$(date -d "$i days ago" +%Y-%m-%d)
    fi

    DIR="jobs/pipeline/$DATE"

    if [ -d "$DIR" ]; then
        COUNT=$(ls -1 "$DIR" 2>/dev/null | wc -l | tr -d ' ')
        if [ "$COUNT" -gt 0 ]; then
            DAYS_WITH_JOBS=$((DAYS_WITH_JOBS + 1))
            TOTAL_JOBS=$((TOTAL_JOBS + COUNT))

            # Format date nicely
            if [[ "$OSTYPE" == "darwin"* ]]; then
                NICE_DATE=$(date -j -f "%Y-%m-%d" "$DATE" "+%A, %B %d" 2>/dev/null || echo "$DATE")
            else
                NICE_DATE=$(date -d "$DATE" "+%A, %B %d" 2>/dev/null || echo "$DATE")
            fi

            echo -e "${GREEN}✓${NC} $NICE_DATE: ${BLUE}$COUNT job(s)${NC}"
        fi
    fi
done

if [ "$DAYS_WITH_JOBS" -eq 0 ]; then
    echo -e "${YELLOW}   No jobs found in the last $DAYS days${NC}"
fi

echo ""
echo "================================================================"
echo "📈 Summary Statistics"
echo "================================================================"
echo ""
echo "   Days searched: $DAYS_WITH_JOBS / $DAYS"
echo "   Total jobs found: $TOTAL_JOBS"

if [ "$DAYS_WITH_JOBS" -gt 0 ]; then
    AVG=$((TOTAL_JOBS / DAYS_WITH_JOBS))
    echo "   Average per search day: $AVG jobs"
fi

# Show processed jobs count
if [ -f "data/processed_jobs.json" ]; then
    echo ""
    PROCESSED_COUNT=$(python -c "import json; print(len(json.load(open('data/processed_jobs.json'))))" 2>/dev/null || echo "0")
    echo "   Total processed (all time): $PROCESSED_COUNT"
fi

# Analyze job titles (most common companies/roles)
echo ""
echo "================================================================"
echo "🏢 Most Common Companies"
echo "================================================================"
echo ""

# Find all jobs from last N days and extract company names
for i in $(seq 0 $((DAYS - 1))); do
    if [[ "$OSTYPE" == "darwin"* ]]; then
        DATE=$(date -v-${i}d +%Y-%m-%d)
    else
        DATE=$(date -d "$i days ago" +%Y-%m-%d)
    fi

    DIR="jobs/pipeline/$DATE"
    if [ -d "$DIR" ]; then
        ls -1 "$DIR" 2>/dev/null | while read -r file; do
            # Extract company from filename (format: Company_Title_#.txt)
            echo "$file" | cut -d'_' -f1
        done
    fi
done | sort | uniq -c | sort -rn | head -10 | while read -r count company; do
    echo "   $count - $company"
done

# Show salary ranges if available
echo ""
echo "================================================================"
echo "💰 Salary Insights"
echo "================================================================"
echo ""

# Show configured salary range
if [ -f "config/search-criteria-complex.yaml" ]; then
    echo "Configured salary range:"
    grep -A 2 "salary_range:" config/search-criteria-complex.yaml | grep -E "min:|max:" | while read -r line; do
        echo "   $line"
    done
fi

echo ""
echo "================================================================"
echo "🎯 Filtering Effectiveness"
echo "================================================================"
echo ""

# Check processed jobs vs saved jobs
if [ -f "data/processed_jobs.json" ]; then
    PROCESSED=$(python -c "import json; print(len(json.load(open('data/processed_jobs.json'))))" 2>/dev/null || echo "0")
    SAVED=$TOTAL_JOBS

    if [ "$PROCESSED" -gt 0 ]; then
        FILTER_RATE=$((100 * (PROCESSED - SAVED) / PROCESSED))
        echo "   Jobs discovered: $PROCESSED"
        echo "   Jobs saved: $SAVED"
        echo "   Filter rate: ${FILTER_RATE}%"
        echo ""

        if [ "$FILTER_RATE" -gt 70 ]; then
            echo -e "   ${YELLOW}⚠️  High filter rate (>${FILTER_RATE}%)${NC}"
            echo "   Consider relaxing criteria in:"
            echo "   config/search-criteria-complex.yaml"
        elif [ "$FILTER_RATE" -lt 30 ]; then
            echo -e "   ${YELLOW}⚠️  Low filter rate (<${FILTER_RATE}%)${NC}"
            echo "   Consider tightening criteria in:"
            echo "   config/search-criteria-complex.yaml"
        else
            echo -e "   ${GREEN}✓ Good filter rate (${FILTER_RATE}%)${NC}"
        fi
    fi
fi

echo ""
echo "================================================================"
echo "📁 Recent Job Files"
echo "================================================================"
echo ""

# Show 10 most recent job files
echo "Most recent jobs:"
find jobs/pipeline -name "*.txt" -type f -mtime -${DAYS} -print0 2>/dev/null | \
    xargs -0 ls -t 2>/dev/null | head -10 | while read -r file; do
    BASENAME=$(basename "$file" .txt)
    echo "   • $BASENAME"
done

echo ""
echo "================================================================"
echo "💡 Recommendations"
echo "================================================================"
echo ""

# Provide recommendations based on stats
if [ "$TOTAL_JOBS" -eq 0 ]; then
    echo "No jobs found in $DAYS days. Try:"
    echo "   1. Clear cache: rm data/processed_jobs.json"
    echo "   2. Relax filters: edit config/search-criteria-complex.yaml"
    echo "   3. Broaden search: edit config/search-criteria.yaml"
elif [ "$TOTAL_JOBS" -lt 5 ]; then
    echo "Few jobs found ($TOTAL_JOBS in $DAYS days). Consider:"
    echo "   1. Relaxing salary range (increase max, decrease min)"
    echo "   2. Removing tech stack requirements"
    echo "   3. Extending date range (7 → 14 days)"
elif [ "$TOTAL_JOBS" -gt 50 ]; then
    echo "Many jobs found ($TOTAL_JOBS in $DAYS days). Consider:"
    echo "   1. Tightening salary range (increase min)"
    echo "   2. Adding tech stack requirements"
    echo "   3. Adding company blacklists"
else
    echo -e "${GREEN}✓ Good volume ($TOTAL_JOBS jobs in $DAYS days)${NC}"
    echo ""
    echo "Continue current strategy:"
    echo "   • Daily searches: ./scripts/my_daily_search.sh"
    echo "   • Review results regularly"
    echo "   • Update blacklists as needed"
fi

echo ""
echo "================================================================"
echo "🔗 Useful Commands"
echo "================================================================"
echo ""
echo "View all jobs:"
echo "   ${BLUE}cat jobs/pipeline/*/*.txt | less${NC}"
echo ""
echo "Search for keyword in jobs:"
echo "   ${BLUE}grep -r 'Kubernetes' jobs/pipeline/${NC}"
echo ""
echo "Clear processed jobs:"
echo "   ${BLUE}rm data/processed_jobs.json${NC}"
echo ""
echo "Run daily search:"
echo "   ${BLUE}./scripts/my_daily_search.sh${NC}"
echo ""
echo "View configuration guide:"
echo "   ${BLUE}cat docs/CONFIGURATION_GUIDE.md${NC}"
echo ""

echo "================================================================"
echo -e "${GREEN}✅ Weekly summary complete!${NC}"
echo "================================================================"
echo ""
