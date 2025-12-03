# Work Session Agenda - December 3, 2025 (Wednesday)

**Focus:** Phase 4 - Organization & Linear Integration
**Linear Issue:** [TT-49](https://linear.app/davidshaevel-dot-com/issue/TT-49)
**Branch:** `david/tt-49-organization-linear-integration`

---

## Session Goals

### Priority 1: Timestamped Evaluation Summaries

**Problem:** Running the pipeline multiple times per day overwrites `evaluation_summary.json`

**Solution:** Add timestamp to summary filename

**Implementation:**
```
jobs/pipeline/2025-12-03/
├── Apple_SRE_evaluation.json           # Individual (unchanged)
├── Visa_DevOps_evaluation.json         # Individual (unchanged)
├── evaluation_summary_083000.json      # Run at 8:30 AM
├── evaluation_summary_140000.json      # Run at 2:00 PM
└── evaluation_summary_180000.json      # Run at 6:00 PM
```

**Tasks:**
1. Update `EvaluationWriter.write_summary()` to include timestamp in filename
2. Format: `evaluation_summary_HHMMSS.json` (24-hour format)
3. Update tests to verify timestamped filenames
4. Document behavior in CLAUDE.md

### Priority 2: Folder Structure Manager

**Goal:** Organize jobs into logical folders based on status

**Structure:**
```
jobs/
├── active/              # Currently pursuing
│   └── {company_name}/
├── evaluating/          # Under evaluation
│   └── {week}/
│       └── {company_name}/
├── archived/            # Not pursuing or completed
│   └── {company_name}/
└── pipeline/            # Auto-discovered, pending review
    └── {date}/          # Current output location
```

**Tasks:**
1. Create `FolderManager` class in `src/organization/folder_manager.py`
2. Implement `move_to_active()`, `move_to_evaluating()`, `move_to_archived()`
3. Preserve evaluation history when moving files
4. Add CLI commands: `--organize`, `--archive {job_id}`

### Priority 3: Linear API Integration

**Goal:** Auto-create Linear issues for high-scoring opportunities

**Threshold:** Score ≥ 85 (B+ or higher) triggers auto-creation

**Tasks:**
1. Create `LinearClient` class in `src/integrations/linear/client.py`
2. Implement `create_issue()` with job details
3. Add `--create-issues` flag to main.py
4. Configure in `config/integrations.yaml`

---

## Implementation Order

| Order | Task | Estimated Time | Priority |
|-------|------|----------------|----------|
| 1 | Timestamped summaries | 30 min | HIGH |
| 2 | Folder structure manager | 2 hours | MEDIUM |
| 3 | Linear API integration | 2 hours | MEDIUM |
| 4 | Tests and documentation | 1 hour | HIGH |

---

## Files to Create/Modify

### New Files
- `src/organization/folder_manager.py` - Folder structure management
- `src/integrations/linear/client.py` - Linear API client
- `config/integrations.yaml` - Integration configuration
- `tests/test_folder_manager.py` - Folder manager tests
- `tests/test_linear_client.py` - Linear client tests

### Modified Files
- `src/organization/evaluation_writer.py` - Add timestamp to summary filename
- `src/main.py` - Add `--organize`, `--archive`, `--create-issues` flags
- `CLAUDE.md` - Document new features
- `README.md` - Update feature list

---

## Success Criteria

1. ✅ Multiple pipeline runs per day don't overwrite summaries
2. ✅ Jobs can be moved between folders (pipeline → evaluating → active/archived)
3. ✅ High-scoring jobs automatically create Linear issues
4. ✅ All tests pass (target: 70+ tests)
5. ✅ Documentation updated

---

## Pre-Session Checklist

- [ ] Pull latest from main
- [ ] Create branch `david/tt-49-organization-linear-integration`
- [ ] Verify LINEAR_API_KEY in .env
- [ ] Review TT-49 issue description

---

## Notes

**From Phase 3 Completion:**
- Current output: `jobs/pipeline/YYYY-MM-DD/` with individual evaluations
- Summary file: `evaluation_summary.json` (currently overwrites)
- Integration point: `SearchOrchestrator.run_search_with_evaluation()`

**Linear API:**
- MCP tools available: `mcp__linear-server__create_issue`
- Team: Team Tacocat
- Project: Job Search Pipeline Development

---

**Session Duration:** 4-6 hours
**Expected PRs:** 1-2 (depending on scope)
