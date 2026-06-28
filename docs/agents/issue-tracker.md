# Issue tracker: GitHub

Issues and PRDs for this repo live as GitHub issues (`llariesalinas/studybuddy-ui`). Use the `gh`
CLI for all operations.

## Conventions

- **Create an issue**: `gh issue create --title "..." --body "..."`. Use a heredoc for multi-line bodies.
- **Read an issue**: `gh issue view <number> --comments`, filtering comments by `jq` and also fetching labels.
- **List issues**: `gh issue list --state open --json number,title,body,labels,comments --jq '[.[] | {number, title, body, labels: [.labels[].name], comments: [.comments[].body]}]'` with appropriate `--label` and `--state` filters.
- **Comment on an issue**: `gh issue comment <number> --body "..."`
- **Apply / remove labels**: `gh issue edit <number> --add-label "..."` / `--remove-label "..."`
- **Close**: `gh issue close <number> --comment "..."`

Infer the repo from `git remote -v` — `gh` does this automatically when run inside a clone.

## Pull requests as a triage surface

**PRs as a request surface: no.** This is not a project taking outside contributions, so `/triage`
only ever processes issues, never PRs.

## Integration with docs/plans/

This repo already runs a documentation workflow independent of these skills (see `AGENTS.md` →
Documentation, and the root `CLAUDE.md`): every confirmed plan is saved as its own file in
`docs/plans/YYYY-MM-DD-<topic>.md` (from `docs/plans/_template.md`), tracked with frontmatter
`status` (`Draft → Approved → In Progress → Blocked → Done`), logged as a row in
`docs/plans/README.md`, and reflected in the `docs/plans/index.html` dashboard. **GitHub Issues do
not replace this — they sit alongside it.** The plan doc is the design record; the GitHub issue is
the work-tracking record. Keep both in sync:

- **When `/to-prd` produces a PRD**: write it to `docs/plans/YYYY-MM-DD-<topic>.md` first, following
  the existing template and frontmatter conventions, with `status: Draft` (or `Approved` if already
  confirmed in conversation). Then create the GitHub issue with a body that links to that file path
  and add the GitHub issue number/URL back into the plan doc's frontmatter or an early line (e.g.
  `issue: <url>`). Add a row to `docs/plans/README.md` and regenerate `docs/plans/index.html`.
- **When `/to-issues` splits a PRD into sub-issues**: each created GitHub issue references the
  parent plan doc's path, since the issues are implementation slices of one design document, not
  separate designs.
- **When an issue moves through triage labels or implementation**: update the plan doc's `status`
  field to match (`ready-for-agent` ≈ `Approved`/`In Progress`, issue closed ≈ `Done`), and
  regenerate `docs/plans/index.html`. On completion, write the session summary in
  `docs/session-summaries/` as this project's conventions already require — don't skip that step
  just because a GitHub issue also got closed.
- **Never let the two drift**: if a plan doc's status and its linked issue's state disagree, fix
  the stale one rather than ignoring the mismatch.

## When a skill says "publish to the issue tracker"

Create a GitHub issue, after (or together with) writing/updating the corresponding `docs/plans/`
file as described above.

## When a skill says "fetch the relevant ticket"

Run `gh issue view <number> --comments`. If the issue body links to a `docs/plans/` file, read that
too — it has the full design context the issue body only summarizes.
