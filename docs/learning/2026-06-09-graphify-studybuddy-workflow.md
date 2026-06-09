# Graphify Workflow for StudyBuddy

## Core model

Graphify has two extraction layers:

- AST extraction reads code structure locally with tree-sitter: functions, classes, imports, and calls. It is fast and does not use an LLM.
- Semantic extraction sends docs, papers, and media to an LLM to extract meaning. This is the expensive layer.

## Normal StudyBuddy flow

Run the full graph once from the StudyBuddy UI repo root:

```bash
/graphify .
```

After that, code changes should usually use the incremental path:

```bash
graphify update .
```

`graphify update .` compares current file hashes against `graphify-out/manifest.json`, re-runs AST extraction only for changed code, and patches `graphify-out/graph.json`. It does not call an LLM.

## Commits and hooks

If the Graphify post-commit hook is installed, day-to-day code changes are simple:

```bash
git commit
```

The hook runs `graphify update .` after the commit, so code changes stay current without LLM cost.

As of 2026-06-09, this repo did not have `.git/hooks/post-commit` installed. Until it is installed, run `graphify update .` manually when you want the graph refreshed after code changes, especially before querying the graph mid-work.

## Plan files in docs/plans

StudyBuddy creates plan markdown files in `docs/plans/` as work is planned and completed. Those files are documentation, not code, so they belong to the semantic layer.

Use this rule:

- If only code changed: use `graphify update .` or rely on the commit hook if installed.
- If new plan docs, summaries, PDFs, papers, or other non-code assets were added and you want them represented in graph meaning: run `/graphify .` again.
- Re-running `/graphify .` after new docs should use Graphify's semantic cache and process new or changed docs instead of redoing unchanged docs.

In practice: run `/graphify .` once, install the hook, commit normally for code, and re-run `/graphify .` only when documentation changes matter to future graph queries.
