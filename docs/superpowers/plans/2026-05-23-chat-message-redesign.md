# Chat Message Area Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Redesign the chat message area with date dividers, avatar circles on received messages, and a status-aware booking banner that reflects all booking lifecycle states.

**Architecture:** Extend `get_current_booking_context` in `services.py` to return a `status_intent` field covering all six booking states plus a new `review_pending` state for completed-unrated sessions. Replace the existing in-stream `BookingCard` header with a new `ChatBanner.vue` component that renders a role-aware variant per `status_intent`. Add `groupedMessages` computed to `Chat.vue` that injects date-separator sentinel objects into the messages array, and add avatar circles to received text bubbles.

**Tech Stack:** Vue 3 Composition API, Pinia, Django REST Framework, Bootstrap 5, `--sb-primary: #00895A`

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `backend/studybuddy/chat/services.py` | Modify | Add `status_intent` to `get_current_booking_context`; handle `review_pending` + terminal states |
| `backend/studybuddy/tests.py` | Modify | Tests for all `status_intent` branches |
| `src/components/ChatBanner.vue` | Create | Status-aware banner with 7 variants |
| `src/views/Chat.vue` | Modify | Date dividers, avatar circles, replace header BookingCard with ChatBanner, wire RatingStackModal |

---

## Task 1: Backend tests for `status_intent` (write first, run red)

**Files:**
- Modify: `backend/studybuddy/tests.py`

**Context:** `get_current_booking_context(room)` in `services.py` currently returns a dict (or `None`) with booking details. It queries only `Pending | Confirmed | Awaiting Payment Verification` statuses. We need it to also return `status_intent` on every result, handle `Completed + unrated`, and handle recent `Rejected | Cancelled`.

The `Rating` model (in `studybuddy/models.py`) has a `OneToOneField` to `Booking` with `related_name="rating"`. A booking is unrated when `not hasattr(booking, 'rating')`, which in ORM terms is `.exclude(rating__isnull=False)`.

- [ ] **Step 1: Add imports at the top of the test file**

Open `backend/studybuddy/tests.py`. The existing imports block ends around line 17. Add `Rating` and `get_current_booking_context` to the imports:

```python
from .chat.services import get_current_booking_context
from .models import (
    Booking,
    Rating,
    Subjects,
    Tutor,
    TutorAvailability,
    TutorAvailabilityOverride,
    TutorSubjects,
    UserProfile,
)
from .chat.models import ChatRoom, Message
```

- [ ] **Step 2: Add a helper method to `ChatFeatureTests` for creating bookings**

Inside `class ChatFeatureTests(APITestCase)`, after the existing `setUp`, add:

```python
def make_booking(self, status, session_mode='F2F', preferred_location='Library',
                 session_date=None, days_ago=0):
    from datetime import date, timedelta
    from uuid import uuid4
    # Cancel the setUp booking so it doesn't interfere with this test's query
    self.booking.status = 'Cancelled'
    self.booking.save(update_fields=['status'])
    d = session_date or (date.today() - timedelta(days=days_ago))
    return Booking.objects.create(
        student=self.tutee_profile,
        tutor=self.tutor,
        availability=self.availability,
        session_date=d,
        session_mode=session_mode,
        preferred_location=preferred_location,
        booking_request_id=uuid4(),
        status=status,
    )
```

- [ ] **Step 3: Write tests for all `status_intent` branches**

Add these test methods inside `class ChatFeatureTests`:

