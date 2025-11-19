# Best job search APIs for automated pipelines in 2024-2025

**JSearch and Adzuna emerge as top choices** for building automated job search pipelines under $50/month, while several major platforms (Indeed, LinkedIn, Glassdoor) have deprecated or never offered public job search APIs. For US market coverage including Austin, TX and remote positions, **JSearch provides the most comprehensive data** at $10-50/month, while **Adzuna offers excellent free access** for testing and moderate usage. Remote-focused applications should combine free APIs like Remotive and RemoteOK for maximum coverage.

The landscape reveals a critical divide: traditional job boards have largely closed public API access, forcing developers toward newer aggregator services or scraping-based solutions. Only 7 of 12 investigated APIs provide legitimate programmatic access, with half of those being free or under $20/month. This research identifies which APIs actually work, their true costs, and optimal strategies for different use cases.

## The viable options: APIs that actually work

### JSearch (via RapidAPI): Most comprehensive paid option

**Status:** Active and well-maintained through 2025, provided by OpenWeb Ninja with strong customer support and Discord community.

**Pricing that fits your budget:** JSearch offers the best value proposition with tiers from $10-50/month providing 10,000-50,000 requests monthly. The free tier includes 50 trial requests over 7 days. Overage costs just $0.0032487 per additional request. No long-term commitments required, cancel anytime. Volume discounts available by contacting OpenWeb Ninja directly.

**Rate limits scale with needs:** Average 20 requests per second on paid tiers, with the provider stating they "support any rate you may require" for custom arrangements. Returns up to 500 job listings per query with full pagination support. Response times average 1-3 seconds, making it suitable for real-time applications.

**Simple API key authentication** via RapidAPI marketplace. Register, subscribe to a plan, and receive immediate access. Same key works across OpenWeb Ninja's API suite if you subscribe to multiple services.

**Exceptional US and remote coverage:** Sources data from Google for Jobs, the largest job aggregator globally, which pulls from LinkedIn, Indeed, Glassdoor, ZipRecruiter, Monster, Dice, and dozens more. This provides comprehensive Austin, TX coverage and excellent remote job filtering with explicit `job_is_remote` boolean field.

**Industry-leading 40+ data points per job** make JSearch the richest data source available. Core fields include job_title, employer_name (plus logo, website, LinkedIn, company_type), full job_description, and job_apply_link with apply_quality_score. Location data provides city, state, country, latitude, and longitude. **Salary transparency** includes min/max/currency/period when available. The API returns explicit remote designation, posting timestamps in both Unix and UTC datetime formats, expiration dates, required experience objects, required education objects, required skills arrays, and job_highlights with separate Qualifications and Responsibilities arrays. Additional metadata includes benefits, employment_type, publisher source, Google link, ONET SOC codes, and NAICS codes.

**Three main endpoints** handle all use cases: `/search` for queries with extensive filtering (remote status, job type, date posted, location radius), `/job-details` for complete information on specific positions using job_id, and `/estimated-salary` for compensation research by title and location.

**Key limitations to consider:** The 500 job maximum per query requires pagination or query subdivision for exhaustive searches. Requires RapidAPI marketplace account, adding a layer of complexity. Free tier extremely limited at 50 total requests. Must contact provider for custom high-volume plans exceeding standard tiers.

**Perfect for daily automation** with multiple successful implementations reported. RESTful design with clean JSON responses, reliable infrastructure with high uptime, fast response times, strong documentation with code samples, active community support via Discord, and filtering options that reduce unnecessary requests. Easily handles scheduled daily searches with moderate volume (under 10,000 requests/month stays well under $50).

### Adzuna: Best free option for testing and moderate use

**Status:** Actively maintained through 2025 with GitHub projects showing updates through April 2025 and API documentation modified July 2024.

**Completely free with registration** at developer.adzuna.com providing instant app_id and app_key. Includes 14-day commercial trial period. No query limits mentioned for basic users complying with terms. For production commercial use beyond trial, contact Adzuna to negotiate custom terms. Rate limits can be increased for commercial relationships, with documentation noting "biggest API users do millions of hits per day" for enterprise implementations.

**Authentication uses simple API key** approach requiring both app_id and app_key in every request as URL parameters. Registration provides keys immediately with no approval process.

