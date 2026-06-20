# Antigravity Edge-Case Findings — 2026-06-14

## Summary
- **Files scanned**: 27
- **Findings**: 55 primary findings, 7 uncertain findings
- **Passes completed**: A / B / C / D

---

## Pass A — Money & Auth

### [A-01] [CRITICAL] [E3: Number/money] — PayMongo Payout Amount Passed in PHP instead of Centavos
- File: backend/studybuddy/paymongo_money_movement.py:97
- What: The PayMongo wallet transaction API requires the amount in PHP centavos (as an integer), but the code passes the PHP decimal value directly as a string.
- Trigger: A tutor cash-out transaction is initiated, and the value (e.g. `500.00` PHP) is sent as `'500.00'` or `'500'`, which PayMongo processes as 500 centavos (5 PHP) or rejects due to validation error.
- Code:
```python
    attributes = {
        'amount': str(amount),
        'currency': 'PHP',
```
- Suggested check: Convert the decimal amount to centavos (multiply by 100) and cast it to an integer before converting to a string.

### [A-02] [CRITICAL] [E3: Number/money] — Response Fee and Net Amount Not Converted from Centavos to PHP
- File: backend/studybuddy/paymongo_money_movement.py:64-65
- What: PayMongo API returns amounts (fees, net amounts) in PHP centavos, but `normalize_wallet_transaction` parses these directly as PHP Decimals, resulting in transaction records that are 100 times their actual value.
- Trigger: A successful wallet transaction callback/response returns a fee of `1500` (15.00 PHP) and net amount of `48500` (485.00 PHP), which are stored as 1500.00 PHP and 48500.00 PHP in the database.
- Code:
```python
        'fee': parse_decimal(attributes.get('fee')),
        'net_amount': parse_decimal(attributes.get('net_amount')),
```
- Suggested check: Divide the parsed decimal amounts by 100 to convert them from centavos to PHP before returning.

### [A-03] [MEDIUM] [E10: External Calls] — Missing Timeout in PayMongo External API Requests
- File: backend/studybuddy/paymongo_money_movement.py:71
- What: The `requests.get` and `requests.post` HTTP calls to PayMongo do not specify a timeout, exposing the system to potential thread blockages and resource exhaustion if PayMongo hangs indefinitely.
- Trigger: The PayMongo API endpoint experiences high latency or hangs without closing the TCP connection.
- Code:
```python
    response = requests.get(
        f'{PAYMONGO_API_BASE_URL}/wallets/receiving_institutions',
        params={'provider': provider},
        headers=get_money_movement_headers(),
    )
```
- Suggested check: Always specify a reasonable `timeout` parameter (e.g., `timeout=10`) on all external requests.

### [A-04] [HIGH] [E9: Error Handling] — Unhandled RequestExceptions in PayMongo API Communication
- File: backend/studybuddy/paymongo_money_movement.py:77-80
- What: If `requests` raises a connection or timeout error (e.g. `requests.exceptions.RequestException`), it is not caught within the helper functions, bypassing custom exception translation and causing 500 internal server errors.
- Trigger: Network disruptions or API downtimes occur during a cash-out transaction, throwing raw network exceptions.
- Code:
```python
    try:
        response_body = response.json()
    except ValueError:
        response_body = {'raw': getattr(response, 'text', '')}
```
- Suggested check: Wrap the API request call in a try-except block that catches `requests.RequestException` and raises `PayMongoCashOutError` or returns a failed response.

### [A-05] [MEDIUM] [E8: Input validation] — Unhandled Decimal Parsing Errors in API Response Processing
- File: backend/studybuddy/paymongo_money_movement.py:41-45
- What: `parse_decimal` does not catch parsing errors (e.g., `decimal.InvalidOperation`), which will crash response parsing if a malformed or non-numeric value is returned by the API.
- Trigger: The PayMongo API returns a non-numeric string or invalid data for `fee` or `net_amount`.
- Code:
```python
def parse_decimal(value, default='0.00'):
    if value in (None, ''):
        return decimal.Decimal(default)

    return decimal.Decimal(str(value))
```
- Suggested check: Wrap the decimal instantiation in a try-except block catching `decimal.InvalidOperation` and return the default value.

### [A-06] [HIGH] [E3: Number/money] — Platform Fees Added to Gross Earnings and Missing from Net Calculations in UI
- File: src/stores/wallet.js:23-33
- What: The `totals` computed property calculates incorrect sums by adding the absolute value of `commission_deduction` to `gross` instead of subtracting it from `net`, and ignores the fact that `session_credit` is already logged as a net value.
- Trigger: Tutors check their balance tracking display when having both `session_credit` (online net) and `commission_deduction` (cash platform fee) transactions.
- Code:
```javascript
    transactions.value.forEach(t => {
      const amount = Number(t.amount) || 0
      if (t.transaction_type === 'session_credit') {
        gross += amount
        net += amount
      } else if (t.transaction_type === 'commission_deduction') {
        const absAmount = Math.abs(amount)
        gross += absAmount
        deductions += absAmount
      }
    })
```
- Suggested check: Ensure deductions are subtracted from `net` and that `gross` is calculated based on actual session price before platform cuts.

### [A-07] [MEDIUM] [E9: Error Handling] — Missing Error Handling in Wallet Store API Calls
- File: src/stores/wallet.js:55-58
- What: Wallet store fetching actions lack try-catch exception handling, which will cause unhandled promise rejections if the API requests fail.
- Trigger: The user loses internet connectivity or the session expires, causing the backend requests to fail.
- Code:
```javascript
  async function fetchTransactions() {
    const { data } = await api.get('wallet/transactions/')
    transactions.value = data
  }
```
- Suggested check: Wrap API calls in a try-catch block to handle errors and potentially prompt a message or reset states.

