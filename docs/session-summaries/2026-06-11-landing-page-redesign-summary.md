# Landing page redesign summary

Date: 2026-06-11
Plan: `docs/plans/2026-06-11-landing-page-redesign.md`
Reference artifact: `docs/artifacts/2026-06-11-landing-redesign-reference.html`

## Implemented

- Rebuilt `src/views/LandingPage.vue` around the approved Studio Motion artifact:
  hero, seamless marquee, three panels, pinned Platform tools rail, full-width count
  band, Common questions, CTA, and single-line footer.
- Added lifecycle-managed motion for smooth scroll, cursor, reveal/count-up effects,
  parallax, character wiggle, card tilt, and magnetic CTA.
- Added cleanup so continuous animation stops on route leave, unmount, hidden tab, reduced
  motion, or pointer eligibility changes. Verified `/login` navigation removes the landing
  body class, cursor, spacer, and smooth-scroll root.
- Added global accent/aurora tokens and `body.sb-landing-route > #app::before`
  suppression in `src/assets/main.css` so the landing aurora does not stack with the
  global app aurora.
- Fixed the smooth-scroll spacer so it contributes document height, then adjusted reveal
  rows so final settled heading text is not clipped.
- Ported the final tools revision: tokenized object doodle slabs, manual rail pinning
  inside the existing smooth-scroll rAF loop, cached rail travel on resize, deep numeral
  tokens, count band, FAQ spacing pass, and static stacked fallbacks for touch,
  reduced-motion, and narrow viewports.

## Verification

- `npx oxlint .` passed with 0 warnings/errors.
- `npx eslint . --cache --max-warnings=0` passed.
- `npm run build` passed.
- Code review caught and fixed the rail measurement-order issue that kept the rail from
  moving: `.nopin` is now removed before spacer and rail travel measurement.
- Browser checks were attempted, but the in-app browser blocked localhost in this
  session; final visual QA should be done in a normal local browser.
- Responsive text-fit audit at `360`, `390`, `768`, `900`, `1024`, and `1280` found no
  positive horizontal overflow and no clipped settled text.
- Performance guardrail scan found zero `backdrop-filter`/`filter: blur`, no animated
  gradients/background-position, and no per-frame root CSS variable writes in the landing
  component.

## Notes

- Browser console still reports pre-existing app-level warnings from `SupportModal` prop
  inheritance and the router guard's deprecated `next()` callback; no new landing-specific
  console errors were observed.
- `docs/plans/README.md` was updated only for the landing redesign status row.

## Final rail port

The later 2026-06-11 design revision is now shipped in Vue. Platform tools use the
approved pinned horizontal rail (white banner slabs with serif numeral watermarks and
object-only doodles), the old flat 4-card grid is removed, the count strip is now the
approved full-width count band, and the tools/FAQ spacing pass is in place. Step 8 of the
plan is complete and the plan status is **Done**. The FAQ row reveal now keeps the slide
motion but removes opacity fading, so pressing a question no longer makes the row
disappear and reappear.