**Strong US market coverage** across all 50 states with confirmed robust Austin, TX presence (search results showed 2,486+ active Austin jobs). Aggregates from multiple US job boards including major national boards and direct employer postings. Supports remote position filtering and provides 2+ billion job advertisements globally serving 15M+ monthly jobseekers.

**Comprehensive structured data** includes job title, company (via company.display_name), full location object with area array plus latitude/longitude, salary_min and salary_max with salary_is_predicted flag, complete job description, job category, contract type (permanent, full_time, part-time, contract), created timestamp, unique job ID, and redirect URL for applications. Remote type not explicitly separated in response but can be inferred from description and location data.

**RESTful API with multiple endpoints:** Job search at `/v1/api/jobs/{country}/search/{page}` accepts parameters for keywords (what), location (where), salary range, employment type, results per page, and sorting. Additional endpoints provide historical salary data, salary distribution histograms, regional vacancy data, top hiring companies, and job category listings. Supports JSON (default), JSONP, XML, HTML, and XLSX response formats.

**Notable constraints** include the 14-day trial limitation for organizational/commercial use requiring licensing agreements beyond trial period. Rate limits not transparently published on documentation. Commercial use requires written consent and proper attribution ("Adzuna API" link required on implementations). Cannot contact third-party content providers directly. Geographic coverage limited to 16 supported countries.

**Excellent for daily automation** with RESTful design built for programmatic access, no hard daily limits for compliant users, real-time data updates, stable API (version 1 maintained consistently for years), good documentation with interactive endpoint testing, and clean JSON parsing. Multiple developers report successful automated job board implementations.

### USAJobs: Free government jobs API

**Status:** Active government-maintained API with Drupal module updated July 2024, confirming ongoing functionality through developer.usajobs.gov.

**Completely free** with no usage fees, paid tiers, or costs. Simply register for API key through the access request form. Intended for public use to promote federal job opportunities.

**Rate limits not explicitly documented** in public documentation, though API reserves right to create limits "at any time with or without notice." Returns up to 250 jobs per page with 5,000 maximum results per search query. Government APIs typically offer generous limits for legitimate use.

**Dual-header authentication** requires both Authorization-Key (your API key) and User-Agent (your email) in HTTP headers for each request. Keys provided after submitting application through developer portal, no credit card required.

**Limited to US federal government positions exclusively.** This is the critical constraint - covers all US states and territories including Austin, TX federal positions, but excludes private sector jobs, state/local government (non-federal), most international positions except federal overseas postings, and contract positions unless federally employed. This makes it unsuitable for general job search but excellent for federal employment focus.

**Comprehensive federal job data** includes PositionTitle, OrganizationName, AgencySubElement, PositionID, ControlNumber, JobSummary (description), QualificationSummary (requirements), PositionLocation with multiple locations per posting, PositionRemuneration with SalaryMin/SalaryMax/SalaryBasis, PayPlan/Series/Grade information, StartDate/EndDate for application windows, PublicationStartDate, ApplicationCloseDate, WorkSchedule (Full-Time/Part-Time), WorkType (Permanent/Temporary/etc.), JobCategory, WhoMayApply eligibility criteria, ApplyOnlineURL, and PositionURI. Remote type not explicitly tracked as separate field.

**Three main endpoints:** Search Jobs at `/api/Search` with extensive parameters (Keyword, LocationName, Organization, Series, Grade, PayGradeHigh/Low, WhoMayApply, DatePosted, JobCategoryCode), Historic JOAs at `/api/HistoricJoa` for bulk historical announcements, and Announcement Text retrieval for specific posting details. Max 250 results per page with pagination support.

**Suitable for specialized federal job automation** with RESTful design, free operation, stable government-maintained service, clean JSON responses, ability to handle daily automated queries, good documentation, and no rate limit concerns for reasonable use. However, unsuitable for general job search platforms needing comprehensive US market coverage including Austin, TX private sector positions.

### The Muse: Free curated career-focused jobs

**Status:** Active with public API v2 operational at themuse.com/developers/api/v2, no deprecation notices found in 2024-2025.

