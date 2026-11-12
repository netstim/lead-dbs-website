# Analytics plan (coordinated branch)

Branch `analytics`, in `.claude/worktrees/analytics`, rebased onto PR #24's
`globe-timelapse`. Main checkout/manual work is excluded. STRATO access is
read-only; live deployment is the lab's decision. Push to the fork only; the
coordinating session opens the stacked PR.

1. Preserve #24's approved monthly download globe, lazy loading, all-country
   inclusion and `countries/months/total/from/to` contract.
2. Keep the reviewed access-import improvements (validation, independent tool
   counts, quality counters, private manifest, tests and clear labels).
3. Extend the existing download importer with a versioned category inventory,
   whole-data breakdown and auditable legacy selection heuristics. Avoid claims
   of verified bots or completed downloads.
4. Prepare a bounded first-party PHP collector, opt-in MATLAB helpers, private
   UTC aggregate archive, retention, backups, monitoring and lab instructions.
   No server writes or activated schedules from this task.
5. Validate the complete local chain and website; ask Opus 5.5 medium to review
   the expanded work and identify remaining implementable issues vs explicit
   lab-only production dependencies.
6. Resolve findings, commit only analytics changes, push fork/analytics and
   report branch, exact head and checks to the coordinating session.

See [analytics-completion.md](analytics-completion.md) for evidence and open
production dependencies. A code review does not turn an undeployed system into
an operational one.
