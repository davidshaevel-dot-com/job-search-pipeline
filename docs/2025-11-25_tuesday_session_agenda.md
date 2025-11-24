# Session Agenda - Tuesday, November 25, 2025

**Project:** Job Search Pipeline Development
**Focus:** Phase 3 Planning and Preparation
**Linear Issue:** [TT-47](https://linear.app/davidshaevel-dot-com/issue/TT-47) - Phase 3: Multi-Board Support

---

## Session Overview

With Phase 2 (Deduplication & Filtering) now merged and complete, this session focuses on planning and preparing for Phase 3: Multi-Board Support.

**Previous Session Accomplishments (Nov 24):**
- Resolved all Gemini Round 2 code review issues (7 fixes)
- PR #4 merged to main
- Phase 2 complete

---

## Priorities

### 1. Phase 3 Planning (HIGH - 60 min)

**Goal:** Create detailed implementation plan for multi-board support

**Tasks:**
- [ ] Review Phase 3 requirements from PLAN.md
- [ ] Identify additional job boards to implement:
  - Adzuna (free tier available)
  - RemoteOK (completely free)
  - Remotive (completely free)
  - The Muse (free tier available)
  - USAJobs (completely free, government jobs)
- [ ] Design rate limiting strategy for multiple boards
- [ ] Plan parallel execution architecture
- [ ] Define success criteria for Phase 3

**Key Considerations:**
- Rate limiting per board (different APIs have different limits)
- Error handling for individual board failures
- Aggregation of results from multiple sources
- Configuration structure for multi-board settings

### 2. Board Adapter Research (MEDIUM - 45 min)

**Goal:** Research API requirements for each new board

**Tasks:**
- [ ] Adzuna API documentation review
- [ ] RemoteOK API documentation review
- [ ] Remotive API documentation review
- [ ] The Muse API documentation review
- [ ] USAJobs API documentation review
- [ ] Document authentication requirements for each
- [ ] Estimate implementation effort per board

### 3. Architecture Design (MEDIUM - 30 min)

**Goal:** Design multi-board orchestration

**Tasks:**
- [ ] Design adapter factory pattern
- [ ] Plan rate limiter implementation
- [ ] Design result aggregation strategy
- [ ] Plan configuration schema updates
- [ ] Consider async/parallel execution options

### 4. Linear Updates (LOW - 15 min)

**Goal:** Update Linear with Phase 3 planning details

**Tasks:**
- [ ] Update TT-47 with implementation plan
- [ ] Add sub-tasks for each board adapter
- [ ] Update project status
- [ ] Set estimated timeline

---

## Technical Notes

### Phase 3 Scope (from PLAN.md)

**Multi-Board Support includes:**
1. Additional job board adapters (beyond JSearch)
2. Rate limiting per API
3. Parallel execution with error handling
4. Result aggregation from multiple sources
5. Configuration for board-specific settings

### Board Priority Order

Based on API research documented in `docs/best-job-search-apis-for-automated-pipelines-in-2024-2025.md`:

1. **RemoteOK** - Completely free, no API key needed
2. **Remotive** - Completely free, no authentication
3. **USAJobs** - Free, requires API key registration
4. **Adzuna** - Free tier (50 requests/day)
5. **The Muse** - Free tier available

### Success Metrics for Phase 3

- [ ] At least 2 additional board adapters implemented
- [ ] Rate limiting prevents API quota exhaustion
- [ ] Failed board searches don't block other boards
- [ ] Aggregated results properly deduplicated (via Phase 2)
- [ ] Configuration allows enabling/disabling boards

---

## Files to Reference

- `PLAN.md` - Full implementation plan
- `docs/best-job-search-apis-for-automated-pipelines-in-2024-2025.md` - API research
- `src/adapters/jsearch.py` - Reference implementation for new adapters
- `src/adapters/base.py` - Base adapter interface
- `config/job-boards.yaml` - Board configuration

---

## Questions to Address

1. Should we implement all boards in Phase 3, or prioritize a subset?
2. What's the right balance between parallel and sequential execution?
3. How should we handle boards with significantly different data schemas?
4. Should rate limiting be global or per-board?
5. What's the minimum viable Phase 3 scope?

---

## End of Session Goals

By the end of this session:
1. Clear implementation plan for Phase 3
2. Board adapter priorities defined
3. Architecture decisions documented
4. Linear TT-47 updated with plan
5. Ready to begin Phase 3 implementation