**Free tier with generous limits:** Without API key, 500 requests per hour. With free API key registration, 3,600 requests per hour (60 per minute). No paid tiers exist - completely free to use. No minimum commitments or usage fees.

**Rate limit transparency** via response headers showing X-RateLimit-Remaining to track quota. Registration at themuse.com/developers increases limits tenfold and is recommended for production use.

**Optional API key authentication** passed as query parameter (?api_key=YOUR_KEY). API functions without key but with lower rate limits. Simple registration process with immediate access.

**Strong US job market support** with excellent coverage including Austin, TX area and remote positions. Location filtering available for major US cities and regions. Supports worldwide locations but maintains primary US market focus.

**Curated job data** includes job title, company name and ID, company profile URL on The Muse, locations array with multiple location objects, categories (job categories), levels (Entry Level, Mid Level, Senior, Internship), tags for skills and attributes, publication date, job description (both short and full versions), references array with application URLs, and landing page URL on The Muse. Additional endpoints provide detailed company profiles with culture information and photos, team member profiles, and career advice articles.

**Main jobs endpoint** at `/api/public/jobs` accepts pagination (page number), api_key, category filter, level filter, location filter, and company name/ID filter. Returns JSON with page metadata (page number, page_count for total pages, and results array with 20 job objects per page). Similar pagination structure for companies and other endpoints.

**Quality over quantity approach:** Smaller dataset compared to major aggregators, with curated listings from quality employers vetted by The Muse editorial team. Focus on career development and company culture with profiles including photos and detailed culture information. Mix of startups and established companies with regular updates but smaller volume than massive aggregators. **Notable absence of salary data** in API responses.

**Limitations include** maximum 20 results per page requiring pagination for larger searches, recent API endpoint URL change (old api-v2.themuse.com redirects to www.themuse.com/api/public), focus on "career development" jobs rather than comprehensive coverage, and cap of 3,600 requests per hour even with API key.

**Moderate suitability for daily automation** with free access and reasonable limits (3,600/hour sufficient for daily scans), stable API with clear documentation, US market coverage including Austin, TX remote roles, and 20 results per page manageable with pagination. Best used for quality over quantity job searches with company culture focus as supplementary source alongside broader aggregators.

### Remotive: Free remote-first jobs with curation

**Status:** Actively maintained remote job API, domain updated to remotive.com with GitHub documentation regularly updated through 2025.

**Two-tier approach:** Public/free API requires no registration or API key, is completely free for unlimited reasonable use, but includes **24-hour delay** on job postings to ensure attribution to Remotive. Private/paid API available by contacting hello@remotive.com offers real-time data without delay and undisclosed pricing (likely under $50/month based on market positioning but requires quote).

**Strict rate limits on public API:** Maximum 2 requests per minute with hard block if exceeded. Recommended usage is 4 times per day maximum since data doesn't update frequently enough to justify more requests. No API key means no per-user tracking on public tier.

**No authentication required** for public API - direct GET requests to endpoint with open access. Private API uses undisclosed authentication method requiring direct contact for implementation details.

**Excellent US remote coverage** as a remote-first job board specifically designed for remote work. Global remote job coverage with strong US presence. Filter by location requirements including "Worldwide," "US Only," "Americas," or specific regions. Ideal for US remote positions and location-flexible Austin, TX searches.

**Comprehensive remote-specific data** includes unique Remotive ID, job listing detail URL on Remotive, job title, company name and logo URL, category (e.g., "Software Development"), job_type for employment type (full_time/contract/part_time/freelance/internship) though often not filled, publication_date in ISO 8601 format, candidate_required_location for geographic restrictions, salary description in optional field usually showing USD range, and full HTML job description.

**Simple API design** with main endpoint at `/api/remote-jobs` accepting optional category filter (name or slug like "software-dev"), company_name filter (case insensitive partial match), search parameter for title and description (case insensitive), and limit for number of results. Categories endpoint at `/api/remote-jobs/categories` lists available filters. Response includes legal notice, job count, and jobs array.

**Strong data quality** with 2,000+ active remote jobs on public board and 35,000+ jobs in premium "Accelerator" tier. Focus on quality remote positions curated and categorized by Remotive team since 2014. Regular updates multiple times daily with strong tech/software development focus. Data delayed 24 hours in public API, real-time in private API.