```python
def test_status_intent_pending_f2f_returns_pending_location(self):
    room = ChatRoom.objects.create(tutee=self.tutee_profile, tutor=self.tutor_profile)
    booking = self.make_booking('Pending', session_mode='F2F')
    context = get_current_booking_context(room)
    self.assertIsNotNone(context)
    self.assertEqual(context['status_intent'], 'pending_location')

def test_status_intent_pending_online_returns_pending(self):
    room = ChatRoom.objects.create(tutee=self.tutee_profile, tutor=self.tutor_profile)
    booking = self.make_booking('Pending', session_mode='Online')
    context = get_current_booking_context(room)
    self.assertIsNotNone(context)
    self.assertEqual(context['status_intent'], 'pending')

def test_status_intent_confirmed_returns_confirmed(self):
    from datetime import date
    room = ChatRoom.objects.create(tutee=self.tutee_profile, tutor=self.tutor_profile)
    self.make_booking('Confirmed', session_date=date(2026, 6, 10))
    context = get_current_booking_context(room)
    self.assertIsNotNone(context)
    self.assertEqual(context['status_intent'], 'confirmed')

def test_status_intent_awaiting_payment_returns_awaiting_payment(self):
    from datetime import date
    room = ChatRoom.objects.create(tutee=self.tutee_profile, tutor=self.tutor_profile)
    self.make_booking('Awaiting Payment Verification', session_date=date(2026, 6, 10))
    context = get_current_booking_context(room)
    self.assertIsNotNone(context)
    self.assertEqual(context['status_intent'], 'awaiting_payment')

def test_status_intent_completed_unrated_returns_review_pending(self):
    room = ChatRoom.objects.create(tutee=self.tutee_profile, tutor=self.tutor_profile)
    self.make_booking('Completed', days_ago=1)
    context = get_current_booking_context(room)
    self.assertIsNotNone(context)
    self.assertEqual(context['status_intent'], 'review_pending')

def test_status_intent_completed_rated_returns_none(self):
    room = ChatRoom.objects.create(tutee=self.tutee_profile, tutor=self.tutor_profile)
    booking = self.make_booking('Completed', days_ago=1)
    Rating.objects.create(
        booking=booking,
        student=self.tutee_profile,
        tutor=self.tutor,
        rating_score=5,
    )
    context = get_current_booking_context(room)
    self.assertIsNone(context)

def test_status_intent_rejected_recent_returns_rejected(self):
    room = ChatRoom.objects.create(tutee=self.tutee_profile, tutor=self.tutor_profile)
    self.make_booking('Rejected', days_ago=2)
    context = get_current_booking_context(room)
    self.assertIsNotNone(context)
    self.assertEqual(context['status_intent'], 'rejected')

def test_status_intent_cancelled_recent_returns_cancelled(self):
    room = ChatRoom.objects.create(tutee=self.tutee_profile, tutor=self.tutor_profile)
    self.make_booking('Cancelled', days_ago=3)
    context = get_current_booking_context(room)
    self.assertIsNotNone(context)
    self.assertEqual(context['status_intent'], 'cancelled')

def test_status_intent_terminal_older_than_7_days_returns_none(self):
    room = ChatRoom.objects.create(tutee=self.tutee_profile, tutor=self.tutor_profile)
    self.make_booking('Rejected', days_ago=8)
    context = get_current_booking_context(room)
    self.assertIsNone(context)
```

- [ ] **Step 4: Run the tests — expect failure**

```bash
cd backend
python manage.py test studybuddy.tests.ChatFeatureTests -v 2
```

Expected: 9 new tests FAIL — `AssertionError` on `status_intent` key not found, `get_current_booking_context` import error, or similar. The existing 2 tests should still pass.

- [ ] **Step 5: Commit the tests**

```bash
git add backend/studybuddy/tests.py
git commit -m "test: add status_intent branch tests for get_current_booking_context"
```

---

## Task 2: Backend — implement `status_intent` in `get_current_booking_context`

**Files:**
- Modify: `backend/studybuddy/chat/services.py`

- [ ] **Step 1: Add `Rating` to imports**

At the top of `backend/studybuddy/chat/services.py`, find:
```python
from studybuddy.models import Booking, Tutor, UserProfile
```
Replace with:
```python
from studybuddy.models import Booking, Rating, Tutor, UserProfile
```

- [ ] **Step 2: Replace `get_current_booking_context` with the extended version**

Find and replace the entire `get_current_booking_context` function (currently ~18 lines ending with `return serialize_booking_context(booking)` or `return None`):