### [A-08] [MEDIUM] [E9: Error Handling] — Unhandled Promise Rejections in Refresh Button Triggers
- File: src/views/TutorWallet.vue:499-506
- What: `refreshData` makes concurrent API calls using `Promise.all` but does not catch failures, leading to unhandled promise rejections when triggered from the Refresh button.
- Trigger: The tutor clicks "Refresh" when the network is offline or the auth token is invalid.
- Code:
```javascript
const refreshData = async () => {
  await Promise.all([
    walletStore.fetchWallet(),
    walletStore.fetchTransactions(),
    walletStore.fetchWithdrawals(),
    walletStore.fetchPayoutAccounts(),
  ])
}
```
- Suggested check: Add a try-catch wrapper in `refreshData` or handle the rejected promise in the button event listener.

### [A-09] [LOW] [E1: Null/undefined/missing] — Unvalidated Date Parsing and Formatting
- File: src/views/TutorWallet.vue:627-634
- What: `formatDate` parses inputs directly with `new Date()` without checking for null, blank, or invalid values, which will display `"Invalid Date"` or cause rendering errors.
- Trigger: The UI attempts to format a transaction or withdrawal that has a missing or malformed date field.
- Code:
```javascript
const formatDate = (dateStr) =>
  new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
```
- Suggested check: Validate that `dateStr` is a valid date string before formatting and return a fallback placeholder if not.

### [A-10] [MEDIUM] [E7: Concurrency/double-action] — Missing Loading/Disabled State for Payout Destination Deactivation
- File: src/views/TutorWallet.vue:179-186
- What: Deactivating a payout account does not disable the click handler or set a loading state, allowing the user to trigger duplicate HTTP PATCH requests.
- Trigger: The user clicks the slash icon/button on a saved destination card multiple times in rapid succession.
- Code:
```javascript
const deactivateAccount = async (id) => {
  if (!confirm('Deactivate this payout destination?')) return
  await walletStore.deactivatePayoutAccount(id)
}
```
- Suggested check: Disable the deactivation action and show a loader while the deactivation request is in flight.

### [A-11] [HIGH] [E1: Null/undefined/missing] — Unchecked Store Array Filter on Component Mount
- File: src/views/AdminWithdrawals.vue:510-512
- What: The `exceptionWithdrawals` computed property attempts to filter `store.withdrawals` without checking if it is initialized, raising a TypeError if the store data is missing.
- Trigger: The component mounts and runs the computed property before the store fetches or if `store.withdrawals` is null.
- Code:
```javascript
const exceptionWithdrawals = computed(() => {
  return store.withdrawals.filter(w => ['failed', 'flagged'].includes(w.status))
})
```
- Suggested check: Add a fallback check (e.g. `(store.withdrawals || []).filter(...)`) to prevent TypeError.

### [A-12] [MEDIUM] [E7: Concurrency/double-action] — Missing Loading States in Action Modal Status Transitions
- File: src/views/AdminWithdrawals.vue:556-568
- What: `updateStatus` does not set a loading state or disable action buttons in the exception details modal, enabling users to send duplicate requests for status updates.
- Trigger: The admin double-clicks or rapidly clicks the "Retry & Mark Processed" or "Reject & Refund Balance" buttons.
- Code:
```javascript
const updateStatus = async (status) => {
  if (confirm(`Are you sure you want to mark this as ${status}?`)) {
    try {
      await store.updateWithdrawalStatus(activeWithdrawal.value.id, { 
        status,
        failure_reason: failureReason.value
      })
      activeWithdrawal.value = null
    } catch {
      toastStore.push('Update failed.', 'error')
    }
  }
}
```
- Suggested check: Disable the modal buttons and display a spinner while the status update API request is processing.

### [A-13] [MEDIUM] [E1: Null/undefined/missing] — Unvalidated Date String Parsing causing Potential RangeError
- File: src/views/AdminWithdrawals.vue:526-529
- What: `formatDate` parses input strings using `new Date()` without validation, which will throw a `RangeError: Invalid time value` if the date is malformed or null, crashing the table rendering.
- Trigger: Rendering a withdrawal request where the `requested_at` timestamp is null or invalid.
- Code:
```javascript
const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: 'numeric', minute: '2-digit' })
}
```
- Suggested check: Add a guard to check for valid date input before invoking `toLocaleDateString` and return a fallback placeholder.

### [A-14] [MEDIUM] [E1: Null/undefined/missing] — Partial Session Restoration Leaves User Profile Fields Undefined
- File: src/stores/auth.js:230-250
- What: `initializeAuth` initializes the session using only `user_role`, `user_id`, and `profile_id` from local storage, which leaves user profile fields like `email`, `fname`, and `lname` as `undefined` upon refreshing.
- Trigger: A user refreshes their browser and the application immediately tries to render `authStore.user?.email` or `authStore.user?.fname`.
- Code:
```javascript
    if (storedRole) {
      const storedUserId = localStorage.getItem('user_id')
      const storedProfileId = localStorage.getItem('profile_id')
      user.value = {
        role: normalizeRole(storedRole),
        id: storedUserId ? parseInt(storedUserId) : undefined,
        profile_id: storedProfileId ? parseInt(storedProfileId) : undefined
      }
    }
```
- Suggested check: Store the complete user object inside `localStorage` or trigger a profile details fetch upon initialization.

