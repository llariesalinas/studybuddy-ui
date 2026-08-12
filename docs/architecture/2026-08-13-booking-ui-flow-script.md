# Demo Script — Booking UI Flow (Tutee & Tutor)

A spoken walkthrough script for demonstrating the end-to-end booking process. Each beat has
**On screen** (what to click) and **Say** (what to narrate). Total runtime ≈ 10–12 minutes;
the trimmed version (Acts 1–3 only) runs ≈ 6 minutes.

Source of truth for the mechanics: [booking-flow.md](booking-flow.md) and
[ADR-0008](../adr/0008-instant-booking-replaces-request-to-book.md).

---

## Before you present

**Two browsers, side by side.** Left = tutee account, right = tutor account. Log both in before
you start — nobody wants to watch a login form.

**Preconditions to set up:**
- The tutor is verified, has a non-negative wallet, is under the session load limit, and has
  published availability inside the next 14 days.
- The tutee has no active strikes.
- Pick a subject you know the tutor teaches, so the search returns them on page one.

**One line to open with, before any clicking:**

> "The booking process is four screens for the tutee and zero approval screens for the tutor.
> That second part is the design decision I'll defend at the end."

---

## Act 0 — The tutor publishes availability (30 sec, tutor side)

This is the precondition, not part of booking proper. Show it briefly so the calendar the tutee
sees later isn't magic.

**On screen:** Tutor browser → `/tch-availability` (Availability in the sidebar).

**Say:**
> "This is Weekly Availability. The tutor blocks out recurring 30-minute slots — 'Add Weekly Slot',
> pick a start and end time, save. They can also block an individual day off.
>
> Two things to notice. First, availability is *recurring*, so the tutor sets it once rather than
> re-publishing every week. Second, because it's recurring, it can go stale — a tutor who set this
> in March is still 'available' in August. We bound that with a 14-day Booking Horizon: nothing can
> be booked more than two weeks out. That's the guardrail instead of nagging tutors to reconfirm."

---

## Act 1 — The tutee books (4 min, tutee side)

### Beat 1 — Preferences (`/dashboard`, InitialBooking form)

**On screen:** Tutee dashboard. The booking form is embedded at the top — not a separate route.

Fill it in while narrating: Subject → Date → Preferred Mode → Time range → Budget slider.

**Say:**
> "The tutee starts on their dashboard. Booking is the first thing on it — it's the primary job of
> the app, so it isn't buried behind a menu.
>
> Subject opens a picker built on the taxonomy — six categories, and a search box that also matches
> an admin-curated keyword field, so a tutee typing 'calculus' still lands on the right subject even
> if that isn't its exact name.
>
> Date, then Preferred Mode — Online or Face-to-face. Watch what happens when I pick Face-to-face:
> a location field appears, and it first asks inside or outside campus. Online doesn't ask, because
> the system generates the meeting link itself.
>
> Time is deliberately optional. If the tutee has no constraint, we'd rather show them more tutors
> than force a filter they don't care about.
>
> Budget is a range, in pesos per hour. Then — Find Tutor."

*Click **Find Tutor**.*

### Beat 2 — Search results (`/find-tutors`)

**On screen:** The tutor list.

**Say:**
> "These aren't filtered results in a database sense — they're ranked by the recommender, which
> weighs subject match, availability overlap, rating and price fit.
>
> The important thing for the booking flow is who is *missing* from this list. A tutor who isn't
> verified, has a negative wallet balance, is at their session load limit, or is carrying three
> active strikes doesn't appear here at all. We gate at search visibility rather than at booking
> time, so the tutee never picks someone only to get rejected later."

*Click a tutor card.*

### Beat 3 — Slot selection (`/tutor/:id`)

**On screen:** Tutor profile with the week calendar. Click one slot, then an adjacent one.

**Say:**
> "The tutor's profile, and their live availability for the week. Grey slots are already booked.
>
> I'll select a slot — and a second one next to it. Two rules are enforced here in the UI: slots
> must be on the same day, and they must be contiguous. You can't book 9am and then 3pm as one
> session, because that's two sessions.
>
> On the right, the estimated total updates live — slots, times half an hour, times the hourly rate.
> No surprise at checkout.
>
> The button now says Confirm Booking. Before I press it, note what it does *not* say. It doesn't
> say 'Send Request'."

### Beat 4 — Confirm (`POST bookings/confirm/`)

*Press **Confirm Booking**. Land back on the dashboard with the session now listed.*

**Say:**
> "That's it. The session is Confirmed — not Pending. There is no tutor approval step in this system.
>
> Behind that one click the server did five things: it re-checked every tutor gate as an
> authoritative backstop, generated a meeting link for the session group if it's online, opened a
> chat room between the two with a neutral system message, notified the tutor in-app, and emailed
> them.
>
> And it enforced the Booking Horizon — a date more than 14 days out is rejected here regardless of
> what the calendar rendered."

---

## Act 2 — What the tutor sees (1.5 min, tutor side)

**On screen:** Switch to the tutor browser. Refresh the dashboard — the new session is there.