```python
def get_current_booking_context(room):
    current_date = timezone.localdate()

    # 1. Active booking: Pending / Confirmed / Awaiting Payment Verification
    booking = (
        Booking.objects
        .filter(
            student=room.tutee,
            tutor__profile=room.tutor,
            status__in=['Pending', 'Confirmed', 'Awaiting Payment Verification'],
        )
        .filter(Q(status='Pending') | Q(session_date__gte=current_date))
        .select_related('availability', 'student', 'tutor__profile__course')
        .order_by('session_date', 'availability__time_slot', 'id')
        .first()
    )

    if booking:
        context = serialize_booking_context(booking)
        if context is None:
            return None
        if booking.status == 'Pending':
            context['status_intent'] = (
                'pending_location' if booking.session_mode == 'F2F' else 'pending'
            )
        elif booking.status == 'Confirmed':
            context['status_intent'] = 'confirmed'
        else:
            context['status_intent'] = 'awaiting_payment'
        return context

    # 2. Completed but not yet rated
    completed = (
        Booking.objects
        .filter(
            student=room.tutee,
            tutor__profile=room.tutor,
            status='Completed',
        )
        .exclude(rating__isnull=False)
        .select_related('availability', 'student', 'tutor__profile__course')
        .order_by('-session_date', '-availability__time_slot', '-id')
        .first()
    )

    if completed:
        context = serialize_booking_context(completed)
        if context is None:
            return None
        context['status_intent'] = 'review_pending'
        return context

    # 3. Recent terminal booking (last 7 days)
    week_ago = current_date - timedelta(days=7)
    terminal = (
        Booking.objects
        .filter(
            student=room.tutee,
            tutor__profile=room.tutor,
            status__in=['Rejected', 'Cancelled'],
            session_date__gte=week_ago,
        )
        .select_related('availability', 'student', 'tutor__profile__course')
        .order_by('-session_date', '-availability__time_slot', '-id')
        .first()
    )

    if terminal:
        context = serialize_booking_context(terminal)
        if context is None:
            return None
        context['status_intent'] = terminal.status.lower()
        return context

    return None
```

- [ ] **Step 3: Run the tests — expect all pass**

```bash
cd backend
python manage.py test studybuddy.tests.ChatFeatureTests -v 2
```

Expected: All 11 tests PASS.

- [ ] **Step 4: Commit**

```bash
git add backend/studybuddy/chat/services.py
git commit -m "feat: extend get_current_booking_context with status_intent and review_pending/terminal states"
```

---

## Task 3: Create `ChatBanner.vue`

**Files:**
- Create: `src/components/ChatBanner.vue`

**Context:** This component receives `bannerContext` (the `current_booking` dict from the room, now augmented with `status_intent`) and `isTutor` (Boolean). It renders one of 7 variants. For `pending_location`, both roles can edit the location via `chatStore.updatePendingLocation(booking_request_id, location)`. For `review_pending`, a `rate` event is emitted so `Chat.vue` can open the rating modal. For `rejected`/`cancelled`, the banner is dismissible locally.

The `bannerContext` shape (all fields already present in `current_booking`):
```
{
  status_intent: 'pending_location' | 'pending' | 'confirmed' | 'awaiting_payment'
                 | 'review_pending' | 'rejected' | 'cancelled',
  booking_request_id: string | null,
  status: string,
  subject: string,
  date: string,           // ISO date e.g. "2026-06-10"
  startTime: string,      // "14:00"
  endTime: string,        // "15:00"
  preferred_location: string | null,
  session_mode: 'F2F' | 'Online',
  student: string,        // tutee full name
  tutor: string,          // tutor full name
  detail_url: string,     // "/booking-details/123"
  tutee_detail_url: string // "/tuteeSessionDetails/123"
}
```

- [ ] **Step 1: Create the file**

Create `src/components/ChatBanner.vue` with the full content below:

```vue
<template>
  <div v-if="bannerContext && !dismissed" class="chat-banner" :class="`chat-banner--${bannerContext.status_intent}`">

    <!-- pending_location: F2F pending — editable location for both roles -->
    <template v-if="bannerContext.status_intent === 'pending_location'">
      <div class="chat-banner__body">
        <i class="bi bi-geo-alt-fill chat-banner__icon"></i>
        <div class="chat-banner__text">
          <span class="chat-banner__label">Session Pending</span>
          <span class="chat-banner__sub">
            {{ isTutor ? 'Set or confirm the meeting location.' : 'Suggest or confirm the meeting location.' }}
          </span>
        </div>
      </div>
      <div class="chat-banner__action">
        <div v-if="editing" class="chat-banner__location-row">
          <input
            v-model="locationDraft"
            class="chat-banner__location-input"
            placeholder="Enter location"
            :disabled="saving"
          />
          <button class="chat-banner__btn chat-banner__btn--primary" :disabled="saving" @click="saveLocation">
            {{ saving ? 'Saving…' : 'Save' }}
          </button>
          <button class="chat-banner__btn" @click="editing = false">Cancel</button>
        </div>
        <div v-else class="chat-banner__location-display">
          <span class="chat-banner__location-value">
            {{ bannerContext.preferred_location || 'No location set' }}
          </span>
          <button class="chat-banner__btn chat-banner__btn--ghost" @click="startEditing">
            {{ isTutor ? 'Edit' : 'Suggest change' }}
          </button>
        </div>
        <p v-if="locationError" class="chat-banner__error">{{ locationError }}</p>
      </div>
    </template>

    <!-- pending: Online session pending -->
    <template v-else-if="bannerContext.status_intent === 'pending'">
      <div class="chat-banner__body">
        <i class="bi bi-hourglass-split chat-banner__icon"></i>
        <div class="chat-banner__text">
          <span class="chat-banner__label">Session Request Pending</span>
          <span class="chat-banner__sub">Waiting for confirmation.</span>
        </div>
      </div>
    </template>

    <!-- confirmed -->
    <template v-else-if="bannerContext.status_intent === 'confirmed'">
      <div class="chat-banner__body">
        <i class="bi bi-calendar-check-fill chat-banner__icon"></i>
        <div class="chat-banner__text">
          <span class="chat-banner__label">Session Confirmed</span>
          <span class="chat-banner__sub">{{ bannerContext.date }} · {{ bannerContext.startTime }}–{{ bannerContext.endTime }}</span>
        </div>
      </div>
      <RouterLink :to="detailsTarget" class="chat-banner__btn chat-banner__btn--ghost">
        View Details
      </RouterLink>
    </template>

    <!-- awaiting_payment -->
    <template v-else-if="bannerContext.status_intent === 'awaiting_payment'">
      <div class="chat-banner__body">
        <i class="bi bi-clock-history chat-banner__icon"></i>
        <div class="chat-banner__text">
          <span class="chat-banner__label">Payment Submitted</span>
          <span class="chat-banner__sub">Awaiting payment verification.</span>
        </div>
      </div>
    </template>

    <!-- review_pending: tutee sees rate button; tutor sees completed notice -->
    <template v-else-if="bannerContext.status_intent === 'review_pending'">
      <div class="chat-banner__body">
        <i class="bi bi-star-fill chat-banner__icon"></i>
        <div class="chat-banner__text">
          <span class="chat-banner__label">Session Completed</span>
          <span v-if="!isTutor" class="chat-banner__sub">How was your session? Leave a rating.</span>
        </div>
      </div>
      <button v-if="!isTutor" class="chat-banner__btn chat-banner__btn--primary" @click="emit('rate')">
        Rate Session
      </button>
    </template>

    <!-- rejected -->
    <template v-else-if="bannerContext.status_intent === 'rejected'">
      <div class="chat-banner__body">
        <i class="bi bi-x-circle-fill chat-banner__icon"></i>
        <div class="chat-banner__text">
          <span class="chat-banner__label">Booking Rejected</span>
          <span class="chat-banner__sub">This booking was not accepted.</span>
        </div>
      </div>
      <button class="chat-banner__dismiss" aria-label="Dismiss" @click="dismissed = true">
        <i class="bi bi-x"></i>
      </button>
    </template>

    <!-- cancelled -->
    <template v-else-if="bannerContext.status_intent === 'cancelled'">
      <div class="chat-banner__body">
        <i class="bi bi-slash-circle-fill chat-banner__icon"></i>
        <div class="chat-banner__text">
          <span class="chat-banner__label">Session Cancelled</span>
          <span class="chat-banner__sub">This session was cancelled.</span>
        </div>
      </div>
      <button class="chat-banner__dismiss" aria-label="Dismiss" @click="dismissed = true">
        <i class="bi bi-x"></i>
      </button>
    </template>

  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { useChatStore } from '@/stores/chat'

const props = defineProps({
  bannerContext: {
    type: Object,
    default: null,
  },
  isTutor: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['location-saved', 'rate'])

const chatStore = useChatStore()

const editing = ref(false)
const locationDraft = ref(props.bannerContext?.preferred_location || '')
const saving = ref(false)
const locationError = ref('')
const dismissed = ref(false)

// Reset dismiss/edit state when the room changes (bannerContext switches)
watch(
  () => props.bannerContext?.booking_request_id,
  () => {
    dismissed.value = false
    editing.value = false
    locationError.value = ''
    locationDraft.value = props.bannerContext?.preferred_location || ''
  },
)

watch(
  () => props.bannerContext?.preferred_location,
  (val) => {
    if (!editing.value) locationDraft.value = val || ''
  },
)

const detailsTarget = computed(() => {
  if (!props.bannerContext) return '/'
  return props.isTutor
    ? props.bannerContext.detail_url
    : props.bannerContext.tutee_detail_url
})

function startEditing() {
  locationDraft.value = props.bannerContext?.preferred_location || ''
  locationError.value = ''
  editing.value = true
}

async function saveLocation() {
  const trimmed = locationDraft.value.trim()
  if (!trimmed) {
    locationError.value = 'Location is required.'
    return
  }
  saving.value = true
  locationError.value = ''
  try {
    await chatStore.updatePendingLocation(props.bannerContext.booking_request_id, trimmed)
    editing.value = false
    emit('location-saved')
  } catch (err) {
    locationError.value = err?.response?.data?.error || 'Could not update location.'
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.chat-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px 20px;
  border-bottom: 1px solid #e8e8e8;
  background: #f8f9fa;
  flex-shrink: 0;
}

.chat-banner--review_pending {
  background: linear-gradient(90deg, #edf7f3 0%, #f0f4ff 100%);
}

.chat-banner--rejected,
.chat-banner--cancelled {
  background: #fff8f6;
}

.chat-banner--confirmed {
  background: #edf7f3;
}

.chat-banner__body {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.chat-banner__icon {
  font-size: 16px;
  color: var(--sb-primary, #00895a);
  flex-shrink: 0;
}

.chat-banner--rejected .chat-banner__icon,
.chat-banner--cancelled .chat-banner__icon {
  color: #dc3545;
}

.chat-banner__text {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.chat-banner__label {
  font-size: 13px;
  font-weight: 700;
  color: #163127;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chat-banner__sub {
  font-size: 12px;
  color: #6c757d;
  margin-top: 1px;
}

.chat-banner__action {
  flex-shrink: 0;
}

.chat-banner__location-row {
  display: flex;
  gap: 8px;
  align-items: center;
}

.chat-banner__location-display {
  display: flex;
  align-items: center;
  gap: 10px;
}

.chat-banner__location-value {
  font-size: 13px;
  color: #495057;
}

.chat-banner__location-input {
  border: 1px solid #dee2e6;
  border-radius: 8px;
  padding: 6px 10px;
  font-size: 13px;
  min-width: 160px;
}

.chat-banner__btn {
  border: 0;
  border-radius: 8px;
  padding: 7px 14px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  background: transparent;
  color: #495057;
}

.chat-banner__btn--primary {
  background: var(--sb-primary, #00895a);
  color: #fff;
}

.chat-banner__btn--ghost {
  color: var(--sb-primary, #00895a);
  font-weight: 700;
}

.chat-banner__dismiss {
  border: 0;
  background: transparent;
  color: #adb5bd;
  cursor: pointer;
  padding: 4px;
  font-size: 16px;
  line-height: 1;
  flex-shrink: 0;
}

.chat-banner__error {
  color: #dc3545;
  font-size: 12px;
  margin: 4px 0 0;
}
</style>
```

