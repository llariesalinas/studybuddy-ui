# Landing Page Redesign Design Spec

Date: 2026-05-08
Surface: `src/views/LandingPage.vue`

## Direction

The StudyBuddy public landing page moves from a Bootstrap 5 marketing layout to a
self-contained Apple-inspired Tile Rhythm page. Tiles stack directly with no visual gaps and
alternate between white, dark green-black, and parchment surfaces. The experience is centered,
quiet, and product-like, with the StudyBuddy green replacing Apple's blue as the single accent.

## Locked Decisions

- Keep Bootstrap 5 available for authenticated views, but do not use Bootstrap classes on the
  landing page.
- Hand-port shadcn-inspired Button, Badge, Card, Avatar, and Accordion patterns as scoped CSS.
- Use no Tailwind and add no npm dependencies.
- Hero is centered, text-first, Apple-style, with no illustration.
- Add How it works, Testimonials, and FAQ sections.
- Use Vue state for the FAQ accordion with one open item at a time.

## Design Tokens

| Token                | Value     | Usage                                         |
| -------------------- | --------- | --------------------------------------------- |
| `--sb-primary`       | `#00895A` | Primary actions, stat numbers, avatars, links |
| `--sb-primary-hover` | `#00704A` | Primary button hover                          |
| `--sb-dark`          | `#0A1916` | Dark tiles                                    |
| `--sb-canvas`        | `#ffffff` | White tiles and card surfaces                 |
| `--sb-parchment`     | `#f5f5f7` | Parchment tiles                               |
| `--sb-ink`           | `#1d1d1f` | Main text                                     |
| `--sb-muted`         | `#6e6e73` | Muted text on light surfaces                  |
| `--sb-muted-dark`    | `#ababab` | Muted text on dark surfaces                   |
| `--sb-divider`       | `#f0f0f0` | Light borders and navbar edge                 |
| `--sb-green-tint`    | `#edf7f3` | Badges and soft icons                         |
| `--sb-green-border`  | `#b8dece` | Badge borders                                 |

Font stack:

```css
system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif
```

## Tile Order

1. Navbar: white, sticky, 52px tall, backdrop blur.
2. Hero: white, centered headline, CTA buttons, badge chips.
3. Stats strip: dark, four stats with green numbers.
4. How it works: parchment, three numbered steps.
5. Features: white, 2 by 2 shadcn-style utility cards.
6. Testimonials: dark, three quote cards with avatar initials.
7. FAQ: parchment, four-item accordion.
8. CTA: dark, centered headline, primary pill and dark outline button.
9. Footer: parchment, four-column link grid and legal line.

## Component Inventory

### Button

Primary pill buttons use `--sb-primary`, pill radius, medium weight, and active press scaling.
Secondary text-link buttons use a green underline on light surfaces. Dark outline buttons are used
on the CTA tile.

### Badge

Badges use a green tint background, green text, a soft green border, and a compact 11px label.
They appear in the hero as proof chips.

### Card

Utility cards use a white surface, subtle border, 18px radius, and hover shadow. Cards are used for
features and adapted for process/testimonial content.

### Avatar

Testimonials use circular initials avatars with the brand green background and white initials.

### Accordion

FAQ items use a shadcn-inspired accordion pattern driven by `openFaq`. Clicking an item toggles it;
clicking it again closes it. A plus/minus glyph reflects state and the answer panel transitions via
max height.

## Responsive Rules

- Below 768px, all content grids collapse to one column.
- Hero headline drops from 56px to 34px.
- Tile padding tightens while preserving the no-gap rhythm.
- Navbar keeps a compact single-row layout and wraps only if needed on very narrow screens.
