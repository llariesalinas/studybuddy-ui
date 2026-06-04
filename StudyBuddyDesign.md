---
version: beta
name: StudyBuddy Design System
description: >
  Current StudyBuddy product design language: quiet foregrounds, StudyBuddy-green
  feedback, aurora glass depth, tactile haptics, and truthful academic data.
sources:
  - docs/superpowers/specs/2026-05-08-landing-redesign-design.md
  - docs/superpowers/specs/2026-05-22-feel-haptics-design.md
  - docs/superpowers/specs/2026-05-25-animation-system-design.md
  - docs/superpowers/specs/2026-05-25-tutee-profile-redesign.md
  - docs/superpowers/plans/2026-05-08-auth-pages-redesign.md
  - docs/superpowers/plans/2026-05-23-chat-message-redesign.md
  - docs/superpowers/plans/2026-05-23-sidebar-notification-badge.md
  - docs/superpowers/plans/2026-05-25-haptics-rollout.md
colors:
  surface: "#f5fbf4"
  surface-dim: "#d6dcd5"
  surface-bright: "#f5fbf4"
  surface-container-lowest: "#ffffff"
  surface-container-low: "#f0f5ee"
  surface-container: "#eaefe9"
  surface-container-high: "#e4eae3"
  surface-container-highest: "#dee4dd"
  on-surface: "#171d19"
  on-surface-variant: "#3e4942"
  inverse-surface: "#2c322e"
  inverse-on-surface: "#edf2ec"
  outline: "#6e7a71"
  outline-variant: "#bdcabf"
  surface-tint: "#006c46"
  primary: "#00895a"
  primary-deep: "#006a44"
  primary-hover: "#00704a"
  on-primary: "#ffffff"
  primary-container: "#008558"
  on-primary-container: "#f6fff6"
  inverse-primary: "#6fdba5"
  secondary-blue: "#006591"
  warning: "#946200"
  danger: "#9a3e3e"
  error: "#ba1a1a"
  ink: "#0f172a"
  muted: "#475569"
  canvas: "#f8fafc"
  background-soft: "#f5fbf4"
  parchment: "#f5f5f7"
  divider: "#f0f0f0"
  green-tint: "#edf7f3"
  green-border: "#b8dece"
  aurora-emerald: "rgba(16, 185, 129, 0.5)"
  aurora-sky: "rgba(14, 165, 233, 0.45)"
  aurora-violet: "rgba(139, 92, 246, 0.4)"
  aurora-emerald-soft: "rgba(16, 185, 129, 0.32)"
  aurora-sky-soft: "rgba(14, 165, 233, 0.18)"
  aurora-violet-soft: "rgba(139, 92, 246, 0.2)"
  glass-light: "rgba(255, 255, 255, 0.64)"
  glass-light-strong: "rgba(255, 255, 255, 0.86)"
  glass-dark: "rgba(15, 23, 42, 0.7)"
typography:
  default-stack: "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
  future-display-stack: "Hanken Grotesk, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
  future-body-stack: "Inter, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
  headline-xl:
    fontSize: "48px"
    fontWeight: "700"
    lineHeight: "1.2"
    letterSpacing: "0"
  headline-lg:
    fontSize: "32px"
    fontWeight: "600"
    lineHeight: "1.25"
    letterSpacing: "0"
  headline-lg-mobile:
    fontSize: "28px"
    fontWeight: "600"
    lineHeight: "1.3"
    letterSpacing: "0"
  headline-md:
    fontSize: "24px"
    fontWeight: "600"
    lineHeight: "1.4"
    letterSpacing: "0"
  body-lg:
    fontSize: "18px"
    fontWeight: "400"
    lineHeight: "1.6"
  body-md:
    fontSize: "16px"
    fontWeight: "400"
    lineHeight: "1.5"
  body-sm:
    fontSize: "14px"
    fontWeight: "400"
    lineHeight: "1.5"
  label-md:
    fontSize: "14px"
    fontWeight: "500"
    lineHeight: "1"
    letterSpacing: "0"
  label-sm:
    fontSize: "12px"
    fontWeight: "600"
    lineHeight: "1"
    letterSpacing: "0.04em"
rounded:
  sm: "0.25rem"
  default: "0.5rem"
  md: "0.75rem"
  lg: "1rem"
  xl: "1.5rem"
  full: "9999px"
