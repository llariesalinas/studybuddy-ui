# Triage Labels

The skills speak in terms of five canonical triage roles. This file maps those roles to the actual
label strings used in this repo's issue tracker (GitHub Issues on `llariesalinas/studybuddy-ui`).

| Label in mattpocock/skills | Label in our tracker | Meaning                                  | Status              |
| --------------------------- | --------------------- | ----------------------------------------- | -------------------- |
| `needs-triage`              | `needs-triage`        | Maintainer needs to evaluate this issue   | create on first use  |
| `needs-info`                | `needs-info`          | Waiting on reporter for more information  | create on first use  |
| `ready-for-agent`           | `ready-for-agent`     | Fully specified, ready for an AFK agent   | create on first use  |
| `ready-for-human`           | `ready-for-human`     | Requires human implementation             | create on first use  |
| `wontfix`                   | `wontfix`              | Will not be actioned                      | already exists       |

When a skill mentions a role (e.g. "apply the AFK-ready triage label"), use the corresponding label
string from this table. The four `create on first use` labels don't exist on the repo yet — create
them with `gh label create <name>` the first time a skill needs to apply one, rather than failing.
