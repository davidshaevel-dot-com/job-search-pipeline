#!/bin/bash
#
# Daily Job Search Script
#
# Purpose: Run automated job search and show summary of results
# Usage: ./scripts/my_daily_search.sh
#
# What it does:
# 1. Activates virtual environment
# 2. Runs job search pipeline
# 3. Shows count of jobs found
# 4. Displays sample job for quick review
#
# Recommended: Run daily at same time (e.g., 9 AM)
#   crontab entry: 0 9 * * * /path/to/job-search-pipeline/scripts/my_daily_search.sh

set -e  # Exit on any error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo ""
echo "================================================================"
echo "🔍 Daily Job Search - $(date '+%A, %B %d, %Y at %I:%M %p')"
echo "================================================================"
echo ""

# Change to project root
cd "$PROJECT_ROOT"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Error: Virtual environment not found${NC}"
    echo "   Please run: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo -e "${BLUE}📦 Activating virtual environment...${NC}"
source venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ Error: .env file not found${NC}"
    echo "   Please create .env with RAPIDAPI_KEY"
    exit 1
fi

# Run the search
echo -e "${BLUE}🔍 Running job search...${NC}"
echo ""

# Run main.py and capture output
if python src/main.py; then
    SEARCH_SUCCESS=true
else
    SEARCH_SUCCESS=false
    echo ""
    echo -e "${RED}❌ Search failed. Check error messages above.${NC}"
    exit 1
fi

echo ""
echo "================================================================"
echo "📊 Daily Search Results"
echo "================================================================"

# Get today's date in format used by pipeline
TODAY=$(date +%Y-%m-%d)
OUTPUT_DIR="jobs/pipeline/$TODAY"

# Check if output directory exists
if [ ! -d "$OUTPUT_DIR" ]; then
    echo -e "${YELLOW}⚠️  No jobs found today${NC}"
    echo ""
    echo "Possible reasons:"
    echo "  - All jobs filtered out (too restrictive criteria)"
    echo "  - All jobs previously processed (run: rm data/processed_jobs.json)"
    echo "  - No jobs matching search criteria on JSearch"
    echo ""
    echo "Next steps:"
    echo "  1. Check config/search-criteria-complex.yaml"
    echo "  2. Try: rm data/processed_jobs.json && ./scripts/my_daily_search.sh"
    echo "  3. Review docs/CONFIGURATION_GUIDE.md for adjustments"
    exit 0
fi

# Count jobs found
JOB_COUNT=$(ls -1 "$OUTPUT_DIR" 2>/dev/null | wc -l | tr -d ' ')

if [ "$JOB_COUNT" -eq 0 ]; then
    echo -e "${YELLOW}⚠️  No new jobs found today${NC}"
    echo ""
    echo "All jobs were either:"
    echo "  - Previously processed (check data/processed_jobs.json)"
    echo "  - Filtered out by your criteria"
    echo ""
    echo "To see jobs again: rm data/processed_jobs.json"
else
    echo -e "${GREEN}✅ Found $JOB_COUNT new job(s)${NC}"
    echo ""
    echo "📁 Location: $OUTPUT_DIR/"
    echo ""

    # Show list of jobs
    echo "📝 Jobs saved:"
    ls -1 "$OUTPUT_DIR" | head -10 | while read -r file; do
        # Extract company and title from filename
        # Format: Company_Title_#.txt
        filename=$(basename "$file" .txt)
        echo "   • $filename"
    done

    if [ "$JOB_COUNT" -gt 10 ]; then
        REMAINING=$((JOB_COUNT - 10))
        echo "   ... and $REMAINING more"
    fi

    echo ""
    echo "================================================================"
    echo "📄 Sample Job Preview"
    echo "================================================================"
    echo ""

    # Show first job details
    FIRST_JOB=$(ls -1 "$OUTPUT_DIR" | head -1)
    if [ -n "$FIRST_JOB" ]; then
        echo -e "${BLUE}File: $FIRST_JOB${NC}"
        echo ""
        # Show first 30 lines of the first job
        head -30 "$OUTPUT_DIR/$FIRST_JOB"

        # Check if there's more content
        LINE_COUNT=$(wc -l < "$OUTPUT_DIR/$FIRST_JOB")
        if [ "$LINE_COUNT" -gt 30 ]; then
            REMAINING_LINES=$((LINE_COUNT - 30))
            echo ""
            echo "   ... ($REMAINING_LINES more lines)"
        fi
    fi
fi

echo ""
echo "================================================================"
echo "📊 Statistics"
echo "================================================================"

# Show processed jobs count
if [ -f "data/processed_jobs.json" ]; then
    PROCESSED_COUNT=$(python -c "import json; print(len(json.load(open('data/processed_jobs.json'))))" 2>/dev/null || echo "0")
    echo "   Total processed jobs (all time): $PROCESSED_COUNT"
fi

# Show today's stats
echo "   New jobs today: $JOB_COUNT"
echo "   Output directory: $OUTPUT_DIR"

echo ""
echo "================================================================"
echo "💡 Next Steps"
echo "================================================================"
echo ""
echo "1. Review jobs:"
echo -e "   ${BLUE}cat $OUTPUT_DIR/*.txt${NC}"
echo ""
echo "2. View specific job:"
echo -e "   ${BLUE}cat '$OUTPUT_DIR/[filename].txt'${NC}"
echo ""
echo "3. Clear processed jobs (to see all jobs again):"
echo -e "   ${BLUE}rm data/processed_jobs.json${NC}"
echo ""
echo "4. Adjust search criteria:"
echo -e "   ${BLUE}code config/search-criteria-complex.yaml${NC}"
echo ""
echo "5. Re-run search:"
echo -e "   ${BLUE}./scripts/my_daily_search.sh${NC}"
echo ""

# Summary message
if [ "$JOB_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✅ Daily search complete! Found $JOB_COUNT new job(s).${NC}"
else
    echo -e "${YELLOW}⚠️  No new jobs today. Consider adjusting your search criteria.${NC}"
fi

echo ""
