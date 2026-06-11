# Landing page redesign summary

Date: 2026-06-11
Plan: `docs/plans/2026-06-11-landing-page-redesign.md`
Reference artifact: `docs/artifacts/2026-06-11-landing-redesign-reference.html`

## Implemented

- Rebuilt `src/views/LandingPage.vue` around the approved Studio Motion artifact:
  hero, marquee, three panels, Platform tools, count strip, Common questions, CTA, and
  single-line footer.
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

## Verification

- `npx oxlint .` passed with 0 warnings/errors.
- `npx eslint . --cache --max-warnings=0` passed.
- `npm run build` passed.
- Browser checks on `http://127.0.0.1:5174/` confirmed all artifact sections render.
- Responsive text-fit audit at `360`, `390`, `768`, `900`, `1024`, and `1280` found no
  positive horizontal overflow and no clipped settled text.
- Performance guardrail scan found zero `backdrop-filter`/`filter: blur`, no animated
  gradients/background-position, and no per-frame root CSS variable writes in the landing
  component.

## Notes

- Browser console still reports pre-existing app-level warnings from `SupportModal` prop
  inheritance and the router guard's deprecated `next()` callback; no new landing-specific
  console errors were observed.
- `docs/plans/README.md` was not updated because it already contains unrelated in-flight
  status edits.

## Post-implementation design revision (pending port)

After this implementation shipped, the design review continued the same day and the
spec/artifact were revised: Platform tools became a **pinned horizontal rail** (white
banner slabs — serif numeral watermark | larger text | object-doodle illustration; the
page anchors while the rail rides sideways), the count strip became a full-width count
band, and the tools/FAQ stretch gained a generous-spacing pass. The shipped
`LandingPage.vue` still has the earlier flat 4-card tools grid; the port is tracked as
Step 8 of the plan, which is back to **In Progress**. This summary will be updated again
when the port lands.