### [A-15] [MEDIUM] [E8: Input validation] — Public Endpoint Slash Mismatch in Auth Bypass Check
- File: src/services/api/api.js:36-40
- What: `isPublicEndpoint` uses exact matching against `PUBLIC_ENDPOINTS` (which all end in trailing slashes), causing any requests dispatched without a trailing slash (like `/login` or `/register`) to bypass the public list, leading to unnecessary token refreshes or logouts.
- Trigger: A post request is made to `/login` without a trailing slash, resulting in a 401 response and triggering a token refresh attempt.
- Code:
```javascript
const isPublicEndpoint = (requestUrl = '') => {
  const path = getApiPath(requestUrl)

  return PUBLIC_ENDPOINTS.some((endpoint) => path === endpoint || path.startsWith(`${endpoint}?`))
}
```
- Suggested check: Strip trailing slashes from both the evaluated path and the static endpoint lists before comparison.

---

## Pass B — Booking Flow

### [B-01] [MAJOR] [E8] — Location validation bypass in Face-to-face confirmation
- File: src/views/TutorDetails.vue:201-209
- What: A user can confirm a Face-to-face booking without providing a preferred location because the input's `required` attribute is not enforced since there is no wrapping `<form>` element for the submission.
- Trigger: Click the "Confirm Booking" button on a Face-to-face session without entering a location in the input.
- Code:
```html
              <div v-if="isFaceToFace" class="mb-4">
                <label class="form-label fw-bold small text-muted">Preferred Location</label>
                <input
                  type="text"
                  v-model="bookedSessionStore.bookedSessionLocation"
                  class="form-control border-sb shadow-none py-2 rounded-3"
                  placeholder="e.g. Library Room 3"
                  required
                />
```
- Suggested check: Add a verification guard in `confirmBooking` that checks if the mode is Face-to-face and the location string is empty or whitespace.

### [B-02] [RESOLVED - FALSE POSITIVE] [E6] — Blocked/overridden slots can be booked via range expansion
- File: src/views/TutorDetails.vue:385-389
- What: Originally flagged because the continuous range auto-selection logic (`effectiveSelectedSlots`) does not separately filter out `slot.is_overridden === true`.
- Verified 2026-06-14: Not exploitable. `backend/studybuddy/views.py:1824` computes
  `"is_booked": is_booked or is_slot_past or is_overridden` — i.e. `is_overridden` is
  already folded into `is_booked` at the API level. Both the slot button's `:disabled`
  (TutorDetails.vue:111) and the range-expansion candidate pool `selectableDaySlots`
  (TutorDetails.vue:385-387) filter on `!slot.is_booked`, so an overridden slot can
  never be clicked directly nor appear in `selectableDaySlots`. Its absence breaks the
  30-minute continuity check (`isContinuousRange`), so a range can never expand across
  it. `slot.is_overridden` is only used for the `blocked` CSS class — purely visual.
- Code:
```javascript
    const selectableDaySlots = [...day.slots]
      .filter(slot => !slot.is_booked)
      .sort((left, right) => left.time_slot.localeCompare(right.time_slot))
```
- No action needed. Keep `is_booked`/`is_overridden` semantics in sync if either side changes.

### [B-03] [MEDIUM] [E9] — Silent failure when tutor details or schedule loading fails
- File: src/views/TutorDetails.vue:544-546
- What: If loading tutor details or schedule fails, the error is caught and printed to the console, but the UI fails silently without displaying any error message/toast to the user.
- Trigger: Network failure or server 500 error while fetching tutor details or schedule on page load.
- Code:
```javascript
  } catch (error) {
    console.error('Failed to load tutor details.', error)
  }
```
- Suggested check: Push a user-friendly error message to the toast store in the `catch` blocks of `getTutorDetails` and `getTutorSchedule`.

### [B-04] [MEDIUM] [E8] — Silent form submit abort when start or end time is missing
- File: src/views/InitialBooking.vue:297-299
- What: The "Find Tutor" form submission aborts silently with no user feedback if the user hasn't selected a start time or end time, leaving the user confused as to why the button does nothing.
- Trigger: Click "Find Tutor" after filling out other fields but leaving "Time From" or "Time To" unselected.
- Code:
```javascript
  if (!store.selectedStartTime || !store.selectedEndTime) {
    return
  }
```
- Suggested check: Push a toast notification informing the user that start and end times must be selected.

### [B-05] [MEDIUM] [E9] — Silent matching algorithm failure in FindTutors view
- File: src/views/FindTutors.vue:542-544
- What: If the recommended tutors API call fails, the search fails silently (stops loading spinner) without showing a toast notification, leaving the user with an empty "No tutors available" message instead of an error warning.
- Trigger: Click "Search Tutors" and have the API return an error or network drop out.
- Code:
```javascript
  try {
    await ensureFindTutorsData()
  } catch (error) {
    console.error('CBF search failed:', error)
  }
```
- Suggested check: In the `catch` block of `searchTutor`, push an error toast informing the user that the tutor search failed.

### [B-06] [MAJOR] [E4] — Check-in modal trigger window is vulnerable to client-side timezone mismatch
- File: src/stores/activeSession.js:38-39
- What: The active session check-in windows (venue check-in and midpoint check-in) are calculated in the client's local timezone using local Date parsing, which will cause prompts to trigger at the wrong physical time if the client's device timezone differs from the server's standardized timezone.
- Trigger: A user in a non-Manila timezone (e.g. UTC) accesses the dashboard during or around their scheduled session.
- Code:
```javascript
  const normalizedTime = String(timeValue).length === 5 ? `${timeValue}:00` : timeValue
  const parsed = new Date(`${dateValue}T${normalizedTime}`)
```
- Suggested check: Parse date and time values using a fixed timezone offset (e.g. Manila, UTC+8) instead of parsing it in the user's local timezone.

