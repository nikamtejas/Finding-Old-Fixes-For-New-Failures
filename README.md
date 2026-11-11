# Finding-Old-Fixes-For-New-Failures

Real GitHub issue data from the Matter smart-home standard repository
[project-chip/connectedhomeip](https://github.com/project-chip/connectedhomeip).
This repository only collects data; no models are trained here.

## Everything is in one notebook: `matter_issues_pipeline.ipynb`

Run the cells from top to bottom (Shift+Enter) in VS Code or Jupyter, using the `.venv` Python.

| Section | What it does | Internet? |
|---|---|---|
| 1-3 | setup, token check, choose the download folder | yes (token check) |
| 4 | download all issues + pull requests (~20 min) | yes |
| 5 | download all comments of the repository (~2-3 h) | yes |
| 6 | find which pull request fixed each closed issue (GraphQL, timeline fallback) | yes |
| 7 | build the table: anonymise usernames, join comments, fix links, outcome, duplicates | no |
| 8 | save **one CSV file** with all issues and check that it reads back identically | no |
| 9-11 | summary counts, PDF overview, file locations | no |

Every download cell is **resumable**. If it stops, run the same cell again and it continues from the
last saved page. Data that is already downloaded is skipped. The notebook waits automatically when the
GitHub rate limit (5,000 requests per hour) runs low.

### Setup (once)

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
export GITHUB_TOKEN=...      # optional: otherwise the notebook asks for it in a hidden input box
```

The token is never printed or saved.

## Output

| File | Contents |
|---|---|
| `data/processed/matter_issues_full.csv` | **the dataset**: one row per issue, all columns below |
| `data/processed/overview.pdf` | short overview for readers |
| `data/raw/download_<date>/` | every raw API response (JSON), unchanged: `issues/`, `comments/`, `graphql/`, `timeline/`, `split/` |

### Columns of `matter_issues_full.csv`

`number, url, title, body, comments` (all comments, oldest first, marked with author ID and date),
`labels, state, state_reason, created_at, closed_at, days_to_close, comment_count, bot_comment_count,
author_id, fix_pr_numbers, fix_merged, link_source, outcome, duplicate_pair_with, duplicate_matched_text`

`outcome` is assigned in this order:
1. `unresolved`: the issue is open.
2. `duplicate`: closed as duplicate.
3. `rejected`: closed as not planned.
4. `success`: closed and linked to a merged PR.
5. `unclear`: closed, but no merged linked PR was found.

**Text is kept exactly as written on GitHub.** The only change is that usernames become IDs such as
`user_00042` / `bot_00007`, including `@mentions` of known accounts. The raw JSON keeps real names, so do not
share `data/raw/`.

**Excel note:** Excel shows at most 32,767 characters per cell, so long comment threads look cut off
*in Excel only*. The CSV itself is complete. Use `pd.read_csv(path, keep_default_na=False)` to load everything.

## Testing without the internet

`MATTER_DATA_DIR=/some/folder` makes the notebook read and write there instead of `data/`.
