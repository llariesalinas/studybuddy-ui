# Feel & Haptics — App-wide Button & Card Wiring Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Apply `.sb-btn` to every action button and `.sb-interactive` to every clickable card surface across all 30+ Vue files, completing the haptics rollout started in the spec.

**Architecture:** The global CSS primitives (tokens, `.sb-btn`, `.sb-interactive`, all 4 keyframes) already live in `App.vue`'s non-scoped `<style>`. Chat.vue is also fully wired. This plan is a mechanical class-addition pass across the remaining 30+ views and components — no new CSS, no new logic, no new files.

**Tech Stack:** Vue 3 (Composition API), class-based Bootstrap 5 buttons, Vite dev server (`npm run dev` → http://localhost:5173)

---

## Rules (read before every task)

| Rule | Detail |
|---|---|
| **Add `.sb-btn`** | Every `<button>` that is an action/submit/nav button. |
| **Skip `btn-close`** | Bootstrap `class="btn-close"` dismiss × icons — no sb-btn. |
| **Router-link btns** | `<router-link class="btn ...">` also gets `.sb-btn`. |
| **Add `.sb-interactive`** | Clickable card/row surfaces (div, li, tr with @click). NOT modal backdrop divs. |
| **Never remove** | Do not remove existing classes; only append. |
| **Commit per task** | Each task ends with a commit. |

---

## Already Complete — Do Not Re-touch

- `src/App.vue` — global CSS (tokens + `.sb-btn` + `.sb-interactive` + 4 keyframes)
- `src/views/Chat.vue` — fully wired (TransitionGroup, room-switch, shake, pop, pulse, send btn, room items)
- `src/views/LandingPage.vue` — already has sb-btn throughout
- `src/views/Login.vue` — already has sb-btn
- `src/views/Register.vue` — already has sb-btn

---

## File Map

| Task | Files touched |
|---|---|
| 1 | App.vue (2 router-link header btns) |
| 2 | PreferenceSetup.vue, TutorPreferenceSetup.vue |
| 3 | ChatBanner.vue, BookingDatePicker.vue, BookingTimePicker.vue, NotificationBell.vue, RatingReminderBanner.vue, RatingStackModal.vue |
| 4 | Dashboard.vue |
| 5 | TuteeSessions.vue, TuteeProfile.vue |
| 6 | TuteeSessionDetails.vue, TuteeSessionDetailsFlow.vue |
| 7 | FindTutors.vue, TutorDetails.vue, InitialBooking.vue |
| 8 | BookingDetails.vue, PaymentScreenTutee.vue, PostSessionPaymentView.vue |
| 9 | TutorDashboard.vue, TutorProfile.vue |
| 10 | TutorSchedule.vue |
| 11 | TutorRequestedSessions.vue, TutorBookingDetailsFlow.vue, TutorPaymentScreen.vue |
| 12 | SessionsReports.vue, TutorSessionsReports.vue, TutorWallet.vue |
| 13 | AdminDashboard.vue, AdminInstitutions.vue, AdminReports.vue, AdminUsers.vue, AdminWithdrawals.vue |

---

## Task 1 — App.vue header router-link buttons

**Files:**
- Modify: `src/App.vue:229` and `src/App.vue:233`

- [x] **Add `sb-btn` to the two header action router-links**
- [x] **Commit**

---

## Task 2 — Auth / Setup Views

- [x] **PreferenceSetup.vue** — add `sb-btn` to the 3 action buttons.
- [x] **TutorPreferenceSetup.vue** — add `sb-btn` to the submit button.
- [x] **Commit**

---

## Task 3 — Shared Components

- [x] **ChatBanner.vue** — 6 buttons. Add `sb-btn`.
- [x] **BookingDatePicker.vue** — 6 buttons. Add `sb-btn`.
- [x] **BookingTimePicker.vue** — 4 buttons. Add `sb-btn`.
- [x] **NotificationBell.vue** — 2 buttons. Add `sb-btn`.
- [x] **RatingReminderBanner.vue** — 1 button. Add `sb-btn`.
- [x] **RatingStackModal.vue** — 5 buttons. Skip any `btn-close`.
- [x] **Commit**

---

## Task 4 — Dashboard (Tutee)

- [x] **Action buttons** — 3 schedule nav, 2 pagination. Add `sb-btn`.
- [x] **Favorite tutor list item** — add `sb-interactive`.
- [x] **Clickable tutor list-group item** — add `sb-interactive`.
- [x] **Commit**

---

## Task 5 — TuteeSessions & TuteeProfile

- [x] **TuteeSessions.vue** — 1 action button, clickable table row (`sb-interactive`).
- [x] **TuteeProfile.vue** — 2 buttons.
- [x] **Commit**

---

## Task 6 — Tutee Session Detail Views

- [x] **TuteeSessionDetails.vue** — 3 action buttons.
- [x] **TuteeSessionDetailsFlow.vue** — 6 action buttons.
- [x] **Commit**

---

## Task 7 — Discovery & Tutor Detail

- [x] **FindTutors.vue** — 3 buttons.
- [x] **TutorDetails.vue** — 9 buttons.
- [x] **InitialBooking.vue** — 1 button.
- [x] **Commit**

---

## Task 8 — Payment Flow

- [x] **BookingDetails.vue** — 1 button.
- [x] **PaymentScreenTutee.vue** — 4 buttons.
- [x] **PostSessionPaymentView.vue** — 5 buttons.
- [x] **Commit**

---

## Task 9 — Tutor Dashboard & Profile

- [x] **TutorDashboard.vue** — 1 button.
- [x] **TutorProfile.vue** — 8 action buttons.
- [x] **Commit**

---

## Task 10 — TutorSchedule

- [x] **Add `sb-btn` to all 19 buttons**.
- [x] **Commit**

---

## Task 11 — Tutor Session Management

- [x] **TutorRequestedSessions.vue** — 5 action buttons, clickable card (`sb-interactive`).
- [x] **TutorBookingDetailsFlow.vue** — 2 buttons.
- [x] **TutorPaymentScreen.vue** — 1 button.
- [x] **Commit**

---

## Task 12 — Reports & Wallet

- [x] **SessionsReports.vue** — 2 buttons.
- [x] **TutorSessionsReports.vue** — 2 buttons.
- [x] **TutorWallet.vue** — 6 action buttons.
- [x] **Commit**

---

## Task 13 — Admin Views

- [x] **AdminDashboard.vue** — 1 retry, 3 quick actions.
- [x] **AdminInstitutions.vue** — 7 buttons.
- [x] **AdminReports.vue** — 1 button.
- [x] **AdminUsers.vue** — 2 action buttons.
- [x] **AdminWithdrawals.vue** — 7 action buttons.
- [x] **Commit**

---

## Manual Testing Checklist (Check all)

### **Global & Shared**
- [ ] **App.vue (Header):** "Book Session" & "Manage Pending Sessions" lift/press.
- [ ] **ChatBanner.vue:** Action buttons (Set Location, Rate Session, View Details).
- [ ] **BookingDatePicker.vue:** Trigger, month nav, "Today" button.
- [ ] **BookingTimePicker.vue:** Time chips, AM/PM toggles, selection trigger.
- [ ] **NotificationBell.vue:** Bell icon trigger and notification items.
- [ ] **RatingReminderBanner.vue:** "Rate Latest Session" button on dashboard.
- [ ] **RatingStackModal.vue:** Star ratings, "Skip", "Previous", and "Submit".

### **Tutee-Specific**
- [ ] **Dashboard.vue:** Schedule nav, pagination, favorite tutor cards (`sb-interactive`), tutor list rows (`sb-interactive`).
- [ ] **FindTutors.vue:** Search/filter buttons, "Book Session" buttons.
- [ ] **InitialBooking.vue:** "Find Tutor" search button.
- [ ] **TutorDetails.vue:** Back button, favorite/message icons, slot selection, "Confirm Booking".
- [ ] **TuteeSessions.vue:** Filter pills, table rows (`sb-interactive`).
- [ ] **TuteeProfile.vue:** "Update Photo" and "Save Changes".
- [ ] **TuteeSessionDetails / Flow:** "Message Tutor", "Cancel Session", "Proceed to Payment".
- [ ] **Payment Screens:** Method selection pills and "Submit" buttons.
- [ ] **PreferenceSetup.vue:** Step navigation buttons and subject cards (`sb-interactive`).

### **Tutor-Specific**
- [ ] **TutorDashboard.vue:** "View Details" in upcoming table.
- [ ] **TutorProfile.vue:** "Edit Bio", "Add Subjects", subject accordion headers, "Save Changes".
- [ ] **TutorSchedule.vue:** (High Impact) Week nav, slot pills, "Block Date", Add Slot modal.
- [ ] **TutorRequestedSessions.vue:** "Accept", "Reject", edit location, request cards (`sb-interactive`).
- [ ] **TutorBookingDetailsFlow.vue:** "Mark as Complete", "Dev: End Session".
- [ ] **TutorPaymentScreen.vue:** "Verify Paid" button.
- [ ] **TutorWallet.vue:** "Withdraw Funds", "Refresh", Dev tool buttons.
- [ ] **TutorPreferenceSetup.vue:** "Complete Profile" button.

### **Admin-Specific**
- [ ] **AdminDashboard.vue:** Quick Action buttons, Retry button.
- [ ] **AdminInstitutions.vue:** "Add Institution", edit pencil, status toggles.
- [ ] **AdminUsers.vue:** Eye icon (View), suspension toggle.
- [ ] **AdminWithdrawals.vue:** "Take Action", "Mark Processed", modal actions.
- [ ] **AdminReports.vue:** "Refresh Data" button.

### **Behavioral Verification**
- [ ] **Hover:** Elements lift `translateY(-3px)` + deeper shadow.
- [ ] **Press:** Elements scale down `0.96`.
- [ ] **Release:** Elements snap back with spring effect.
- [ ] **Interactive Surfaces:** `sb-interactive` shows green border + lift on hover.
- [ ] **Disabled State:** No animation/lift when `disabled` attr is present.