### [B-07] [LOW] [E9] — Unhandled Promise Rejections during active session polling
- File: src/stores/activeSession.js:180-183
- What: `startPolling` sets an interval to call `refreshActive` (which fetches session data from the API) but does not catch or handle potential API errors inside the interval, leading to unhandled promise rejections on network dropouts.
- Trigger: Network connection is lost while the active session polling interval is running.
- Code:
```javascript
    pollTimer = window.setInterval(() => {
      currentTime.value = new Date()
      refreshActive()
    }, SESSION_POLL_INTERVAL_MS)
```
- Suggested check: Wrap the `refreshActive` call inside the interval in a try-catch block or handle the error using a `.catch` call.

### [B-08] [MEDIUM] [E7] — Rapid clicking on favorite button causes concurrent API requests
- File: src/views/TutorDetails.vue:460-463
- What: Rapidly clicking the favorite button can send multiple concurrent API calls (add/remove) out of order, leading to a mismatched favorite state or backend exceptions due to missing debouncing or disabling.
- Trigger: Rapidly click the favorite button.
- Code:
```javascript
const toggleFavorite = async () => {
  isFavorite.value = !isFavorite.value

  try {
```
- Suggested check: Disable the button or add a locking boolean flag during the async favorite update call.

### [B-09] [MAJOR] [E4] — Client local time is used to validate past dates in InitialBooking view
- File: src/views/InitialBooking.vue:141-144
- What: Validation of past dates using `todayKey()` relies on the client's local system time instead of the server's or Manila's timezone, allowing users in timezone-lagged locations to select and request bookings for days that are already in the past in Manila.
- Trigger: A user in a timezone behind Manila (e.g., US or Europe) visits the booking page when it is already the next day in Manila, and selects their local current date (which is already yesterday in Manila).
- Code:
```javascript
const todayKey = () => {
  const today = new Date()
  return `${today.getFullYear()}-${padNumber(today.getMonth() + 1)}-${padNumber(today.getDate())}`
}
```
- Suggested check: Retrieve the current date in Manila timezone (UTC+8) or get the current date from the backend to perform the past date validation.

### [B-10] [MAJOR] [E4] — Client local time is used to validate past dates in FindTutors view
- File: src/views/FindTutors.vue:220-223
- What: Past date validation in the FindTutors view uses the client's local date instead of Manila timezone, letting users in earlier timezones query and book past dates.
- Trigger: A user in a timezone behind Manila queries tutors on their local date when that date has already passed in Manila.
- Code:
```javascript
const todayKey = () => {
  const today = new Date()
  return `${today.getFullYear()}-${padNumber(today.getMonth() + 1)}-${padNumber(today.getDate())}`
}
```
- Suggested check: Validate dates using Manila timezone (UTC+8) or standard server time.

### [B-11] [MEDIUM] [E9] — Silent chat initialization failure in TutorDetails
- File: src/views/TutorDetails.vue:274-281
- What: If starting an inquiry/chat session fails, the error is caught and printed to the console but no toast notification or modal feedback is presented to the user, leaving them stuck.
- Trigger: Click on the "Message" icon when the chat service is down or authentication has expired.
- Code:
```javascript
const openChat = async () => {
  try {
    const room = await chatStore.startInquiry(tutorID)
    router.push({ name: 'chat', query: { room: room.id } })
  } catch (error) {
    console.error('Failed to open chat:', error)
  }
}
```
- Suggested check: Push an error toast to inform the user that the chat session could not be opened.

### [B-12] [LOW] [E4] — Client local time is used to disable past times in BookingTimePicker
- File: src/components/BookingTimePicker.vue:160-166
- What: The check to disable past time slots (`isPastSlot`) compares slots against the client's current local time, which allows users in earlier timezones to select and submit booking requests for time slots that have already passed in Manila.
- Trigger: A user in a timezone behind Manila views available times for the current date, and selects a time that has already passed in Manila but is still in the future in their local timezone.
- Code:
```javascript
const isPastSlot = (slotValue) => {
  if (props.selectedDate !== todayKey()) {
    return false
  }

  return timeToMinutes(slotValue) < getCurrentComparableMinutes()
}
```
- Suggested check: Use Manila timezone (UTC+8) to compute the current date and time when disabling past slots.

---

## Pass C — Backend Endpoints

### [C-01] [CRITICAL] [E5] — Privilege escalation via unvalidated role at registration
- File: backend/studybuddy/views.py:784
- What: A registering user can specify any role (such as 'Admin' or 'SuperAdmin') and successfully register with that role because the registration view does not restrict role input.
- Trigger: Calling the registration endpoint with `"role": "Admin"` or `"role": "SuperAdmin"`.
- Code:
```python
    role = request.data.get('role')
    institution_id = request.data.get('institution_id')
```
- Suggested check: Restrict the allowed registration roles to only 'Tutor' and 'Tutee'.

### [C-02] [CRITICAL] [E10] — Unhandled API exception in cashout requests can leak wallet balance
- File: backend/studybuddy/views.py:4133
- What: A network timeout or other non-`PayMongoCashOutError` exception during the external cash-out call will crash the endpoint and leave the tutor's wallet balance permanently deducted without triggering a reversal.
- Trigger: A connection timeout or non-PayMongo error occurs during `create_wallet_transaction`.
- Code:
```python
    try:
        provider_data = create_wallet_transaction(
            settings.PAYMONGO_WALLET_ID,
            payout_account,
            amount,
            rail,
            get_cashout_callback_url(request),
            withdrawal.id,
        )
    except PayMongoCashOutError as exc:
```
- Suggested check: Catch all exceptions during the API call and trigger the reversal process to refund the tutor.

