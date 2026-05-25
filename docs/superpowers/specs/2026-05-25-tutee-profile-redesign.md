# Tutee Profile Redesign — Design Spec

**Date:** 2026-05-25  
**Topic:** Tutee Profile Bento Redesign  
**Route:** `/tutee-profile` → `src/views/TuteeProfile.vue`  
**Role:** Tutee only (`meta: { role: 'Tutee' }`)  
**Styling:** Scoped CSS glassmorphism (No Tailwind, Bootstrap Icons only)

---

## 1. Goal

Replace the plain Bootstrap layout of the tutee profile page with an Aurora Bento glassmorphism aesthetic. All existing data fields are preserved, with added frontend-only enhancements for education-level-aware year and course selection. Real avatar photo upload is wired to the existing `profile_picture` model field via a new backend endpoint.

---

## 2. Architecture & Data Flow

### 2a. Backend Updates (`backend/studybuddy/`)

- **GET `/tutee/profile/`**: Update response to include `profile_picture_url` using `request.build_absolute_uri(profile.profile_picture.url)` if available.
- **POST `/tutee/profile/avatar/`**: New endpoint.
  - Accepts `multipart/form-data` with field `avatar`.
  - Validates: presence of file, `image/*` content-type, max size 5MB.
  - Saves to `UserProfile.profile_picture`.
  - Returns `{ "profile_picture_url": "..." }`.
  - Auth: `@permission_classes([IsAuthenticated])`.
- **PUT `/tutee/profile/update/`**: Payload remains `{ fname, mname, lname, course, year_level, bio, subjects }`.

### 2b. Frontend State (`src/views/TuteeProfile.vue`)

- **Reactive `profile` Object**: Synchronized with server data.
- **`educationLevel`**: Local reactive state (`elementary` | `jhs` | `shs` | `college`) derived from `year_level` on load.
  - **Derivation Logic**: 
    - 1–6: Elementary
    - 7–10: JHS
    - 11–12: SHS
    - 13–16: College

---

## 3. UI & Interaction Design

### 3a. Layout: The Unified Bento

A 100% height aurora shell containing a centered `.glass-modal` (max-width 900px).

- **Header**: Profile identity (Avatar + Name) + Action buttons (Discard, Save).
- **Body (Split Grid)**:
  - **Left (7/12)**: 
    - Personal Info section (fname, mname, lname, email - email locked).
    - Bio section with character counter integration.
  - **Right (5/12)**: 
    - Education Level (4 radio cards).
    - Year Level (Radio grid, context-aware).
    - Course/Strand (Radio cards, labels change based on level).
    - Preferred Subjects (Multi-select pill checkboxes).

### 3b. Context-Aware Selection

| Academic Level | Year Options | Label for Specialization |
|---|---|---|
| **Elementary** | Grade 1-6 | Hidden |
| **JHS** | Grade 7-10 | Hidden |
| **SHS** | Grade 11-12 | "Strand" |
| **College** | 1st-4th Year | "Course" |

*Note: Changing the Academic Level clears the current Year Level and Course/Strand selection to maintain validity.*

### 3c. Styling & Haptics

- **Glassmorphism**: `backdrop-filter: blur(24px)`, `rgba(255, 255, 255, 0.86)` background, subtle 1px white border.
- **Bio Counter**: Color-warning only. Textarea border/glow transitions from neutral to red (e.g., `var(--sb-danger)`) as the character count approaches 500.
- **Buttons**: All buttons use `.sb-btn` for consistent haptics and hover lift animations.
- **Inputs**: `.input-glass` class for consistent focus rings and semi-transparent backgrounds.

---

## 4. Testing & Validation

### 4a. Functional Tests
- Verify profile data loads correctly on mount.
- Verify avatar upload updates the preview and persists to the backend.
- Verify changing Academic Level updates Year Level options and clears previous selections.
- Verify multi-select subjects are correctly saved and loaded.

### 4b. UI/UX Tests
- Verify glassmorphism rendering across different screen sizes (responsive check).
- Verify bio counter color change at/near 500 characters.
- Verify "Discard" resets all local changes to server state.

---

## 5. Out of Scope
- Tutor profile redesign.
- Shared navigation/sidebar changes.
- Dark mode.