**Important terms of service restrictions:** Must link back to job URL on Remotive with DIRECT link (no redirects), must mention Remotive as source, cannot submit jobs to third-party sites (Jooble, Neuvoo, Google Jobs, LinkedIn Jobs), cannot collect signups/emails to show listings, and API access can be terminated for violations. Maximum 2 requests per minute blocks if exceeded, and job_type field often not populated.

**Excellent for daily automated remote job searches** with free and reliable access, purpose-built for remote jobs perfect for remote position searches, US market well-represented, 24-hour delay acceptable for daily scans (not real-time trading anyway), 4 requests per day guideline working perfectly for daily automation, no authentication complexity, and clean JSON API. Must comply with strict ToS attribution requirements and cannot use for commercial job aggregation without permission.

### RemoteOK: Largest free remote jobs database

**Status:** Active official JSON API created by @levelsio (Pieter Levels), actively maintained with jobs updated constantly through 2025.

**Completely free** with no API key required, no registration needed, no paid tiers, no rate limits publicly disclosed, and no costs whatsoever. Most accessible API in the market.

**No official rate limits published,** with API designed for reasonable public use and legal terms suggesting respectful usage expected. Community reports indicate no strict enforcement. No authentication means no per-user tracking or throttling.

**No authentication required** - public JSON endpoint accessible via direct HTTP GET requests without API key or registration. Add optional `?api=1` parameter to force JSON response.

**Excellent global remote coverage** claiming to be the #1 remote job board with 50,000+ remote job listings. Global coverage with strong US representation claiming to cover "80% of remote jobs on the web." All positions are remote by definition, making it ideal for US remote positions and location-flexible work.

**Rich job data despite simple API** includes slug (job URL slug), unique job ID, epoch (Unix timestamp of posting), date (ISO 8601 formatted), company name and logo URL when available, position (job title), tags array (skills, job type, technologies), extensive HTML job description, location (often empty for remote-only), apply_url on RemoteOK, salary_min/salary_max when available in USD, direct RemoteOK job listing URL, alternative logo field, and special flags including `original` and `verified` for verified postings.

**Massive dataset with frequent updates:** 50,000+ remote job listings updated claim with new jobs added daily/hourly. Mix of original postings and aggregated content from startups to major tech companies. Strong tech/developer focus across engineering, design, marketing, sales, support, and operations roles. Includes **24-hour data delay** similar to Remotive for attribution purposes, with verified jobs marked separately.

**Single comprehensive endpoint** at `https://remoteok.com/api` (or remoteok.io) returns JSON array starting with legal notice object followed by all job objects. Tag filtering available via URL structure: `https://remoteok.com/remote-{tag}-jobs` (example: `https://remoteok.com/remote-python-jobs`). Force JSON with optional `?api=1` parameter.

**Important legal terms in API response:** Must link back to Remote OK with follow (no nofollow), must mention Remote OK as source, cannot use Remote OK logo without permission, should credit Remote OK for traffic, and API access can be suspended for violations. Additional constraints include 24-hour delay on job postings, no official documentation page (just JSON endpoint), no filtering via query parameters (must parse full dataset client-side), large response size (all jobs returned at once), no pagination available, company logo URLs sometimes empty, and salary fields often null/empty.

**Perfect for comprehensive daily remote job scanning** with completely free access and no authentication barriers, simple JSON endpoint, massive 50,000+ job dataset, remote-first focus perfect for remote work, strong US coverage, frequent updates, no rate limits enabling easy automation, and 24-hour delay acceptable for daily scans. Must comply with ToS attribution/linking requirements. Large payload requires downloading all jobs and filtering client-side with no built-in search/filter parameters. Multiple third-party scrapers exist (Apify, Browse.ai) confirming endpoint stability.

## APIs that don't work: What to avoid

### Reed API: UK only, not suitable for US

**Geographic fatal flaw:** Reed.co.uk API is exclusively UK-focused serving the UK job market with all documentation examples using UK locations (London, Manchester, Stoke-on-Trent) and salary data in GBP. While Reed has US operations (Reed Global USA), the developer API is UK-specific with no US job coverage, making it completely unsuitable for Austin, TX area searches or US market in general.