### [C-03] [HIGH] [E5] — Pending tutors bypass screening approval
- File: backend/studybuddy/views.py:984
- What: Tutor applications are not checked for approval before allowing tutors to set availability, get recommended, and accept bookings.
- Trigger: A tutor registers, and while their application is still pending, they log in and set up their profile.
- Code:
```python
    # 🔥 Check tutor application status
    if profile.role == 'Tutor':
        try:
            application = profile.tutor_application
            if application.application_status == 'rejected':
```
- Suggested check: Verify that the tutor application status is 'approved' before allowing them to access tutor-specific features, be recommended, or be booked.

### [C-04] [HIGH] [E5] — Tutor functions accessible by tutees without authorization
- File: backend/studybuddy/views.py:3038
- What: Tutor-specific endpoints do not verify if the authenticated user's profile is actually a Tutor, causing `Tutor.DoesNotExist` 500 errors or unauthorized actions.
- Trigger: A user with a 'Tutee' profile calls a tutor-specific endpoint like `/api/tutor/setup/`.
- Code:
```python
@api_view(['POST'])
def tutor_setup(request):

    profile = request.user.userprofile
    tutor = Tutor.objects.get(profile=profile)
```
- Suggested check: Implement permission checks (e.g. `IsTutor`) or handle `Tutor.DoesNotExist` to reject non-tutor users.

### [C-05] [HIGH] [E6] — State machine bypass on withdrawal requests
- File: backend/studybuddy/admin_views.py:109
- What: Admins can update the status of a withdrawal request even if it is already in a terminal state (processed, rejected, failed), allowing inconsistent transitions like rejected-to-processed.
- Trigger: An admin patches a completed or rejected withdrawal request to a different state.
- Code:
```python
        withdrawal.status = new_status
        if failure_reason:
            withdrawal.failure_reason = failure_reason
```
- Suggested check: Enforce that withdrawal requests in terminal states cannot be modified.

### [C-06] [HIGH] [E7] — Concurrent status updates on withdrawals can cause double-action
- File: backend/studybuddy/admin_views.py:102
- What: The withdrawal detail patch view does not lock the `WithdrawalRequest` object using `select_for_update()`, allowing concurrent status transitions (e.g. 'rejected' and 'processed' simultaneously) to conflict.
- Trigger: Concurrent HTTP PATCH requests on the same withdrawal request ID.
- Code:
```python
    def patch(self, request, pk):
        queryset = self.get_queryset_for_user(request, WithdrawalRequest.objects.all(), user_path='tutor__profile')
        withdrawal = get_object_or_404(queryset, pk=pk)
```
- Suggested check: Wrap the retrieval and update of the withdrawal request in a transaction block with `.select_for_update()`.

### [C-07] [HIGH] [E3] — Money calculation crash on null hourly rate
- File: backend/studybuddy/views.py:4196
- What: Calculating the booking total for a tutor who has no hourly rate set raises a `decimal.InvalidOperation` crash during Decimal conversion.
- Trigger: Booking a tutor whose `hourly_rate` is `None`.
- Code:
```python
    total_amount = decimal.Decimal(str(representative_booking.tutor.hourly_rate)) * decimal.Decimal(
        str(duration_hours)
    )
```
- Suggested check: Ensure `hourly_rate` is not null or default to a fallback before conversion.

### [C-08] [HIGH] [E3] — Commission leak on GCASH and BANK payments
- File: backend/studybuddy/views.py:4438
- What: Direct payment methods like `GCASH` and `BANK` bypass the commission deduction logic entirely, leading to unpaid platform commissions for tutors.
- Trigger: A booking using GCASH or BANK payment method is completed.
- Code:
```python
        if payment.method.code in PAYMONGO_SETTLED_CODES:
            ...
        elif payment.method.code == 'CASH':
            ...
```
- Suggested check: Treat GCASH and BANK manual payments the same as CASH for commission deductions.

### [C-09] [HIGH] [E1] — Null pointer crash on deleted payment methods in credit_tutor_wallet
- File: backend/studybuddy/views.py:4438
- What: If the payment method associated with a completed session has been deleted, `payment.method` is `None` (due to `SET_NULL`), raising an `AttributeError` when checking `.code`.
- Trigger: Accessing `payment.method.code` when `payment.method` is `None`.
- Code:
```python
        if payment.method.code in PAYMONGO_SETTLED_CODES:
```
- Suggested check: Guard against `payment.method` being null before accessing `.code`.

### [C-10] [HIGH] [E1] — Null pointer crash in support ticket resolution when chatroom is deleted
- File: backend/studybuddy/views.py:4657
- What: Resolving or claiming a support ticket when its associated chatroom has been deleted (causing `ticket.chatroom` to be `None` due to `SET_NULL`) causes a crash.
- Trigger: Admin claims or resolves a support ticket whose chatroom is null.
- Code:
```python
    Message.objects.create(
        room=ticket.chatroom,
        sender=None,
        content="This support ticket has been marked as Resolved. The chat is now closed."
    )
```
- Suggested check: Guard against `ticket.chatroom` being `None` before referencing it.

