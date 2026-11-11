# NOTES

Findings, surprises and decisions, one entry per step.

## Step 1: Load and check (`src/01_load.py`)
- 14,698 issues × 20 columns, numbers unique, created 2020-03-03 to 2026-11-11; 12,205 closed, 2,493 open. All checks pass
  (close dates match state, `days_to_close` matches the dates). Saved `data/processed/issues_loaded.parquet` (15.7 MB).
- Empty text: 248 bodies, 4,158 issues without comments, 3,603 without labels. Text columns keep `""` and are not missing.
- Surprise: 97 open issues have `state_reason = reopened`, and 12,161 of 12,205 closed issues (99.6%) are just `completed`.
  The close reason tells us very little, so the outcome label must lean on fix links (`fix_merged`).