- [ ] **Step 2: Verify the file was created**

```bash
ls src/components/ChatBanner.vue
```

Expected: file exists.

- [ ] **Step 3: Commit**

```bash
git add src/components/ChatBanner.vue
git commit -m "feat: add ChatBanner component with status_intent variants"
```

---

## Task 4: `Chat.vue` — date dividers and avatar circles

**Files:**
- Modify: `src/views/Chat.vue`

**Context:** `Chat.vue` currently iterates `chatStore.messages` inside a `TransitionGroup`. We need to:
1. Replace the iteration source with `groupedMessages` — a computed that injects `{ type: 'date-separator', label, key }` sentinels between date groups.
2. Change the single `div.message-wrapper` in the loop to conditionally render either a date separator or the existing message content.
3. Add a `.message-avatar-sm` circle to the left of each non-me text bubble and restructure the bubble column with CSS.

**`getDateLabel` logic:**
- Same calendar day as today → `'TODAY'`
- Same calendar day as yesterday → `'YESTERDAY'`
- Older → `'May 10, 2026'` format (locale `en-US`, `{ month: 'long', day: 'numeric', year: 'numeric' }`)

- [ ] **Step 1: Add `groupedMessages` computed and `getDateLabel` helper to the `<script setup>` block**

Find the line `watch(() => chatStore.messages.length, scrollToBottom)` in `Chat.vue`. Insert the following before it:

```js
function getDateLabel(timestamp) {
  const date = new Date(timestamp)
  if (Number.isNaN(date.getTime())) return ''
  const today = new Date()
  const yesterday = new Date(today)
  yesterday.setDate(yesterday.getDate() - 1)
  if (date.toDateString() === today.toDateString()) return 'TODAY'
  if (date.toDateString() === yesterday.toDateString()) return 'YESTERDAY'
  return date.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })
}

const groupedMessages = computed(() => {
  const result = []
  let lastLabel = null
  for (const msg of chatStore.messages) {
    const label = getDateLabel(msg.created_at)
    if (label && label !== lastLabel) {
      result.push({ type: 'date-separator', label, key: `sep-${label}` })
      lastLabel = label
    }
    result.push(msg)
  }
  return result
})

function getInitials(name) {
  return String(name || '')
    .split(' ')
    .filter(Boolean)
    .map((part) => part[0])
    .join('')
    .slice(0, 2)
    .toUpperCase()
}
```

- [ ] **Step 2: Replace the `TransitionGroup` block in the template**

Find this exact block in the template (around line 75–122):

```html
              <TransitionGroup :name="historyLoaded ? 'msg' : ''" tag="div" class="messages-group">
                <div
                  v-for="msg in chatStore.messages"
                  :key="msg.id"
                  class="message-wrapper"
                  :class="{
                    'is-me': msg.is_me,
                    'is-system': msg.message_type !== 'text',
                    'is-pending': msg.status === 'pending' || msg.pending === true,
                  }"
                >
                  <div v-if="!msg.is_me && msg.message_type === 'text'" class="message-sender">
                    {{ msg.sender_name }}
                  </div>

                  <div v-if="msg.message_type === 'booking_event'" class="system-event">
```

Replace the entire `TransitionGroup` (from the opening tag to its closing `</TransitionGroup>`) with:

```html
              <TransitionGroup :name="historyLoaded ? 'msg' : ''" tag="div" class="messages-group">
                <div
                  v-for="item in groupedMessages"
                  :key="item.type === 'date-separator' ? item.key : item.id"
                  :class="item.type === 'date-separator'
                    ? 'date-separator-row'
                    : ['message-wrapper', {
                        'is-me': item.is_me,
                        'is-system': item.message_type !== 'text',
                        'is-pending': item.status === 'pending' || item.pending === true,
                      }]"
                >
                  <!-- Date separator -->
                  <template v-if="item.type === 'date-separator'">
                    <span class="date-separator-label">{{ item.label }}</span>
                  </template>

                  <!-- Message content -->
                  <template v-else>
                    <div v-if="item.message_type === 'booking_event'" class="system-event">
                      <i class="bi bi-calendar-check"></i>
                      <div>
                        <strong>{{ item.content }}</strong>
                        <BookingCard
                          v-if="item.metadata?.booking"
                          :booking="item.metadata.booking"
                          :is-tutor="isTutor"
                          compact
                          @location-saved="handleLocationSaved"
                        />
                      </div>
                    </div>

                    <template v-else>
                      <div v-if="!item.is_me" class="message-avatar-sm">
                        {{ getInitials(item.sender_name) }}
                      </div>
                      <div class="message-bubble-col">
                        <div
                          class="message-bubble"
                          :class="{ 'sb-pop-active': poppingMessages.has(item.id) }"
                        >
                          <div class="message-content">{{ item.content }}</div>
                          <div class="message-meta">
                            <span>{{ formatTime(item.created_at) }}</span>
                            <span v-if="item.pending" class="send-status">
                              <span class="send-indicator-dot" aria-hidden="true"></span>
                              Sending
                            </span>
                            <span v-else-if="item.is_me && item.is_read">Read</span>
                            <span v-else-if="item.is_me">Sent</span>
                          </div>
                        </div>
                      </div>
                    </template>
                  </template>
                </div>
              </TransitionGroup>
```

