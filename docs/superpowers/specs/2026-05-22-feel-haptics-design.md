# Feel & Haptics Interaction System — Design Spec
**Date:** 2026-05-22  
**Status:** Approved  
**Scope:** App-wide interaction primitives + Chat view wiring

---

## Overview

A CSS-first interaction layer that gives every interactive element in StudyBuddy a consistent physical "feel" — spring-physics lift on hover, scale-press on click, and animation feedback for async state changes. No new dependencies. Implemented as global utility classes and keyframes in `App.vue`, consumed by all views.

---

## 1. Timing & Easing Tokens

Added to the `:root` block in `App.vue` alongside existing color variables:

| Token | Value | Use |
|---|---|---|
| `--sb-spring` | `cubic-bezier(0.16, 1, 0.3, 1)` | Cards, panels, room switch — smooth deceleration |
| `--sb-spring-fast` | `cubic-bezier(0.34, 1.56, 0.64, 1)` | Buttons — slight overshoot for tactile feel |
| `--sb-t-quick` | `120ms` | Button press, hover in |
| `--sb-t-normal` | `250ms` | Cards, bubble entrance, room transition |

---

## 2. Utility Classes (global, `App.vue` non-scoped style)

### `.sb-btn`
Applied to every `<button>` in the app.

- **Hover:** `translateY(-3px)` + shadow deepens
- **Active/press:** `scale(0.96) translateY(0)` — snaps down instantly, springs back on release
- **Disabled:** `opacity: 0.4`, `pointer-events: none`
- **Transition:** `transform` + `box-shadow` + `background-color` all on `--sb-t-quick` with `--sb-spring-fast`

### `.sb-interactive`
Applied to cards, room rail rows, and any pressable surface.

- **Hover:** `translateY(-6px)` + shadow + glass opacity increases + green bottom border appears
- **Active:** `scale(0.98) translateY(0)`
- **Transition:** `--sb-t-normal` with `--sb-spring`

---

## 3. Keyframe Animations (global)

| Name | Trigger | Effect |
|---|---|---|
| `sb-bubble-in` | New message appended | Fade in + slide up 12px + scale from 0.94 → 1 |
| `sb-pulse-dot` | Pending message indicator | Green glow ring pulses outward repeatedly |
| `sb-pop` | Read receipt `is_read` flips true | Check icon scales 0.6→1.3→1 with opacity |
| `sb-shake` | Send failure / empty send attempt | Composer translates ±5px × 2 cycles, 400ms total |

---

## 4. Chat View Wiring

### Message bubbles
- `<TransitionGroup>` wraps the message list; entering nodes get `sb-bubble-in` (250ms, `--sb-spring`)
- Only **newly appended** messages animate — existing history renders statically on load
- Pending bubble: `opacity: 0.55` + `sb-pulse-dot` on the send-state indicator dot
- Read receipt icon: watches `message.is_read`; on `false → true` transition, adds `sb-pop` class for one cycle via `setTimeout` cleanup

### Input composer
- Send button gets `.sb-btn`
- On send failure or empty-submit: adds `.sb-shake` to the composer wrapper, removed after 420ms

### Room switch
- `<Transition>` keyed on `chatStore.currentRoom?.id`
- Enter: `opacity 0→1` + `translateX(16px → 0)` in 250ms with `--sb-spring`
- Rail rows get `.sb-interactive`; active row shows `--sb-primary` left border

### Unread badge pulse
- When `room.unread_count` increases (watched), badge briefly plays `sb-pulse-dot` once (non-repeating, 600ms)

---

## 5. Files Changed

| File | Change |
|---|---|
| `src/App.vue` | Add timing tokens + `.sb-btn` + `.sb-interactive` + 4 keyframes to non-scoped `<style>` |
| `src/views/Chat.vue` | Wire `<TransitionGroup>` on messages, `<Transition>` on room switch, `.sb-btn` on send button, shake logic on error |

No other files change. No new dependencies.

---

## 6. What Was Validated

All four interaction patterns were reviewed live in the visual companion browser demo:
- Button press states (hover lift, scale press, disabled)
- Card/surface hover (lift, glass opacity, green border)
- Message bubble entrance + pending pulse + read receipt pop
- Room switch slide-in + send button spring + composer error shake

User confirmed: **"yep these checks out"**