Free with registration providing 1,000 requests per day for Job Seeker API and 2,000 requests per hour for Recruiter API (customizable). API key authentication via Basic Auth with simple registration at reed.co.uk/developers. Returns comprehensive job data including job ID, employer name, job title, location, salary range in GBP, expiration date, posting date, HTML job description, application count, and job URL. Large UK database from major UK recruitment platform with real-time data and professional quality.

**Verdict: Not suitable for US-based job searches.** Excellent for UK market but wrong geographic region for Austin, TX or US remote positions.

### LinkedIn API: No public job search access

**Critical limitation: No public job search API exists.** LinkedIn's official "Job Posting API" is exclusively for POSTING jobs, not searching or retrieving them. Requires LinkedIn Partner Program approval which is extremely difficult to obtain with most applications rejected. As of January 2025, LinkedIn is "not accepting new partnerships for LinkedIn's Job Posting API."

**Prohibitively expensive if somehow approved:** Profile API costs $59+/month minimum, Company Profile API $699+/month, Marketing Developer Platform estimated at $7,200+/year. No public pricing - all costs negotiated individually with enterprise agreements or advertising spend commitments required.

**Third-party scraping alternatives exist but risky:** RapidAPI providers offer LinkedIn Job Search APIs at $25-50/month for 20,000 requests/month. Apify LinkedIn Jobs Scraper charges ~$3 per 1,000 jobs scraped. ScrapFly and Fresh LinkedIn Scraper offer similar services. However, LinkedIn actively blocks scraping with anti-bot protections, these scrapers violate Terms of Service, may break without warning when LinkedIn changes structure, create legal/compliance risk, and risk account blocking if LinkedIn detects automated patterns.

These third-party services can technically retrieve excellent data (job title, company, location, remote type, salary on ~30% of listings, description, requirements, posting date, URL, company logo, applicant count, experience level, employment type, industries) from LinkedIn's 2+ million jobs per week, but reliability concerns and legal risks make this approach problematic for production systems.

**Verdict: Not suitable.** No official API makes this legally and technically problematic despite having excellent job coverage.

### Indeed API: Deprecated for job search

**Job Search API officially deprecated** and unavailable for new integrations since 2020. Publisher Jobs API (Get Job API) also deprecated. What remains is the Sponsored Jobs API, which is for MANAGING paid job campaigns, not searching for jobs.

**Sponsored Jobs API pricing makes it unsuitable:** Charges $3 USD per API call (as of December 2024 in US, November 2025 in EU) with minimum spending requirement of campaign spend in last 3 months. If you make 1,000 API calls per month, you must spend $3,000 on sponsored campaigns. This is exclusively for employers managing their own sponsored campaigns, not for job search applications.

Indeed platform still has excellent coverage with 250+ million unique visitors monthly and 10+ jobs added per second, but this cannot be accessed programmatically for job search purposes. The deprecated API used to return job title, company, location, description, posting date, URL, and salary when available, with 25 results per API call maximum, but this endpoint no longer works for new integrations.

**Verdict: Completely unsuitable.** API does not exist for job search purposes. Must use third-party aggregators or web scraping instead.

### AngelList/Wellfound API: No public API exists

**No public API available for job search.** AngelList Talent rebranded to Wellfound in November 2022. Platform is active and well-maintained with 130,000+ startup jobs, over 2 million candidates, and 35,000+ recruiting companies, but no public API for job search exists. Integration capabilities limited to ATS system partnerships (Greenhouse, Workable, Lever) using proprietary APIs not accessible to public. These integrations sync jobs FROM your ATS TO Wellfound, not searching Wellfound's database.

Platform pricing for employers ranges from free Access tier (post jobs, review applicants) to Essentials at $149/month to Promoted Jobs from $200 to custom RecruiterCloud enterprise pricing. Third-party scraping options include Apify Wellfound Jobs Scraper at ~$3 per 1,000 jobs, Bright Data enterprise pricing, ScrapFly credit-based, and Piloterr API private endpoint requiring approval.

Despite no API, platform has excellent coverage for startup ecosystem with strong Austin, TX tech hub presence, prominent remote position filtering, 130,000+ global jobs focused on startups and early-stage companies. **Unique feature: salary AND equity shown upfront** on ~80%+ of listings, with comprehensive data including company funding stage, size, culture, founders information. Best for software engineering, product, design, and startup roles, less comprehensive for traditional corporate jobs.