### [C-11] [MEDIUM] [E5] — Missing permission classes on registration and public endpoints
- File: backend/studybuddy/views.py:773
- What: Public and authenticated endpoints are missing the `@permission_classes` decorator, which defaults to DRF's global permission class (and can cause unexpected access denials or AttributeErrors if defaults change).
- Trigger: Accessing these endpoints when global permission settings differ or default to restricted.
- Code:
```python
@api_view(['POST'])
@authentication_classes([])
@throttle_classes([LoginRateThrottle])
@transaction.atomic
def register_user(request):
```
- Suggested check: Explicitly specify `@permission_classes` on all endpoints.

### [C-12] [MEDIUM] [E6] — State machine transition bypass in tutor application resubmission
- File: backend/studybuddy/views.py:4680
- What: Approved tutors can resubmit their tutor application, resetting their status back to 'pending', which is an invalid state transition for already-approved tutors.
- Trigger: An approved tutor calls the `/api/tutor/application/resubmit/` endpoint.
- Code:
```python
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def tutor_application_resubmit(request):
```
- Suggested check: Verify that the current application status is 'rejected' or 'pending' before allowing resubmission.

### [C-13] [MEDIUM] [E8] — Input validation crash in confirm_payment_and_book with non-list slots
- File: backend/studybuddy/views.py:1926
- What: The `confirm_payment_and_book` endpoint assumes `slots` is a list/iterable of dicts, and will crash with an `AttributeError` if `slots` is a dictionary.
- Trigger: Sending a payload where `slots` is a dictionary instead of a list.
- Code:
```python
    requested_dates = {
        parse_request_date(slot.get("session_date"))
        for slot in slots
    }
```
- Suggested check: Check that `slots` is a list before iterating and querying.

### [C-14] [MEDIUM] [E8] — Input validation crash with duplicate booking slots
- File: backend/studybuddy/views.py:1965
- What: Submitting duplicate slots in a single booking request bypasses the initial conflict check but triggers a database `IntegrityError` (500) upon saving due to unique constraints.
- Trigger: Booking request payload contains the same slot twice in the `slots` array.
- Code:
```python
    with transaction.atomic():
        for slot in slots:
            availability = get_object_or_404(
```
- Suggested check: Ensure that the list of slots contains unique availability IDs.

### [C-15] [MEDIUM] [E9] — Unhandled DoesNotExist in setup_profile
- File: backend/studybuddy/views.py:3279
- What: Setting up a profile with a non-existent course code raises an unhandled `Course.DoesNotExist` exception and returns a 500 error instead of a client error.
- Trigger: Sending a POST to `/api/profile/setup/` with a non-existent course code.
- Code:
```python
    if course_code:
        course = Course.objects.get(course_code=course_code)
        profile.course = course
```
- Suggested check: Use `get_object_or_404` or catch the `Course.DoesNotExist` exception.

### [C-16] [LOW] [E8] — Input validation crash on numeric query parameters
- File: backend/studybuddy/views.py:1759
- What: The `tutor_availability` endpoint directly converts `month_offset` to an integer without catching `ValueError`, resulting in a 500 error if a non-numeric string is sent.
- Trigger: Accessing `/api/tutor/availability/<id>/?month_offset=abc`.
- Code:
```python
    month_offset = int(request.GET.get("month_offset", 0))
```
- Suggested check: Safely parse `month_offset` or catch `ValueError`.

---

## Pass D — Recommender & Chat

### [D-01] [MAJOR] [E6] — Cold-start CF penalty in hybrid prediction
- File: backend/studybuddy/recommender/hybrid.py:28-31
- What: Setting `cf_score = 0` when collaborative filtering data is missing penalizes the tutor's hybrid score instead of falling back to CBF.
- Trigger: A tutor has no collaborative filtering data (e.g. cold start), causing `cf_score` to be `None`.
- Code:
```python
    if cf_score is None:
        cf_score = 0

    hybrid_score = (0.7 * cbf_score) + (0.3 * (cf_score / 5))
```
- Suggested check: Check if `cf_score` is None and fall back to the `cbf_score` entirely or reweight the hybrid formula instead of setting it to 0.

### [D-02] [MAJOR] [E1] — False course similarity match for missing courses
- File: backend/studybuddy/recommender/cbf.py:67-74
- What: If both the student and the tutor have no course assigned, they will receive a similarity score of 1, which falsely implies a perfect course match.
- Trigger: Both `student_course` and `tutor_course` are `None`.
- Code:
```python
    if student_course == tutor_course:
        s_course = 1
    elif (
        student_course
        and tutor_course
        and student_course.strand == tutor_course.strand
    ):
```
- Suggested check: Ensure `student_course` and `tutor_course` are not None before assessing course equality.

### [D-03] [MAJOR] [E6] — Incorrect SHS teaching level matching for college students
- File: backend/studybuddy/recommender/cbf.py:84-85
- What: College student year levels (1 to 4) are less than 12, so they bypass this check and receive a perfect teaching level similarity score of 1, matching them incorrectly with SHS tutors.
- Trigger: A college student has `year_level` 1-4 and the tutor has `teaching_level` "SHS".
- Code:
```python
    if tutor_level == "SHS" and student_year is not None and int(student_year) > 12:
        s_level = 0
```
- Suggested check: Normalize or translate the student year levels and tutor teaching levels to a comparable domain before evaluating the condition.

### [D-04] [MAJOR] [E3] — ZeroDivisionError on empty student ratings
- File: backend/studybuddy/recommender/CF.py:99
- What: Accessing the length of an empty dictionary will cause `len(ratings[student_id])` to be 0, triggering a `ZeroDivisionError`.
- Trigger: A student is present in the `ratings` dictionary but has no ratings (empty dictionary).
- Code:
```python
    student_avg = sum(ratings[student_id].values()) / len(ratings[student_id])
```
- Suggested check: Add a guard to verify `len(ratings[student_id])` is greater than 0 before performing division.

