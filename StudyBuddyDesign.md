# StudyBuddy Design System (Pre-Finals)

## 1. Primary Rule: "Loud Background, Quiet Foreground"
To balance academic professionalism with modern gamification, StudyBuddy uses a highly vibrant "Aurora Mesh" background paired with heavily blurred, stark white "Frosted Glass" UI components. 
- **The Foreground:** Must remain clean, monochromatic (black/white/slate), and use the primary brand green sparingly for actions. No random colorful gradients on text or icons.
- **The Background:** Must provide all the visual energy. 

## 2. Core Design Tokens (CSS Variables)

**Brand & Typography:**
- `--sb-primary`: `#00895a` (StudyBuddy Green - used for buttons, links, and active states)
- `--sb-primary-hover`: `#00704a`
- `--sb-ink`: `#0f172a` (Deep Slate - used for all primary headings and text)
- `--sb-muted`: `#475569` (Used for paragraphs and secondary text)
- `--sb-canvas`: `#f8fafc` (Off-white base behind the aurora mesh)

**Aurora Mesh (The "Loud" Background):**
These colors are exclusively used as heavily blurred (`filter: blur(140px)`), large circular blobs (`mix-blend-mode: multiply`) in the absolute background.
- **Emerald:** `rgba(16, 185, 129, 0.5)`
- **Sky Blue:** `rgba(14, 165, 233, 0.45)`
- **Deep Violet:** `rgba(139, 92, 246, 0.4)`

## 3. Layout & Architecture Rules

- **Absolute Backgrounds:** Background meshes must use `position: absolute` with `width: 100%` and `height: 100%` relative to the document (NOT `100vh` or `fixed`) to prevent harsh cutoff lines when scrolling in Vue Router.
- **Split-Screen Layouts:** Use `.sb-split` (a 2-column CSS Grid) for hero sections and feature highlights. Left side for text, right side for SVG Clipart.
- **Anti-Density:** Ensure generous padding (e.g., `padding: 100px 0` for sections) to prevent the "Decision Fatigue" noted by the thesis panel.

## 4. Component Standards: "Frosted Glass"

**Glass Panels (Cards & Navbars):**
Instead of solid white backgrounds, use heavily blurred translucency so the Aurora Mesh subtly bleeds through.
- **Light Panels:** `background: rgba(255, 255, 255, 0.6)` with `backdrop-filter: blur(24px)` and a crisp `border: 1px solid rgba(255, 255, 255, 0.9)`.
- **Dark Panels:** `background: rgba(15, 23, 42, 0.7)` with `backdrop-filter: blur(24px)` and `border-top: 1px solid rgba(255,255,255,0.1)`.

**Buttons & Actions:**
- Primary CTAs use a solid `--sb-primary` background with a subtle drop shadow: `box-shadow: 0 4px 15px rgba(0, 137, 90, 0.3)`.
- Hover states must utilize spring-physics lifts: `transform: translateY(-3px)`.

## 5. Iconography & Graphics
- **No Stock Photos:** Avoid generic stock images of real people.
- **SVG Clipart:** Use dependency-free, inline SVG illustrations. 
- **Clipart Wrapper:** Wrap SVGs in a `.sb-image-wrapper` glass container (max-width ~380px) to keep them constrained and professional. Apply a scale effect on hover (`transform: scale(1.1) translateY(-10px)`).

## 6. Motion & Interaction (Gamification)
- **Spring Physics:** All hover transitions and entrance animations must use a smooth deceleration curve: `cubic-bezier(0.16, 1, 0.3, 1)`.
- **Card Hover (`.interactive-card`):** Cards lift (`translateY(-6px)`), their glass becomes more opaque (`background: rgba(255,255,255,0.9)`), and a green border highlight appears at the bottom.
- **Accordion Toggles:** The "+" icon must physically rotate 45 degrees (`transform: rotate(45deg)`) and fill with green when opened.

## 7. Thesis Panel Logic Proofs
Every design element must reflect actual backend capability:
- **OTP/Verification:** Visually represented by the "CPU Verified Only" badges.
- **Hybrid Recommender:** Visually represented by the "Step 02: Match and Book" flow.
- **Wallet/Ledger:** Visually represented by the "Tutor Earnings/Reports" feature cards.