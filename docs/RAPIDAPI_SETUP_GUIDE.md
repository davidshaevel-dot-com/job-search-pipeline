# RapidAPI Setup Guide - JSearch API

**Date:** November 21, 2025
**API:** JSearch (Google for Jobs aggregator)
**Free Tier:** 50 requests over 7 days

---

## Overview

This guide will walk you through:
1. Creating a RapidAPI account (2 minutes)
2. Subscribing to JSearch API free tier (3 minutes)
3. Getting your API key (1 minute)
4. Setting the environment variable (1 minute)
5. Verifying the setup (2 minutes)

**Total time:** ~10 minutes

---

## Step 1: Create RapidAPI Account (2 minutes)

### 1.1 Go to RapidAPI Website

Open your browser and navigate to:
```
https://rapidapi.com/
```

### 1.2 Sign Up

Click the **"Sign Up"** button in the top-right corner.

**Choose one of these options:**
- Sign up with Google (recommended - fastest)
- Sign up with GitHub
- Sign up with email

**If using email:**
- Enter your email address
- Create a password (at least 8 characters)
- Click "Sign Up"
- Check your email for verification link
- Click the verification link

### 1.3 Complete Profile (Optional)

You may be asked to:
- Choose your role (select "Developer")
- Indicate your experience level
- Skip any optional surveys

**✅ Checkpoint:** You should now be logged into RapidAPI dashboard

---

## Step 2: Subscribe to JSearch API (3 minutes)

### 2.1 Navigate to JSearch API

**Option A - Direct Link:**
```
https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch
```

**Option B - Search:**
1. Click the search bar at the top
2. Type "JSearch"
3. Click on "JSearch" by letscrape

### 2.2 Review API Details

You should see the JSearch API page with:
- API description: "Google for Jobs aggregator"
- Pricing tabs: Free, Basic, Pro, Ultra, Mega
- Code snippets on the right
- Endpoints on the left

### 2.3 Subscribe to Free Tier

1. Click the **"Pricing"** tab (next to Documentation)
2. You'll see the pricing plans:

   **Free Plan (Basic):**
   - ✅ **50 requests** over 7 days
   - ✅ Hard limit (no charges)
   - ✅ No credit card required
   - Rate limit: Varies by endpoint

3. Under the **"Basic"** plan, click **"Subscribe"**

4. A modal will appear:
   - Review: "50 Requests / 7 Days"
   - Confirm: "Subscribe to Free"
   - Click **"Subscribe"**

### 2.4 Confirm Subscription

You should see:
- ✅ Green checkmark or "Subscribed" badge
- Your quota: "0 / 50 requests used"
- Endpoints are now active

**✅ Checkpoint:** JSearch API is now subscribed and ready to use

---

## Step 3: Get Your API Key (1 minute)

### 3.1 View API Key

Your API key should be visible in the code snippets section on the right side of the page.

**Look for the code snippet that shows:**
```javascript
const options = {
  method: 'GET',
  headers: {
    'X-RapidAPI-Key': 'YOUR-API-KEY-HERE',  // ← This is your key
    'X-RapidAPI-Host': 'jsearch.p.rapidapi.com'
  }
};
```

### 3.2 Copy Your API Key

**Method 1 - From Code Snippet:**
1. Look at the `X-RapidAPI-Key` value
2. It will be a long string (32-64 characters)
3. Select and copy the entire key

**Method 2 - From Dashboard:**
1. Click your profile picture (top-right)
2. Select **"My Apps"** or **"App Dashboard"**
3. Click on "default-application"
4. Your API key will be displayed
5. Click the "Copy" button

**Your API key looks like:**
```
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```
(32-64 alphanumeric characters)

### 3.3 Keep Your Key Secure

