---
status: accepted
---

# Protected demo environment on Vercel, Render, and Supabase

StudyBuddy will use a three-part hosting split for the demo-first rollout:

- Vercel for the Vue frontend
- Render for the Django backend and any needed worker process
- Supabase for PostgreSQL

The demo environment will be protected rather than public, and it will run from the `develop`
branch. Feature branches merge into `develop`, `develop` auto-deploys to the protected demo
environment, and `main` stays reserved for production promotion later. Production will use the
same stack, but with separate environment variables, separate database resources, and a stricter
release gate.

This keeps the deployment model simple for the team while still giving us a realistic staging
surface:

- demo traffic exercises the real cloud stack
- test data stays isolated from production data
- PayMongo can stay on sandbox keys for the demo phase
- the later production switch becomes a controlled branch/env promotion instead of a rebuild of
  the architecture

Render is the chosen backend host because the app already needs a long-running Django process and
may need a worker process for async jobs. Supabase is the database host because the project already
uses PostgreSQL and wants a managed database that can be pointed at separate demo and production
instances cleanly.
