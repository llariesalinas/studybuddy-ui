---
title: Dashboard card stability
date: 2026-06-07
status: Done
spec:
---

# Dashboard card stability

## Goal

Make the tutee dashboard's weekly session cards and recommended tutor cards keep a
stable visual height even when subjects or tutor metadata are long.

## Approach

Keep this as a frontend-only pass in `src/views/Dashboard.vue`. Summarize long tutor
subject lists in the component, keep the full list available through a title tooltip,
and clamp fixed-height session/tutor cards so long text cannot stretch the layout.

## Steps

1. Add tutor metadata helpers for subject summaries and full tooltip text.
2. Replace the raw joined subject list in recommendation cards with the summary.
3. Remove dynamic weekly session card height and use a fixed-height card.
4. Clamp tutor names, tutor metadata, session times, session titles, and tutor names.
5. Keep day columns scrollable when fixed session cards exceed the visible height.

## Risks

- Some full subject names are hidden until hover, which is intentional for dashboard
  scanability.
- Mobile tutor cards need a taller fixed height because the rate pill stacks under
  the copy.

## Checks to run

- `npm run build`
- Open the tutee dashboard and verify long tutor subjects and long session titles do
  not stretch cards or overlap adjacent controls.