spacing:
  unit: "8px"
  container-max: "1280px"
  gutter-desktop: "24px"
  gutter-mobile: "16px"
  margin-desktop: "48px"
  margin-mobile: "20px"
motion:
  spring: "cubic-bezier(0.16, 1, 0.3, 1)"
  spring-fast: "cubic-bezier(0.34, 1.56, 0.64, 1)"
  t-quick: "120ms"
  t-normal: "250ms"
  t-slow: "400ms"
patterns:
  public-tile-rhythm:
    usage: "Landing and public marketing surfaces"
    order: "white, dark, parchment, white, dark, parchment, dark, parchment"
  auth-shell:
    usage: "Login and Register"
    surface: "parchment page, white card, green icon badge"
  aurora-bento-dashboard:
    usage: "Authenticated dashboards and dense utility pages"
    background: >
      radial-gradient(circle at 0% 0%, rgba(16, 185, 129, 0.32), transparent 38%),
      radial-gradient(circle at 96% 6%, rgba(139, 92, 246, 0.2), transparent 36%),
      radial-gradient(circle at 88% 74%, rgba(14, 165, 233, 0.18), transparent 42%),
      linear-gradient(135deg, #f8fafc 0%, #f5fbf4 100%)
    foreground: "Frosted glass bento cards with real product data only"
---

# StudyBuddy Design System

This is the canonical design reference for StudyBuddy after the landing redesign,
auth redesign, haptics rollout, animation system expansion, chat polish, dashboard
calendar refinements, wallet/profile glass work, and toast migration.

StudyBuddy should feel academic, calm, and modern: a quiet foreground on top of a
softly energetic background, with tactile controls and truthful data.

## Core Principles

1. **Loud background, quiet foreground.** Use aurora mesh or parchment/canvas
   surfaces to create atmosphere. Keep foreground UI restrained, legible, and
   mostly monochrome with StudyBuddy green as the primary accent.
2. **Green means action, current state, or success.** Do not introduce random
   accent colors. Use blue, amber, and red only for semantic secondary, warning,
   and danger states.
3. **Glass-first depth.** Authenticated premium surfaces use frosted glass panels
   with blur, white borders, and soft shadows. Modals use stronger glass.
4. **Every button feels physical.** Buttons press down, cards lift, and async
   feedback uses the global haptics layer.
5. **Never animate history.** Only newly mounted or newly inserted UI should
   animate. Existing list content must not replay when filters or tabs change.
6. **No fake product claims.** Metrics, badges, progress rings, tips, and status
   labels must reflect real backend/store data.
7. **Use the existing stack.** Vue 3, Pinia, Bootstrap Icons, Bootstrap-compatible
   authenticated views, scoped CSS, no Tailwind, and no new npm dependencies
   unless explicitly approved.
8. **No emojis in product UI.** Use Bootstrap Icons, text labels, badges, and
   state color instead. Emojis are too casual and inconsistent for StudyBuddy's
   academic product tone.

## Implementation Boundaries

- Global tokens, haptic utilities, route transitions, modal animation, skeletons,
  and shared keyframes live in the non-scoped `<style>` block of `src/App.vue`.
- Route-specific layout and visual treatments live in each view's `<style scoped>`.
- Public and auth pages can be self-contained and avoid Bootstrap layout classes.
- Authenticated app pages can use Bootstrap utilities when they match the local
  pattern, but should still use StudyBuddy tokens, `.sb-btn`, and `.sb-interactive`.
- Use Bootstrap Icons. Do not add Material Symbols, new icon packages, Tailwind,
  or webfont dependencies without approval.
- Prefer modal dialogs for option-heavy or stateful actions. Do not add dropdowns
  as a default interaction pattern; use dropdowns only when the necessary function
  of the design truly requires compact inline selection or menu behavior.

## Color System

### Primary Product Tokens

```css
--sb-primary: #00895a;
--sb-primary-hover: #00704a;
--sb-primary-deep: #006a44;
--sb-secondary-blue: #006591;
--sb-warning: #946200;
--sb-danger: #9a3e3e;
--sb-ink: #0f172a;
--sb-muted: #475569;
--sb-canvas: #f8fafc;
--sb-background-soft: #f5fbf4;
```

### Material-Inspired Surface Tokens

Use these for larger neutral UI systems, especially admin/profile surfaces.

```css
--sb-surface: #f5fbf4;
--sb-surface-container-lowest: #ffffff;
--sb-surface-container-low: #f0f5ee;
--sb-surface-container: #eaefe9;
--sb-surface-container-high: #e4eae3;
--sb-surface-container-highest: #dee4dd;
--sb-on-surface: #171d19;
--sb-on-surface-variant: #3e4942;
--sb-outline: #6e7a71;
--sb-outline-variant: #bdcabf;
```

### Public Page Tokens

```css
--sb-dark: #0a1916;
--sb-parchment: #f5f5f7;
--sb-divider: #f0f0f0;
--sb-green-tint: #edf7f3;
--sb-green-border: #b8dece;
```

### Aurora And Glass

Use strong aurora values on public hero-scale surfaces. Use soft aurora values for
authenticated route shells.

```css
--sb-aurora-emerald: rgba(16, 185, 129, 0.5);
--sb-aurora-sky: rgba(14, 165, 233, 0.45);
--sb-aurora-violet: rgba(139, 92, 246, 0.4);
--sb-aurora-emerald-soft: rgba(16, 185, 129, 0.32);
--sb-aurora-sky-soft: rgba(14, 165, 233, 0.18);
--sb-aurora-violet-soft: rgba(139, 92, 246, 0.2);
--sb-glass-light: rgba(255, 255, 255, 0.64);
--sb-glass-light-strong: rgba(255, 255, 255, 0.86);
--sb-glass-dark: rgba(15, 23, 42, 0.7);
```

## Typography

Use the system stack by default:

```css
font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
```

The Google Stitch direction names Hanken Grotesk for display and Inter for body.
Treat those as a future type direction only. Do not import new fonts unless the
project explicitly approves the dependency.

Use fixed, responsive sizes. Do not scale font size with viewport width.

| Role | Size | Weight | Line Height |
|---|---:|---:|---:|
| Hero headline | 56px desktop, 34px mobile | 700 | 1.05-1.15 |
| Product headline XL | 48px | 700 | 1.2 |
| Section headline | 32-34px | 600 | 1.25 |
| Card/title headline | 20-24px | 600-800 | 1.3-1.4 |
| Body large | 18px | 400 | 1.6 |
| Body | 16px | 400 | 1.5 |
| UI body/card | 13-14px | 400-600 | 1.4-1.5 |
| Eyebrow/label | 11-12px | 700-900 | 1 |

Letter spacing should be `0` by default. Use small positive tracking only for
uppercase metadata labels.

## Layout Patterns

### Public Tile Rhythm

The landing page uses Apple-inspired tile rhythm: full-width sections stacked
directly with no visual gaps. The order is:

1. Sticky white navbar with backdrop blur and 52px minimum height.
2. White centered hero with headline, CTAs, and green proof chips.
3. Dark stats strip with StudyBuddy-green numbers.
4. Parchment "How it works" section.
5. White feature grid with shadcn-style utility cards.
6. Dark testimonials with initials avatars.
7. Parchment FAQ accordion.
8. Dark CTA.
9. Parchment footer.

Landing pages are text-first, centered, and product-like. Avoid generic stock
photos and busy illustrations.

### Auth Shell

Login and Register use `AuthShell.vue`:

- parchment page background
- top-left StudyBuddy brand/back link
- centered white auth card
- green-tinted icon badge
- scoped `sb-auth-*` form classes
- green focus rings
- red inline alert blocks for auth errors

Auth pages should not use Bootstrap layout/form classes. Preserve existing auth
logic and route behavior when restyling.

### Aurora Bento Dashboard

Use this for authenticated pages that need premium density, such as wallet and
profile surfaces. Apply it inside the route view only, not the shared app shell.

```css
.route-shell {
  position: relative;
  isolation: isolate;
  background:
    radial-gradient(circle at 0% 0%, rgba(16, 185, 129, 0.32), transparent 38%),
    radial-gradient(circle at 96% 6%, rgba(139, 92, 246, 0.2), transparent 36%),
    radial-gradient(circle at 88% 74%, rgba(14, 165, 233, 0.18), transparent 42%),
    linear-gradient(135deg, #f8fafc 0%, #f5fbf4 100%);
}
```

Bento layouts should use 2-column or 3-column CSS grids and collapse below
tablet widths. Avoid nested cards; use flat rows inside panels.

### Weekly Schedule Navigation

Weekly schedule controls should be compact and quiet:

- Previous/next week controls use icon buttons with `.sb-btn`.
- The date range pill is the temporal anchor.
- Remove extra jump CTAs unless the workflow truly needs them.
- When viewing the current week, the date pill uses a StudyBuddy-green animated
  outline and `aria-current="date"`.
- Clicking the date pill returns to the current week when the user has navigated
  elsewhere.
- Day-level "today" highlighting and week-level current highlighting are separate
  cues.

## Surfaces And Elevation

### Standard Glass Panel

```css
.glass-panel {
  background: rgba(255, 255, 255, 0.64);
  backdrop-filter: blur(24px);
  border: 1px solid rgba(255, 255, 255, 0.9);
  border-radius: 24px;
  box-shadow: 0 18px 60px rgba(15, 23, 42, 0.08);
}
```

### Strong Glass Modal

```css
.glass-modal {
  background: rgba(255, 255, 255, 0.86);
  backdrop-filter: blur(24px);
  border: 1px solid rgba(255, 255, 255, 0.9);
  border-radius: 24px;
  box-shadow: 0 24px 80px rgba(15, 23, 42, 0.18);
}
```

### High-Emphasis Action Card

Use a deep green gradient only inside a card or panel:

```css
background: linear-gradient(135deg, #006a44 0%, #00895a 100%);
```

Do not apply this gradient to the whole page or app shell.

## Core Components

### Buttons

Every action `<button>` and button-like `<router-link>` gets `.sb-btn`, except
Bootstrap `.btn-close`.

```css
.sb-btn {
  transition: transform var(--sb-t-quick) var(--sb-spring-fast),
              box-shadow var(--sb-t-quick) var(--sb-spring-fast),
              background-color var(--sb-t-quick) var(--sb-spring-fast);
  cursor: pointer;
}
```

- Hover: lift `translateY(-3px)` with deeper shadow.
- Press: `scale(0.96) translateY(0)`.
- Disabled: opacity `0.4`, no pointer events.
- Icon-only buttons should use familiar Bootstrap Icons and an `aria-label`.

### Interactive Surfaces

Clickable cards, rows, and panels get `.sb-interactive`.

- Hover: lift up to `translateY(-6px)`, increase glass opacity, show green border.
- Press: `scale(0.98) translateY(0)`.
- Do not override transforms ad hoc.

### Badges And Pills

Use green-tinted pills for proof chips, metadata, active filters, current week,
and non-critical status indicators.

```css
.sb-badge {
  background: #edf7f3;
  color: #00895a;
  border: 1px solid #b8dece;
  border-radius: 9999px;
  font-size: 11px;
  font-weight: 600;
  padding: 3px 10px;
}
```

Semantic badges:

- success/active/current: StudyBuddy green
- pending/warning: amber
- danger/rejected/failed: muted red
- neutral/inactive: slate

### Cards

Use cards for repeated content, compact panels, modals, and framed tools. Avoid
card-in-card page composition.

Public utility cards:

```css
.sb-card {
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 18px;
  padding: 28px;
  transition: box-shadow var(--sb-t-normal) var(--sb-spring),
              transform var(--sb-t-normal) var(--sb-spring);
}
```

### Forms

- Inputs use 12px radius, clear labels, and green focus rings.
- Disabled fields should explain why they are locked.
- Use inline field errors when the error belongs to one field.
- Use toast messages for global success/error feedback after actions.
- For profile selection controls, radio/checkbox cards may use a `selection-card`
  pattern where checked state turns the inner card green.
- Avoid dropdowns for complex choices, destructive actions, or workflows that need
  explanation. Use pop-up modals with clear labels, helper text, and explicit
  confirm/cancel actions.
- Use dropdowns only for simple native select cases or when compact menu behavior
  is required by the interaction itself.

### Accordions

Use one open item ref unless multiple open sections are explicitly needed.
Animate height with Vue `<Transition>` hooks and max-height/opacity transitions.
Accordion icons rotate and turn green when open.

### Step Progress

Use `SbStepBar.vue` for multi-step flows. It shows "Step X of Y", a percentage,
and a green animated fill. Do not use raw Bootstrap progress bars for these flows.

### Toasts

Browser `alert()` is not part of the StudyBuddy design system.

Use `src/stores/toast.js` and `src/components/SbToast.vue`:

```js
toastStore.push('Saved successfully')
toastStore.push('Please select a session date.', 'warning')
toastStore.push('Unable to save changes.', 'error')
```

Toasts are non-blocking, appear top-right, auto-dismiss after 3500ms, and can be
clicked to dismiss.

### Notifications

The sidebar notification badge mirrors the shared Pinia notifications store. It:

- appears for authenticated users
- hides when unread count is `0`
- caps display at `99+`
- does not create a broken `/notifications` route
- updates from the same store as the header bell

## Motion And Haptics

### Tokens

These tokens are global in `App.vue`:

```css
--sb-spring: cubic-bezier(0.16, 1, 0.3, 1);
--sb-spring-fast: cubic-bezier(0.34, 1.56, 0.64, 1);
--sb-t-quick: 120ms;
--sb-t-normal: 250ms;
--sb-t-slow: 400ms;
```

Never hardcode a new cubic-bezier when one of these applies.

### Global Keyframes And Utilities

| Name | Trigger | Behavior |
|---|---|---|
| `sb-bubble-in` | new chat message | fade/slide/scale in |
| `sb-pulse-dot` | pending/unread indicator | green glow pulse |
| `sb-pop` | read receipt or success icon | scale pop |
| `sb-shake` | invalid or failed send | short horizontal shake |
| `sb-stagger-in` | newly mounted stat/card group | fade/slide up |
| `sb-scale-in` | Bootstrap modal open | modal scales 0.94 to 1 |
| `sb-shimmer` | skeleton placeholder | loading shimmer |
| `sb-tab-indicator` | active filter/tab | underline grows from left |
| `sb-toast-in` | toast enters | top-right spring entrance |
| `sb-success-border` | confirmed success | green border pulse |

Use these utilities:

- `.sb-btn`
- `.sb-interactive`
- `.sb-stagger-item`
- `.sb-skeleton`
- `.sb-success-card`

### Route And Modal Motion

- Wrap route views with `<Transition name="page" mode="out-in">`.
- Sidebar/header/app shell must stay static while route content fades/slides.
- Bootstrap modals scale in globally with `sb-scale-in`.
- Respect `prefers-reduced-motion: reduce`; all animation and transition durations
  collapse to `1ms`.

### Animation Rules

- Entrance animation is for newly rendered nodes only.
- Never animate filtered history or existing rows on re-render.
- Do not animate aurora blobs continuously.
- Use foreground feedback, not background movement.

## Chat Design

Chat is status-aware and conversational, not just a text log.

- Date dividers separate message groups by day.
- Received messages show avatar circles.
- Message list uses `<TransitionGroup>` so only new messages animate.
- Pending send state uses reduced opacity and a pulse dot.
- Read receipts pop once when `is_read` flips true.
- Composer errors or empty sends shake briefly.
- Room switch uses a keyed `<Transition>` with a small horizontal slide.
- `ChatBanner.vue` renders role-aware booking states through `status_intent`.
- Booking banners must reflect real lifecycle states: pending, pending location,
  confirmed, awaiting payment, review pending, rejected, and cancelled.

## Dashboard And Data Components

### Stat Cards

Stat cards can use `sb-stagger-item` on mount with 70ms offsets. Do not count
numbers up artificially unless real product logic is added.

### Skeletons

Use `.sb-skeleton` for loading placeholders where custom shimmer would otherwise
be duplicated.

### Tab And Filter Pills

Active filter pills use a green underline animated by `sb-tab-indicator`. Existing
list rows must not replay entrance animation when a filter changes.

### Progress Rings

Use inline SVG rings only for real computed metrics. Clamp values to `0-100`.
Use primary green for the main ring and secondary blue for the secondary ring.

### Activity Rows

Rows use icon tile + title/body + metadata + amount/status. Use colors
semantically:

- green for credits, success, active
- red for deductions, failed, rejected
- amber for pending
- slate for neutral

### Sensitive Data

Mask account numbers as first 4 characters, bullet group, and last 3 characters.
Show active/inactive state with compact pills.

## Profile Pages

### Tutee Profile

Use the Aurora Bento glassmorphism profile layout:

- route-local aurora shell
- strong glass main card
- avatar with initials fallback or uploaded image
- hidden file input triggered by an Update Photo button
- two-column profile body on desktop, one column on mobile
- education-level-aware year selection
- course and preferred subjects as selection cards/pills
- email locked with helper affordance
- save/discard actions
- toast outcomes for save/avatar upload

Avatar upload rules:

- field name: `avatar`
- image files only
- max size: 5 MB
- show upload failure with toast

### Tutor Profile

Tutor profile accordions use height/opacity transition hooks. Subject bodies
expand smoothly and existing chevron state should remain intact.

## Payment And Booking Flows

- Multi-step progress uses `SbStepBar`.
- Payment confirmation and tutor verification use `showSuccess`, a `sb-pop`
  success icon, and `.sb-success-card` border pulse.
- All payment/booking validations use toast feedback, not blocking alerts.
- Multi-slot booking visuals must keep grouped payment/session state consistent
  with backend truth.

## Accessibility

- Icon-only buttons require `aria-label`.
- Current temporal state, such as the current week, should use `aria-current`
  where appropriate.
- Toasts use alert/live-region semantics.
- Buttons must be real `<button>` elements when they trigger actions.
- Disabled controls must use actual `disabled` attributes.
- Reduced-motion users get near-instant animations.
- Color is never the only state cue; combine color with text, shape, icon, border,
  or position.

## Coding Practices

- Preserve existing dirty work. If a file already has unrelated edits, make the
  smallest possible patch and do not commit unrelated changes.
- Keep route-level redesigns scoped to the route component. Do not alter `App.vue`,
  shared stores, router definitions, or backend APIs unless the feature requires it.
- Add global CSS only for shared primitives used across the app: tokens,
  keyframes, `.sb-btn`, `.sb-interactive`, route transitions, modals, skeletons,
  and toasts.
- Prefer existing local stores, services, and component patterns over new
  abstractions.
- For repeated app-wide behavior, create one reusable primitive instead of
  duplicating one-off CSS or JavaScript.
- Use real Vue state and computed properties for UI state. Avoid ad hoc DOM
  manipulation except for transition height hooks where Vue requires direct style
  control.
- Preserve existing business logic when redesigning a surface. Template and style
  rewrites should not change API payloads, routes, auth behavior, or store shape
  unless the task explicitly calls for it.
- Use `toastStore.push()` for feedback, not browser alerts. Use inline field
  errors for field-specific validation.
- Keep comments sparse and useful. Do not narrate obvious assignments.
- Favor targeted verification for touched files when repo-wide lint is noisy due
  to unrelated worktrees, backend vendor files, or pre-existing issues.

## Responsive Rules

- Collapse dashboard/profile/auth grids below tablet widths.
- Keep fixed-format UI stable with explicit dimensions, grid tracks, min/max
  widths, or aspect ratios.
- Avoid text overflow in buttons, pills, cards, and sidebars.
- Do not use viewport-width font scaling.
- Use 16px mobile gutters and 24px desktop gutters as a default baseline.

## Do Not Do

- Do not add decorative gradient blobs inside foreground cards.
- Do not animate aurora backgrounds continuously.
- Do not use browser `alert()`.
- Do not use emojis in UI copy, buttons, empty states, badges, or notifications.
- Do not use dropdowns as the default way to expose actions or settings. Prefer
  pop-up modals, radio cards, segmented controls, or explicit buttons unless a
  dropdown is functionally necessary.
- Do not add fake stats, streaks, discounts, or achievement metrics.
- Do not link to routes that do not exist.
- Do not introduce new dependencies for animation, icons, fonts, or utility CSS
  unless explicitly approved.
- Do not use Tailwind in this Vue/Vite app.
- Do not style page sections as nested floating cards.
- Do not overwrite shared shell behavior from route-level redesign work.

## Verification Checklist

For frontend changes, run the most relevant checks available:

- `npm run build`
- targeted `npx oxlint <files>`
- targeted `npx eslint <files>` when repo-level lint is noisy
- browser smoke checks for changed routes/components

If full `npm run lint` fails because it scans unrelated worktrees, backend vendor
files, or pre-existing issues, report that clearly and verify the touched files
directly.