### [D-05] [MAJOR] [E3] — ZeroDivisionError on empty neighbor ratings
- File: backend/studybuddy/recommender/CF.py:106
- What: Accessing the length of an empty dictionary for a neighbor will cause `len(ratings[neighbor])` to be 0, triggering a `ZeroDivisionError`.
- Trigger: A neighbor is present in the `ratings` dictionary but has no ratings (empty dictionary).
- Code:
```python
        neighbor_avg = sum(ratings[neighbor].values()) / len(ratings[neighbor])
```
- Suggested check: Ensure that `ratings[neighbor]` has a length greater than 0 before division.

### [D-06] [CRITICAL] [E9] — Secondary crash in get_sender_info error handler
- File: backend/studybuddy/chat/consumers.py:120-121
- What: If `user.userprofile` fails (such as for `AnonymousUser`), the exception handler attempts to access `user.email`. Since `AnonymousUser` does not have an `email` attribute, it raises a secondary `AttributeError` which crashes the call.
- Trigger: `get_sender_info` is called with an `AnonymousUser` object.
- Code:
```python
        except Exception:
            return {
                'name': user.email,
                'profile_id': None
            }
```
- Suggested check: Avoid accessing the non-existent `user.email` attribute on `AnonymousUser` by returning a default name like "Anonymous" or "System".

### [D-07] [MAJOR] [E9] — Unhandled JSONDecodeError on malformed text frame
- File: backend/studybuddy/chat/consumers.py:46-47
- What: If `json.loads(text_data)` raises `JSONDecodeError`, the error goes uncaught, causing the WebSocket task to crash and close unexpectedly.
- Trigger: The WebSocket client sends a text frame that is not valid JSON.
- Code:
```python
    async def receive(self, text_data):
        data = json.loads(text_data)
```
- Suggested check: Wrap the `json.loads` statement in a try-except block to gracefully catch and handle `json.JSONDecodeError`.

### [D-08] [MINOR] [E9] — AttributeError during WebSocket disconnect
- File: backend/studybuddy/chat/consumers.py:39-44
- What: `disconnect` accesses `self.room_group_name` directly without checking if the attribute exists, raising an `AttributeError` and causing the disconnection handler to crash.
- Trigger: Connection disconnects before `self.room_group_name` is defined in `connect`.
- Code:
```python
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
```
- Suggested check: Use `hasattr(self, 'room_group_name')` before invoking `group_discard`.

### [D-09] [MAJOR] [E7] — Concurrency race condition creating duplicate inquiry rooms
- File: backend/studybuddy/chat/services.py:21-27
- What: Both concurrent requests will query, find no room, and attempt to create one. Due to the database's `unique_inquiry_chat` constraint, one request will raise an unhandled `IntegrityError` and crash the transaction.
- Trigger: Two concurrent requests call `get_canonical_room` for the same `tutee` and `tutor` when no room exists.
- Code:
```python
def get_canonical_room(tutee, tutor):
    room = ChatRoom.objects.filter(tutee=tutee, tutor=tutor, booking__isnull=True).first()

    if room:
        return room

    return ChatRoom.objects.create(tutee=tutee, tutor=tutor, booking=None)
```
- Suggested check: Wrap the room creation in a transaction block or try-except to catch `IntegrityError`, or use Django's atomic `get_or_create`.

### [D-10] [MAJOR] [E4] — Default active timezone used instead of Manila timezone
- File: backend/studybuddy/chat/services.py:204-205
- What: `timezone.make_aware` converts the naive datetime to the default timezone instead of the user's local or Manila timezone, causing session states to transition to "Ongoing", "Upcoming", or "Payment Required" at incorrect times.
- Trigger: Standard default timezone is active (such as UTC) when resolving session times.
- Code:
```python
            session_naive = datetime.combine(booking.session_date, booking.availability.time_slot)
            session_start = timezone.make_aware(session_naive)
```
- Suggested check: Pass the correct timezone (such as the Manila timezone) explicitly to `timezone.make_aware` to ensure status transitions align with local time.

### [D-11] [MINOR] [E1] — Unhandled AttributeError when tutee is None in participant IDs
- File: backend/studybuddy/chat/services.py:34-39
- What: The code directly accesses `room.tutee.user_id` without verifying if `room.tutee` is `None`, which will raise an `AttributeError` and crash.
- Trigger: `get_participant_user_ids` is called on a room where `tutee` is `None`.
- Code:
```python
def get_participant_user_ids(room):
    return [
        user_id
        for user_id in [room.tutee.user_id, room.tutor.user_id if room.tutor else None]
        if user_id
    ]
```
- Suggested check: Verify `room.tutee` is not None before attempting to access `room.tutee.user_id`.

### [D-12] [MINOR] [E9] — Unhandled DoesNotExist exceptions on missing tutor profile
- File: backend/studybuddy/chat/services.py:703-706
- What: The function queries `UserProfile` and `Tutor` without any try-except blocks, causing a crash with `DoesNotExist` or `ValueError` exceptions if entities are missing.
- Trigger: `get_room_for_tutor_profile` is called with a non-existent or invalid tutor profile ID.
- Code:
```python
def get_room_for_tutor_profile(tutee_profile, tutor_profile_id):
    tutor_profile = UserProfile.objects.get(id=tutor_profile_id, role='Tutor')
    tutor = Tutor.objects.get(profile=tutor_profile)
    return get_canonical_room(tutee_profile, tutor.profile)
```
- Suggested check: Wrap database retrievals in try-except blocks for `DoesNotExist` to prevent unhandled 500 errors.