**Say:**
> "Same moment, tutor's screen. The session is already on their Full Schedule. They didn't accept
> anything, because there's nothing to accept.
>
> This is the design decision the panel pushed us toward, and it's worth stating the trade-off
> honestly: the tutor loses the ability to vet a tutee before committing. We considered keeping a
> per-tutor opt-in toggle and rejected it, because two coexisting booking models means the tutee
> never knows which one they're in — the confirmation delay survives for every tutor who opts out.
>
> What replaces pre-approval is post-hoc accountability, and there are two pieces of it on this
> screen."

*Click into the session → `/booking-details/:id`.*

**Say:**
> "One: chat. It's already open, created at confirmation. If the tutor has a question about scope
> or the tutee's level, that conversation happens here instead of blocking the booking.
>
> Two: the tutor can cancel, self-serve, and the screen tells them exactly what it costs. Penalty-free
> up to 12 hours before the session — we call that the Grace Cutoff. After it, they can still cancel;
> it just carries a consequence. I'll show that path at the end.
>
> Notice the tutor is never *blocked* from cancelling. A hard block turns an honest late cancellation
> into a silent no-show, which is strictly worse for the tutee."

---

## Act 3 — Session day (2 min, both sides)

**On screen:** Tutee session details (`/tuteeSessionDetails/:id`) and tutor booking details side by side.

**Say:**
> "As the session approaches, both detail screens change state. The countdown bar goes live, the
> status flips to Happening now, and the action rail promotes whatever the next action actually is —
> join the meeting link if it's online, or the location if it's face-to-face.
>
> Both sides see the same session facts — subject, date, time, mode, location, status — so there's
> no version of the truth that only one party has."

*Trigger the check-in modal (or show it from the QA panel).*

**Say:**
> "Mid-session, both sides get a check-in prompt: 'How is the session going so far?' — everything on
> track, or having issues.
>
> This is our substitute for supervision. Nobody is watching the session, so we sample it from both
> ends. A tutee reporting issues while the session is still running gives support something to act
> on *before* it becomes a dispute afterward."

---

## Act 4 — After the session (1.5 min)

**On screen:** Tutee side → status becomes Payment required → action rail → `/payment-tutee/:bookingId`.

**Say:**
> "When the session ends, the tutee's screen moves to Payment required and the rail's next action
> routes them to payment. They see the session summary, choose a payment method, and upload a receipt
> image.
>
> Payment is deliberately *after* the session, not before. Charging up front for a service that
> hasn't happened yet creates a refund problem on every cancellation, and we already have a
> cancellation policy to enforce — we didn't want to run a refund policy alongside it."

**On screen:** Tutor side → `/tch-wallet`.

**Say:**
> "On the tutor's side the earnings land in their wallet, minus platform commission, and they cash
> out from here. The wallet also feeds back into booking: a negative balance is one of the gates
> that hides a tutor from search."

---

## Act 5 — The exception path: late cancellation (1.5 min)

Show this only if you have time — but have it ready, because it is the most likely question.

**On screen:** A session inside 12 hours. Press Cancel Session; the warning modal appears.

**Say:**
> "Here's the same cancel button on a session that's less than 12 hours away. The modal names the
> cutoff and names the consequence — it doesn't just say 'are you sure'.
>
> Confirming cancels the session immediately and auto-opens a support ticket. The system is the
> reporter, not a person; nobody has to file a complaint.
>
> That strike counts *provisionally*, from the moment the ticket opens, before any admin has looked
> at it. An admin then resolves it: excused, which relieves the strike, or counted, which for a tutor
> also triggers a flat ₱50 wallet deduction.
>
> Three active strikes in a rolling 14-day window suspends a tutee from booking, or hides a tutor
> from search. Each strike expires on its own, 14 days after it was issued — so this is a cooling-off
> mechanism, not a permanent record."

---

## Closing line

> "So: four screens to book, zero to approve. The confirmation layer we removed was protecting the
> tutor from bad bookings — we replaced it with chat before the session, a penalty-free cancellation
> window, and a strike system after it. The tutee gets a booking that's actually booked, and the
> tutor keeps a way out that's honest about what it costs."

---

## Likely questions, short answers

**"What stops a tutee from booking a tutor who can't actually teach them?"**
Four gates, all enforced twice — once by hiding the tutor from search, once server-side at confirm:
verification, non-negative wallet, session load limit, strike cap.

**"What if the tutor's availability is stale?"**
The 14-day Booking Horizon. Nothing can be booked further out than that, so a stale recurring
schedule can only be wrong for two weeks, not indefinitely.

**"Why not require admin approval before a late cancellation?"**
Because it depends on an admin being awake. If no one is online, the cancellation doesn't happen —
it becomes a no-show, and the tutee finds out by sitting alone in a meeting room. We let the
cancellation through and review it after.

**"Can a tutor refuse a specific tutee?"**
Not before the booking. They can cancel, penalty-free if it's more than 12 hours out. That's a
deliberate trade — it's stated as a known cost in ADR-0008, not an oversight.

**"Who generates the meeting link?"**
The server, at confirmation, one per session group. Neither party types a link, so neither party can
send the other somewhere unexpected.