⚠️ **IMPORTANT:**
- **DO NOT** share your API key publicly
- **DO NOT** commit it to GitHub
- **DO NOT** post it in screenshots or logs
- Store it securely (we'll use environment variable)

**✅ Checkpoint:** You have copied your RapidAPI key

---

## Step 4: Set Environment Variable (1 minute)

### 4.1 Set RAPIDAPI_KEY in Your Shell

Open your terminal and run:

```bash
# Navigate to project directory
cd /Users/dshaevel/workspace-ds/job-search-pipeline

# Activate virtual environment
source venv/bin/activate

# Set the environment variable (replace with your actual key)
export RAPIDAPI_KEY="your-actual-api-key-here"
```

**⚠️ Replace `your-actual-api-key-here` with the key you copied!**

### 4.2 Verify Environment Variable

```bash
# Check it's set (should show your key)
echo $RAPIDAPI_KEY
```

**Expected output:**
```
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

**If it shows nothing or an error:**
- Make sure you didn't include quotes incorrectly
- Try again: `export RAPIDAPI_KEY="your-key"`
- Check for typos

### 4.3 Make It Persistent (Optional)

**For current session only:**
- The `export` command works for current terminal session
- You'll need to re-run it each time you open a new terminal

**To make it permanent:**

Add to your shell configuration file:

```bash
# For Zsh (default on macOS)
echo 'export RAPIDAPI_KEY="your-actual-api-key-here"' >> ~/.zshrc
source ~/.zshrc

# OR for Bash
echo 'export RAPIDAPI_KEY="your-actual-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

**⚠️ Security Note:** Only do this if you're comfortable storing the key in your shell config. Otherwise, set it manually each session.

**✅ Checkpoint:** RAPIDAPI_KEY environment variable is set

---

## Step 5: Verify Setup (2 minutes)

### 5.1 Test Environment Variable in Python

Run this quick test:

```bash
python -c "import os; key = os.environ.get('RAPIDAPI_KEY'); print('✅ API key set!' if key else '❌ API key not set'); print(f'Key ends with: ...{key[-4:]}' if key else '')"
```

**Expected output:**
```
✅ API key set!
Key ends with: ...o5p6
```

### 5.2 Test API Connection (Optional)

Test a simple API call with curl:

```bash
curl --request GET \
  --url 'https://jsearch.p.rapidapi.com/search?query=DevOps&page=1&num_pages=1' \
  --header "X-RapidAPI-Host: jsearch.p.rapidapi.com" \
  --header "X-RapidAPI-Key: $RAPIDAPI_KEY"
```

**Expected response:**
- JSON response with job data
- Status: "OK"
- Array of jobs

**If you get an error:**
- 401 Unauthorized: API key is wrong
- 403 Forbidden: Not subscribed or quota exceeded
- 429 Too Many Requests: Rate limit exceeded

### 5.3 Check Your Quota

1. Go back to RapidAPI JSearch page
2. Look at the top-right for quota usage
3. Should show: "1 / 50" (if you ran the curl test)

**✅ Checkpoint:** API key verified and working!

---

## Troubleshooting

### Error: "X-RapidAPI-Key header is missing"

**Problem:** API key not set or not passed correctly

**Solutions:**
1. Verify environment variable: `echo $RAPIDAPI_KEY`
2. Re-set it: `export RAPIDAPI_KEY="your-key"`
3. Make sure you're in the same terminal session
4. Try restarting terminal and re-exporting

### Error: "401 Unauthorized"

**Problem:** Invalid API key

**Solutions:**
1. Copy the key again from RapidAPI dashboard
2. Check for extra spaces: `export RAPIDAPI_KEY="key"` (no spaces)
3. Verify you copied the entire key
4. Try regenerating the key in RapidAPI dashboard

### Error: "403 Forbidden"

**Problem:** Not subscribed or quota exceeded

**Solutions:**
1. Verify you're subscribed: Check JSearch page shows "Subscribed"
2. Check quota: Should be under 50 requests
3. If over quota, wait for 7-day reset or upgrade plan

### Error: "You have exceeded the rate limit"

**Problem:** Too many requests in short time

**Solutions:**
1. Wait a few seconds between requests
2. Free tier has rate limits (varies by endpoint)
3. Our code has rate limiting built-in (1 request/second default)

### Environment Variable Not Persisting

**Problem:** Variable disappears when you close terminal

**Solutions:**
1. Add to shell config (~/.zshrc or ~/.bashrc)
2. Or create a `.env` file (see next section)
3. Or set it each session manually

---

## Alternative: Using .env File

### Create .env File

```bash
# In project root
cd /Users/dshaevel/workspace-ds/job-search-pipeline

# Create .env file
cat > .env << 'EOF'
# RapidAPI Key for JSearch
RAPIDAPI_KEY="your-actual-api-key-here"
EOF
```

**⚠️ Replace `your-actual-api-key-here` with your key!**

### Load .env File

```bash
# Option 1: Export all variables from .env
export $(cat .env | xargs)

# Option 2: Use python-dotenv (recommended for production)
pip install python-dotenv
```

**Verify .env is in .gitignore:**
```bash
grep "^\.env$" .gitignore
```

Should show: `.env` (already in .gitignore ✅)

---

## Security Best Practices

### ✅ DO:
- Store keys in environment variables
- Use `.env` file (excluded from git)
- Store in shell config (~/.zshrc) for convenience
- Rotate keys periodically
- Use different keys for dev/prod

### ❌ DON'T:
- Commit keys to GitHub
- Share keys publicly
- Hardcode keys in source code
- Include keys in logs or screenshots
- Reuse keys across projects

---

## Next Steps

Now that your RapidAPI key is set up:

1. **Run the test script:**
   ```bash
   python scripts/test_jsearch_adapter.py
   ```

2. **Run the full pipeline:**
   ```bash
   python src/main.py
   ```

3. **Monitor your quota:**
   - Check RapidAPI dashboard
   - Free tier: 50 requests / 7 days
   - Used by test script: 1 request
   - Used by full pipeline: 1 request per search

---

## Summary

**Account Created:** ✅
- RapidAPI account at https://rapidapi.com/

**Subscription:** ✅
- JSearch API Free Tier (50 requests / 7 days)

**API Key:** ✅
- Copied from dashboard
- Set as RAPIDAPI_KEY environment variable

**Verification:** ✅
- Environment variable set
- Optional: API connection tested

**Ready for:** ✅
- Phase 1 testing
- Test script execution
- Full pipeline execution

---

**Setup Complete!** 🎉

You're now ready to test the Phase 1 implementation with real API calls.

**Next:** Run `python scripts/test_jsearch_adapter.py`

---

**Last Updated:** November 21, 2025
**API Documentation:** https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch/docs
**Support:** RapidAPI has 24/7 support via dashboard