**Verdict: Not suitable.** No official API forces reliance on fragile scraping solutions with legal/compliance concerns despite excellent startup job coverage.

### Glassdoor API: Deprecated since 2021

**Public API closed in 2021.** Glassdoor shut down public access to their official API and is no longer available for general developers or individual job seekers. Employers can request access through partnership arrangements, but no public availability exists.

Third-party alternatives like OpenWeb Ninja Real-Time Glassdoor Data API via RapidAPI charge $0.002-0.004 per request with response times of 0.5-4 seconds. However, Glassdoor was never designed as comprehensive job search API - primarily a company review platform with job listings as secondary feature.

Historical API returned company information (name, ID, ratings), company reviews and ratings, salary information, CEO ratings, and culture ratings with limited job listing data. This made it unsuitable for job search automation focused on finding positions rather than researching companies.

**Verdict: Not suitable.** Official API unavailable; was never designed for comprehensive job search anyway. Third-party scraping expensive and unreliable for job search purposes.

## Additional APIs worth considering

### SerpApi (Google Jobs): Premium comprehensive option

**Status:** Active and well-maintained service scraping Google for Jobs, which aggregates from all major job boards.

**Pricing at budget limit:** Free tier provides 100 searches/month. Starter plan at $50/month offers 5,000 searches, sitting exactly at your budget threshold. Pro jumps to $150/month for 20,000 searches. No hard rate limit on requests per second, only monthly quota constraints.

**Excellent data coverage** sourcing from Google for Jobs, the most comprehensive aggregator covering worldwide jobs including strong US and Austin, TX presence. Returns job title, company name, location, full description, detected extensions (date posted, job type), multiple apply options from different sources, salary when available, related jobs, job highlights, and schedule/benefits/qualifications extensions.

**Simple API key authentication** with endpoints at `/search?engine=google_jobs` for job search and `/search?engine=google_jobs_listing` for individual job details. Returns full SERP data with structured job results in clean JSON format.

**Monthly search quotas** limit usage, and as a scraping service rather than direct job board API, there's indirect access to source data. However, provides most comprehensive coverage available since Google for Jobs aggregates virtually all major boards.

**Verdict: Excellent for comprehensive coverage** if you can allocate full $50/month budget to single API. Starter plan's 5,000 monthly searches translates to ~165 searches per day, sufficient for focused automated daily scanning.

## Recommended strategies by use case

### For comprehensive US market including Austin, TX

**Primary recommendation: JSearch at $10-30/month** provides best balance of coverage, data quality, and cost. Sources from Google for Jobs aggregating all major boards. 40+ data points per job including explicit remote designation, comprehensive salary data, and rich metadata. 10,000-50,000 monthly requests sufficient for robust daily automation. Real-time data with 1-3 second response times.

**Budget alternative: Adzuna free tier** offers excellent US coverage with no cost during 14-day trial. Provides comprehensive data with salary information and real-time updates. Must negotiate commercial terms for production use beyond trial, but no hard limits for compliant usage. Good option for testing and building proof-of-concept before committing to paid service.

**Maximum budget option: SerpApi at $50/month** provides most comprehensive coverage via Google for Jobs scraping. 5,000 monthly searches (~165/day) sufficient for daily automated scanning. Higher cost but maximum data coverage and quality.

### For remote job focus

**Optimal free combination: RemoteOK + Remotive** provides comprehensive remote job coverage at zero cost. RemoteOK offers 50,000+ remote listings with no rate limits and simple JSON endpoint returning all jobs. Remotive adds 2,000+ curated remote positions with 4 requests/day guideline. Combined coverage captures vast majority of US remote jobs.

**Both APIs require attribution** (linking back to source) and have 24-hour data delays, but these constraints work perfectly for daily automated scanning. No authentication complexity, clean JSON responses, and stable endpoints make automation straightforward.

**For real-time remote data: Remotive private API** available by contacting hello@remotive.com for pricing (likely under $50/month). Eliminates 24-hour delay if real-time data essential for your use case.

### For federal government jobs