---

## UNCERTAIN (need a human to look)

### [U-01] [CRITICAL] [E7: Concurrency/double-action] — Non-Atomic Withdrawal API Call Can Leave Funds Stuck
- File: backend/studybuddy/views.py:4124-4132
- What: The external request to `create_wallet_transaction` is executed outside the Django database transaction that deducts the tutor's wallet balance. If the external call raises a network or timeout exception, the withdrawal is left in 'pending' status while the tutor's balance remains deducted with no automatic reversal triggered.
- Trigger: A network timeout occurs during the external PayMongo transaction call.
- Code:
```python
    try:
        provider_data = create_wallet_transaction(
            settings.PAYMONGO_WALLET_ID,
            payout_account,
            amount,
            rail,
            get_cashout_callback_url(request),
            withdrawal.id,
        )
```
- Suggested check: Wrap the API request in a connection/timeout-handling try-except block that triggers `reverse_failed_cash_out` on any general `requests` library failures.

### [U-02] [HIGH] [E5: Auth/permission] — Webhook Verification Bypassed When Shared Secret is Unconfigured
- File: backend/studybuddy/views.py:4154-4160
- What: If `PAYMONGO_CASHOUT_CALLBACK_SECRET` is not set in Django settings, the PayMongo cashout callback verification is skipped entirely, allowing any unauthorized agent to post fake transaction status updates.
- Trigger: The backend receives an unauthenticated webhook request when the secret setting is empty.
- Code:
```python
    secret = getattr(settings, 'PAYMONGO_CASHOUT_CALLBACK_SECRET', '')
    if secret:
        provided = request.query_params.get('token', '')
        if not constant_time_compare(provided, secret):
            logger.warning("Rejected PayMongo cashout callback: invalid or missing token.")
            return Response({"error": "Unauthorized."}, status=status.HTTP_403_FORBIDDEN)
```
- Suggested check: Enforce signature/token verification unconditionally and fail the request if the secret configuration is missing.

### [U-03] [LOW] [E1] — Write-only BookedSessionDetails store
- File: src/stores/bookedSessionDetails.js:4-34
- What: The `bookedSessionDetails` store is written to in `FindTutors.vue` and `TutorDetails.vue`, but none of its properties are ever read anywhere in the application.
- Trigger: N/A
- Code:
```javascript
export const useBookedSessionStore = defineStore('bookedSessionDetails', () => {

    const bookedSessionTutorID = ref(null)
    const bookedSessionTutorName = ref('')
```
- Suggested check: Audit the application to see if `bookedSessionDetails` was intended to be used on the dashboard or checkout pages, or clean up the dead store code if it's no longer needed.

### [U-04] [LOW] [E6] — Missing state persistence in paymentStore
- File: src/stores/tuteePaymentDetails.js:4-22
- What: The payment store does not persist its selected method or receipt image state, meaning a browser refresh on the post-session payment screen will clear all user selections and uploaded receipts.
- Trigger: Refreshing the page during post-session payment.
- Code:
```javascript
export const usePaymentStore = defineStore('payment', () => {
  const selectedMethod = ref(null)
  const amountPaid = ref(null)
  const receiptImage = ref(null)
```
- Suggested check: Consider adding sessionStorage persistence to the payment store if keeping the selected payment method across accidental reloads is desired.

### [U-05] Lack of PayMongo Signature Verification Fallback
- File: backend/studybuddy/views.py:4154
- What: When `PAYMONGO_CASHOUT_CALLBACK_SECRET` is not set, signature token verification is skipped entirely, allowing any sender to trigger callbacks. We are uncertain if signature header validation is supposed to be implemented here rather than query param token check.
- Trigger: PayMongo callback is received and no callback secret is configured.
- Code:
```python
    secret = getattr(settings, 'PAYMONGO_CASHOUT_CALLBACK_SECRET', '')
    if secret:
        provided = request.query_params.get('token', '')
        if not constant_time_compare(provided, secret):
```
- Suggested check: Always enforce signature verification, or require signature checking on the header rather than query parameters.

### [U-06] Redundant is_booked boolean flag on TutorAvailability model
- File: backend/studybuddy/models.py:450
- What: The `TutorAvailability` model contains an `is_booked` boolean flag labeled "system controls this". However, booking logic is date-specific and handled by the `Booking` model, making `is_booked` on the weekly template redundant and potentially confusing if left unused.
- Trigger: Normal system execution where availability is booked.
- Code:
```python
    is_booked = models.BooleanField(default=False)   # system controls this
```
- Suggested check: Remove `is_booked` from `TutorAvailability` if it has been replaced by date-specific `Booking` constraints.

### [U-07] [INFO] [E8] — Type mismatch of requested_subject parameter in CBF score
- File: backend/studybuddy/recommender/cbf.py:38-39
- What: If `requested_subject` is a model instance, appending it to the string-based list `subject_codes` will cause later expertise comparisons to fail, but it is uncertain if callers always pass a string.
- Trigger: `requested_subject` is passed as a `Subject` model object rather than a string code.
- Code:
```python
    if requested_subject and requested_subject not in subject_codes:
        subject_codes.append(requested_subject)
```
- Suggested check: Verify or convert `requested_subject` to its code string (e.g. `requested_subject.subject_code`) before adding it to `subject_codes`.