Note: the `poppingMessages.has(item.id)` check moved to the bubble div's class. Remove the standalone `sb-pop-active` span that was previously wrapping "Read" — the pop animation now lives on the bubble itself. If you want the pop on the "Read" text only, move `:class="{ 'sb-pop-active': poppingMessages.has(item.id) }"` back to the `<span>` instead and remove it from the bubble div.

- [ ] **Step 3: Add CSS for date separators and avatar circles**

In the `<style scoped>` block, find `.message-sender {` and replace it with the following (remove the old `.message-sender` rule entirely and add these):

```css
.date-separator-row {
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 8px 0;
  max-width: 100%;
  align-self: stretch;
}

.date-separator-label {
  font-size: 11px;
  font-weight: 700;
  color: #adb5bd;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  background: #fcfdfc;
  padding: 0 12px;
}

.message-avatar-sm {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--sb-primary, #00895a);
  color: #fff;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 800;
  flex-shrink: 0;
  align-self: flex-end;
}

.message-bubble-col {
  display: flex;
  flex-direction: column;
  min-width: 0;
  max-width: 100%;
}
```

Also update `.message-wrapper` (not `.is-me`) to be a flex row so the avatar sits to the left of the bubble:

Find:
```css
.message-wrapper {
  display: flex;
  flex-direction: column;
  max-width: 72%;
  align-self: flex-start;
}
```

Replace with:
```css
.message-wrapper {
  display: flex;
  flex-direction: row;
  gap: 8px;
  max-width: 72%;
  align-self: flex-start;
  align-items: flex-end;
}

.message-wrapper.is-me {
  flex-direction: column;
  align-items: flex-end;
}
```

- [ ] **Step 4: Start the dev server and verify visually**

```bash
npm run dev
```

Open `http://localhost:5173` in a browser. Navigate to a chat room with messages spanning multiple dates. Confirm:
- Date labels (TODAY / YESTERDAY / date string) appear between date groups.
- Received messages have a green initial circle to their left.
- Sent messages have no avatar circle and remain right-aligned.
- Booking event messages are full-width with no avatar.

- [ ] **Step 5: Commit**

```bash
git add src/views/Chat.vue
git commit -m "feat: add date dividers and avatar circles to chat message list"
```

---

## Task 5: `Chat.vue` — integrate ChatBanner and RatingStackModal

**Files:**
- Modify: `src/views/Chat.vue`

**Context:** The current `Chat.vue` renders a `BookingCard` at the top of the `.message-list` when `chatStore.currentRoom.current_booking` exists. We replace this with `ChatBanner` above the message list. We also add `RatingStackModal` (already used in `RatingReminderBanner`) to handle the `rate` event emitted by `ChatBanner`.

- [ ] **Step 1: Add imports to `<script setup>`**

Find:
```js
import { useChatStore } from '@/stores/chat'
import { useAuthStore } from '@/stores/auth'
```

Replace with:
```js
import { useChatStore } from '@/stores/chat'
import { useAuthStore } from '@/stores/auth'
import { useSessionsStore } from '@/stores/completedSessions'
import ChatBanner from '@/components/ChatBanner.vue'
import RatingStackModal from '@/components/RatingStackModal.vue'
```

- [ ] **Step 2: Add sessions store and rating modal state**

Find:
```js
const isTutor = computed(() => {
```