**USAJobs API exclusively** with completely free access, no rate limits for reasonable use, comprehensive federal job data, and stable government-maintained service. Only suitable if your focus is federal employment. Must be combined with other APIs if you need private sector coverage alongside federal positions.

### For startup/tech company jobs

**Challenge: No good API option exists.** Wellfound/AngelList has best startup job coverage (130,000+ positions with unique salary/equity transparency) but no public API. Options limited to third-party scrapers like Apify ($3 per 1,000 jobs) with reliability and legal concerns, or supplementing broader APIs with startup-specific filtering.

**Practical approach: Use JSearch or SerpApi** with filtering for startup-related keywords, company size, and tech job categories. Less comprehensive for startup-specific data (funding stage, equity) but more reliable than scraping solutions.

### For quality over quantity with company culture

**The Muse API free tier** provides 3,600 requests/hour with API key registration. Curated listings from vetted employers with focus on company culture and career development. Good supplementary source alongside broader aggregators for candidates prioritizing culture fit. Mix of startups and established companies with detailed company profiles. No salary data in API responses limits usefulness for compensation-focused searches.

## Multi-API aggregation strategy

For maximum coverage under $50/month total budget, combine multiple free APIs:

**Core free stack:**
- **Adzuna** (general US jobs, free tier)
- **RemoteOK** (50,000+ remote jobs, free)
- **Remotive** (2,000+ curated remote jobs, free)
- **The Muse** (curated quality jobs, free)
- **USAJobs** (federal jobs, free)

This combination provides comprehensive coverage across general job boards, remote-first positions, curated opportunities, and federal employment at zero cost. Requires managing multiple API integrations and deduplicating results, but maximizes data coverage within budget.

**Paid alternative: Single comprehensive API**
- **JSearch at $10-30/month** provides comparable coverage to free stack with single integration point, consistent data structure, real-time updates without delays, and 40+ standardized fields per job. Simpler architecture with one API client, one authentication method, and one data schema. Worth cost premium for reduced complexity.

## Critical implementation considerations

**Authentication approaches vary widely:** JSearch requires RapidAPI marketplace account with API key. Adzuna uses dual app_id and app_key system. USAJobs requires both Authorization-Key header and User-Agent email. RemoteOK and RemoteOK require no authentication. The Muse offers optional API key for higher limits. Plan for flexible authentication handler supporting multiple methods.

**Rate limit management essential:** RemoteOK and RemoteOK have no strict limits but expect reasonable use. Remotive strictly enforces 2 requests/minute with blocking. The Muse provides 3,600 requests/hour with key. JSearch offers 20 requests/second on paid tiers. Adzuna has undisclosed limits but allows millions daily for large users. USAJobs has unpublished limits expecting reasonable usage. Implement per-API rate limiters with appropriate backoff strategies.

**Data delay considerations:** RemoteOK and Remotive introduce 24-hour delays on free public APIs, acceptable for daily automation but not real-time applications. JSearch, Adzuna, SerpApi, The Muse, and USAJobs provide real-time or near-real-time data. Consider data freshness requirements when selecting APIs.

**Legal compliance and attribution:** RemoteOK requires linking back with follow links and source attribution. Remotive prohibits resyndicating to third-party sites (Google Jobs, LinkedIn Jobs) and requires direct linking. Adzuna requires attribution link. The Muse has standard terms of service. Always review and comply with each API's terms of service to avoid access termination.

**Data normalization challenge:** Each API returns different field names and structures. Job titles appear as `job_title`, `PositionTitle`, `title`, or `position` depending on API. Salary data formats vary from separate min/max fields to single range strings to structured objects. Remote status exists as explicit boolean (`job_is_remote`), location-based inference, or description parsing. Implement robust data normalization layer mapping all APIs to consistent internal schema.

## What to avoid and why

**Never attempt to use:** LinkedIn API (no public access), Indeed API (deprecated for job search), Glassdoor API (deprecated), or Wellfound API (doesn't exist) for job search automation. These platforms either shut down public APIs or never offered them. Third-party scraping services exist but create legal risks, reliability concerns, and Terms of Service violations.

**UK-focused Reed API unsuitable** for US market despite being free and well-documented. Geographic mismatch makes it irrelevant for Austin, TX or US remote positions. Only use if you need UK job market coverage.

**Avoid building custom scrapers** for major job boards. Legal and compliance risks high, development and maintenance costs exceed API fees, anti-bot protections constantly evolving break scrapers, IP blocking and rate limiting common, and scraped data quality inferior to structured API responses. Only scrape as last resort for platforms with no alternatives.

**Be cautious with third-party scraping APIs** marketed as "LinkedIn API" or "Indeed API" on RapidAPI marketplace. These violate platform Terms of Service, may break without warning when target sites change, create legal liability for your application, typically more expensive than legitimate APIs, and have reliability issues. Use legitimate aggregators instead.

## Technical architecture recommendations

**Start simple with single API:** Begin implementation with either JSearch (paid, comprehensive) or Adzuna (free, testing). Validate data quality, test automation workflows, and build core application features before adding complexity of multi-API aggregation.

**Design for multi-API from start:** Even if starting with one API, architect system with abstraction layer supporting multiple providers. Define internal job schema, create API adapter interface, implement per-API concrete adapters, build unified job deduplication, and design normalized data models. This enables adding APIs later without refactoring core application.

**Implement robust error handling:** APIs may experience downtime, rate limit exhaustion, authentication failures, or response schema changes. Build resilient system with retry logic with exponential backoff, graceful degradation when APIs unavailable, comprehensive logging for debugging, health monitoring per API endpoint, and automatic failover to backup APIs when possible.

**Deduplication strategy essential:** When using multiple APIs, same job appears in multiple sources. Deduplicate based on company name + job title + location similarity matching, posting date comparison (keep newest), URL normalization and comparison, and fuzzy matching algorithms (Levenshtein distance). Merge data from multiple sources for richer job profiles when same position detected.

**Optimize request patterns:** Minimize API costs and respect rate limits by implementing request caching with appropriate TTL (24 hours for Remotive/RemoteOK given data delays), incremental updates using date filters fetching only new/updated jobs, pagination management fetching only needed pages, and smart filtering using API query parameters to reduce response sizes and processing overhead.

**Monitor costs actively:** Track API usage per provider, monitor approaching quota limits, alert on unusual usage patterns, project monthly costs based on current trends, and plan for overage fees or tier upgrades before hitting limits unexpectedly.

## Final recommendations for your use case

Based on your requirements for US market with Austin, TX and remote positions, under $50/month budget, and structured data for automated pipeline:

**Best single solution: JSearch at $20-30/month tier** provides comprehensive coverage from Google for Jobs aggregating all major boards, 40+ data points including explicit remote designation and salary data, 20,000-30,000 monthly requests sufficient for robust daily automation, real-time data without delays, simple integration via RapidAPI, excellent documentation and support, and proven reliability with many successful implementations.

**Best free solution: Adzuna during 14-day trial, then evaluate commercial terms.** Offers comprehensive US coverage including Austin, TX, real-time data with salary information, generous free tier for testing, established platform with good reliability, and simple API key authentication. Must contact for commercial licensing beyond trial period, but provides excellent free testing period to validate approach before committing to costs.

**Best remote-focused solution: RemoteOK + Remotive free combination** provides 50,000+ total remote jobs at zero cost, no authentication complexity, stable APIs with years of operation, acceptable 24-hour delays for daily scanning, and complementary coverage (RemoteOK breadth, Remotive curation). Requires managing two integrations and complying with attribution requirements but unbeatable for pure remote job focus on zero budget.

**Best comprehensive free stack: Combine Adzuna + RemoteOK + Remotive + The Muse + USAJobs** for maximum coverage at zero cost during testing phases. Provides general jobs (Adzuna), remote jobs (RemoteOK, Remotive), curated opportunities (The Muse), and federal positions (USAJobs). More complex to implement and maintain but maximizes data coverage when budget is absolute constraint.

For your specific use case of automated daily searches returning structured data for Austin, TX area and remote positions, **JSearch at the $20-30/month tier offers the best balance** of comprehensive coverage, data quality, ease of implementation, and cost effectiveness. The 40+ data points per job, explicit remote designation, real-time updates, and aggregation from Google for Jobs make it the most complete solution available under your $50 budget constraint.