Insert before it:
```js
const sessionsStore = useSessionsStore()
const ratingModalOpen = ref(false)

async function openRatingModal() {
  if (!sessionsStore.sessions.length) {
    await sessionsStore.fetchSessions()
  }
  ratingModalOpen.value = true
}
```

- [ ] **Step 3: Replace the inline `BookingCard` header with `ChatBanner`**

In the template, find (inside `.message-list`):
```html
            <div class="message-list" ref="messageList">
              <BookingCard
                v-if="chatStore.currentRoom.current_booking"
                :booking="chatStore.currentRoom.current_booking"
                :is-tutor="isTutor"
                @location-saved="handleLocationSaved"
              />
```

Replace with:
```html
            <ChatBanner
              v-if="chatStore.currentRoom.current_booking"
              :banner-context="chatStore.currentRoom.current_booking"
              :is-tutor="isTutor"
              @location-saved="handleLocationSaved"
              @rate="openRatingModal"
            />

            <div class="message-list" ref="messageList">
```

Note: `ChatBanner` moves OUTSIDE `.message-list` (above it), so it doesn't scroll with messages. The div remains as the scrollable container.

- [ ] **Step 4: Add `RatingStackModal` to the template**

After the closing `</section>` tag of `.chat-main` (or just before `</div>` of `.chat-shell`), add:

```html
    <RatingStackModal
      :open="ratingModalOpen"
      :sessions="sessionsStore.unratedCompletedSessions"
      @close="ratingModalOpen = false"
      @rated="ratingModalOpen = sessionsStore.unratedCompletedSessions.length > 0"
    />
```

- [ ] **Step 5: Verify layout — banner is above the scrollable message area**

The `.chat-main-inner` already uses `display: flex; flex-direction: column`. After this change, the vertical order inside `.chat-main-inner` should be:
1. `.chat-header` (partner name + connection status)
2. `ChatBanner` (when booking exists)
3. `.message-list` (scrollable, `flex: 1`)
4. `.chat-input-area` (composer)

Start the dev server (`npm run dev`) and open a chat room with a current booking. Confirm the banner appears between the header and the messages, does not scroll with messages, and renders the correct variant for the booking status.

- [ ] **Step 6: Test each banner variant manually**

Using the Django admin or the existing API, set a booking to each status and reload the chat room:
- `Pending` + F2F → location edit row visible
- `Pending` + Online → "Session Request Pending" info strip
- `Confirmed` → date/time shown, "View Details" link visible
- `Awaiting Payment Verification` → "Payment Submitted" info strip
- `Completed` (no rating, tutee view) → "Rate Session" button opens modal
- `Rejected` or `Cancelled` (within 7 days) → dismissible strip

- [ ] **Step 7: Commit**

```bash
git add src/views/Chat.vue
git commit -m "feat: integrate ChatBanner and RatingStackModal into chat view"
```

---

## Self-Review Checklist

**Spec coverage:**
- [x] Date dividers — Task 4
- [x] Avatar circles on received messages — Task 4
- [x] `pending_location` banner (F2F tutee/tutor editable location) — Task 3
- [x] `pending` banner (Online sessions) — Task 3
- [x] `confirmed` banner with View Details — Task 3
- [x] `awaiting_payment` info strip — Task 3
- [x] `review_pending` Rate button → modal — Tasks 3 + 5
- [x] `rejected` / `cancelled` dismissible strip — Task 3
- [x] Backend `status_intent` for all states — Task 2
- [x] Backend tests (TDD) — Task 1
- [x] Left sidebar unchanged — (no sidebar tasks)
- [x] File attachments excluded — (not in plan)

**Placeholder scan:** No TBD/TODO in any step. All code blocks are complete.

**Type consistency:**
- `bannerContext.status_intent` — written in Python as `context['status_intent']`, read in Vue as `bannerContext.status_intent` ✓
- `chatStore.updatePendingLocation(booking_request_id, location)` — same signature used in existing `BookingCard` and in `ChatBanner.vue` ✓
- `sessionsStore.unratedCompletedSessions` — same store key used by existing `RatingReminderBanner` ✓
- `groupedMessages` items: separator shape `{ type, label, key }`, message shape passes through unchanged ✓
