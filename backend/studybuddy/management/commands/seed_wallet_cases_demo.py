"""Restore the Isabel Fernandez / Miguel Torres wallet-states demo case lost in the
2026-07-16 taxonomy reseed (see docs/architecture/demo-data-testing-accounts.html,
"No Longer Seeded").

Creates two brand-new tutors from scratch:
  - Isabel Fernandez: one WalletTopUp row per state (paid/pending/failed) and one
    WithdrawalRequest row per state (pending/processed/rejected/failed/flagged), each
    with the Transaction row(s) the real request_withdrawal/cash_outs/
    admin_resolve_ticket code paths would have written, reconciling to a round
    TARGET_BALANCE.
  - Miguel Torres: Wallet.balance forced negative by a single counted_strike
    Transaction (the ADR-0008 Late Cancellation wallet-deduction path, sized via the
    same COUNTED_STRIKE_WALLET_DEDUCTION views.py uses) -- a Transaction row only, no
    backing SupportTicket/cancelled Booking, since the debt banner
    (views.wallet_negative) only reads Wallet.balance. Plus CASH_PAYMENT_COUNT
    completed cash-paid Booking/Payment rows for cash-payment history.

Deliberately additive and reversible: creates nothing but the two tutors, one shared
seed tutee to own Miguel's bookings, and everything that cascades from those three
profiles. --remove deletes all of it. Does not reseed and never touches
seed_data.py's fixed-seed output.
"""
import datetime
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from studybuddy.models import (
    Booking,
    Course,
    PartnerInstitution,
    Payment,
    PaymentMethod,
    Subjects,
    Transaction,
    Tutor,
    TutorApplication,
    TutorAvailability,
    TutorSubjects,
    UserProfile,
    Wallet,
    WalletTopUp,
    WithdrawalRequest,
)
from studybuddy.views import COUNTED_STRIKE_WALLET_DEDUCTION, get_cashout_provider_fee

PASSWORD = 'studybuddy123'
INSTITUTION_DOMAIN = 'cpu.edu.ph'
PLACEHOLDER_SCHOOL_ID = 'demo/placeholder_school_id.png'
PLACEHOLDER_ENROLLMENT_PROOF = 'demo/placeholder_enrollment_proof.pdf'

ISABEL_USERNAME = 'isabel.fernandez.demo@cpu.edu.ph'
ISABEL_FNAME, ISABEL_LNAME = 'Isabel', 'Fernandez'
MIGUEL_USERNAME = 'miguel.torres.demo@cpu.edu.ph'
MIGUEL_FNAME, MIGUEL_LNAME = 'Miguel', 'Torres'

SEED_TUTEE_USERNAME = 'walletcases.demo@cpu.edu.ph'
SEED_TUTEE_FNAME, SEED_TUTEE_LNAME = 'WalletCases', 'Demo'

# Isabel's ledger amounts. Chosen so the balance reconciles to a round TARGET_BALANCE:
# paid top-up credits ISABEL_PAID_TOPUP; the pending/processed/flagged withdrawals debit
# on request (like the real cash_outs view) and are never reversed; the rejected/failed
# withdrawals debit on request and are fully reversed (net zero), same as
# admin_resolve_ticket / reverse_failed_cash_out. The flagged amount is solved for below
# rather than hardcoded, so a change to the provider fee still reconciles exactly.
TARGET_BALANCE = Decimal('500.00')
ISABEL_PAID_TOPUP = Decimal('1000.00')
ISABEL_PENDING_TOPUP = Decimal('300.00')
ISABEL_FAILED_TOPUP = Decimal('200.00')
ISABEL_PENDING_WITHDRAWAL = Decimal('100.00')
ISABEL_PROCESSED_WITHDRAWAL = Decimal('250.00')
ISABEL_REJECTED_WITHDRAWAL = Decimal('80.00')
ISABEL_FAILED_WITHDRAWAL = Decimal('60.00')

CASH_PAYMENT_COUNT = 3
CASH_PAYMENT_SPACING_DAYS = 7  # sessions dated 7/14/21 days ago

AVAILABILITY_DAY = 'Mon'
AVAILABILITY_START_HOUR = 8
WEEKDAY_NAMES = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']


class Command(BaseCommand):
    help = (
        'Seed Isabel Fernandez (full wallet-state ledger, reconciled balance) and '
        'Miguel Torres (forced-negative wallet, cash-payment history) to demo wallet '
        'states. Use --remove to undo.'
    )

    def add_arguments(self, parser):
        parser.add_argument('--remove', action='store_true',
                             help='Delete the two seeded tutors and the seed tutee.')

    def handle(self, *args, **options):
        if options['remove']:
            return self._remove()

        with transaction.atomic():
            institution = self._get_institution()
            course = self._get_course()
            subject = self._get_subject()
            cash_method = self._get_cash_payment_method()

            isabel, isabel_created = self._get_or_create_tutor(
                ISABEL_USERNAME, ISABEL_FNAME, ISABEL_LNAME, institution, course, subject,
                with_availability=False,
            )
            miguel, miguel_created = self._get_or_create_tutor(
                MIGUEL_USERNAME, MIGUEL_FNAME, MIGUEL_LNAME, institution, course, subject,
                with_availability=True,
            )

            if isabel_created:
                self._build_isabel_ledger(isabel)
            if miguel_created:
                self._apply_miguel_strike(miguel)
                seed_tutee = self._get_or_create_seed_tutee(institution, course)
                self._create_cash_payments(miguel, seed_tutee, subject, cash_method)

        self._print_summary(isabel, miguel)

    # ------------------------------------------------------------------ lookups

    def _get_institution(self):
        institution = PartnerInstitution.objects.filter(
            school_email_domain=INSTITUTION_DOMAIN,
        ).first()
        if institution is None:
            raise CommandError(
                'No PartnerInstitution for cpu.edu.ph found. Run `python manage.py '
                'seed_data` first.'
            )
        return institution

    def _get_course(self):
        course = Course.objects.filter(course_code='BSCS').first() or Course.objects.first()
        if course is None:
            raise CommandError('No Course found. Run `python manage.py seed_data` first.')
        return course

    def _get_subject(self):
        subject = (
            Subjects.objects.filter(subject_name='Python').first()
            or Subjects.objects.first()
        )
        if subject is None:
            raise CommandError('No Subjects found. Run `python manage.py seed_data` first.')
        return subject

    def _get_cash_payment_method(self):
        method = PaymentMethod.objects.filter(code='CASH').first()
        if method is None:
            raise CommandError(
                'No CASH PaymentMethod found. Run `python manage.py seed_data` first.'
            )
        return method

    # ------------------------------------------------------------------ creation

    def _get_or_create_seed_tutee(self, institution, course):
        profile = UserProfile.objects.filter(user__username=SEED_TUTEE_USERNAME).first()
        if profile:
            return profile

        user = User.objects.create_user(
            username=SEED_TUTEE_USERNAME, email=SEED_TUTEE_USERNAME, password=PASSWORD,
            first_name=SEED_TUTEE_FNAME, last_name=SEED_TUTEE_LNAME,
        )
        return UserProfile.objects.create(
            user=user, fname=SEED_TUTEE_FNAME, lname=SEED_TUTEE_LNAME, role='Tutee',
            course=course, year_level=1, institution=institution, profile_completed=True,
            bio='Holds seeded cash-paid bookings for the wallet-cases demo.',
        )

    def _get_or_create_tutor(self, username, fname, lname, institution, course, subject,
                              with_availability):
        existing_profile = UserProfile.objects.filter(user__username=username).first()
        if existing_profile:
            return Tutor.objects.get(profile=existing_profile), False

        now = timezone.now()
        user = User.objects.create_user(
            username=username, email=username, password=PASSWORD,
            first_name=fname, last_name=lname,
        )
        profile = UserProfile.objects.create(
            user=user, fname=fname, lname=lname, role='Tutor', course=course, year_level=3,
            institution=institution, profile_completed=True,
            bio=f'{fname} {lname} -- seeded for the wallet-cases demo.',
        )
        tutor = Tutor.objects.create(
            profile=profile, teaching_level='College', can_online=True, can_f2f=False,
            hourly_rate=300, response_time='within_a_day',
        )
        TutorApplication.objects.create(
            profile=profile, application_status='approved',
            school_id=PLACEHOLDER_SCHOOL_ID, enrollment_proof=PLACEHOLDER_ENROLLMENT_PROOF,
            submitted_at=now, updated_at=now, reviewed_at=now,
        )
        # Wallet.objects.get_or_create is unnecessary here -- Tutor's post_save signal
        # (create_tutor_wallet, models.py) already created it above.
        TutorSubjects.objects.create(tutor=tutor, subject=subject, expertise_level=4)

        if with_availability:
            for i in range(CASH_PAYMENT_COUNT):
                TutorAvailability.objects.create(
                    tutor=tutor, day=AVAILABILITY_DAY,
                    time_slot=self._hour_slot(AVAILABILITY_START_HOUR + i),
                    is_active=True, is_booked=False,
                )
        return tutor, True

    def _hour_slot(self, hour):
        return datetime.time(hour, 0)

    # ------------------------------------------------------------------ Isabel

    def _build_isabel_ledger(self, tutor):
        # Fetch fresh rather than tutor.wallet -- Tutor's post_save signal
        # (create_tutor_wallet, models.py) already created the Wallet at
        # Tutor.objects.create() time and cached it on the reverse accessor with the
        # DecimalField's raw float default, which blows up Decimal arithmetic below.
        wallet = Wallet.objects.get(tutor=tutor)
        now = timezone.now()

        # Top-ups: only the paid one lands on the wallet (cash_in), matching how a real
        # WalletTopUp only credits the balance once its provider callback marks it paid.
        WalletTopUp.objects.create(
            tutor=tutor, amount=ISABEL_PAID_TOPUP, status='paid', paid_at=now,
        )
        self._credit(wallet, 'cash_in', ISABEL_PAID_TOPUP, 'Wallet top-up', 'TOPUP-PAID')
        WalletTopUp.objects.create(tutor=tutor, amount=ISABEL_PENDING_TOPUP, status='pending')
        WalletTopUp.objects.create(tutor=tutor, amount=ISABEL_FAILED_TOPUP, status='failed')

        # Withdrawals: every request debits the wallet immediately (withdrawal +
        # cashout_fee, mirroring cash_outs in views.py); rejected/failed get reversed
        # (withdrawal_reversal + cashout_fee_reversal, mirroring
        # admin_resolve_ticket / reverse_failed_cash_out); pending/processed/flagged
        # stay debited.
        provider_fee = get_cashout_provider_fee()

        self._request_withdrawal(tutor, wallet, ISABEL_PENDING_WITHDRAWAL, 'pending')

        processed = self._request_withdrawal(
            tutor, wallet, ISABEL_PROCESSED_WITHDRAWAL, 'processed', provider_fee=provider_fee,
        )
        processed.processed_at = now
        processed.save(update_fields=['processed_at'])

        rejected = self._request_withdrawal(
            tutor, wallet, ISABEL_REJECTED_WITHDRAWAL, 'rejected',
        )
        self._reverse_withdrawal(wallet, rejected)

        failed = self._request_withdrawal(tutor, wallet, ISABEL_FAILED_WITHDRAWAL, 'failed')
        self._reverse_withdrawal(wallet, failed)

        # Flagged amount solved from the running balance rather than hardcoded, so the
        # ledger reconciles to TARGET_BALANCE even if provider_fee ever changes.
        flagged_amount = (wallet.balance - TARGET_BALANCE).quantize(Decimal('0.01'))
        if flagged_amount <= 0:
            raise CommandError(
                f'Isabel\'s ledger already at or below TARGET_BALANCE ({wallet.balance}) '
                'before the flagged withdrawal -- adjust the fixed amounts above.'
            )
        self._request_withdrawal(tutor, wallet, flagged_amount, 'flagged')

        if wallet.balance != TARGET_BALANCE:
            raise CommandError(
                f'Isabel\'s ledger reconciled to {wallet.balance}, expected {TARGET_BALANCE}.'
            )

    def _credit(self, wallet, transaction_type, amount, description, reference_id):
        wallet.balance += amount
        wallet.save(update_fields=['balance', 'last_updated'])
        Transaction.objects.create(
            wallet=wallet, transaction_type=transaction_type, amount=amount,
            description=description, reference_id=reference_id,
        )

    def _debit(self, wallet, transaction_type, amount, description, reference_id):
        wallet.balance -= amount
        wallet.save(update_fields=['balance', 'last_updated'])
        Transaction.objects.create(
            wallet=wallet, transaction_type=transaction_type, amount=-amount,
            description=description, reference_id=reference_id,
        )

    def _request_withdrawal(self, tutor, wallet, amount, status, provider_fee=Decimal('0.00')):
        withdrawal = WithdrawalRequest.objects.create(
            tutor=tutor, amount=amount, method='gcash', account_number='09171234567',
            account_name=f'{tutor.profile.fname} {tutor.profile.lname}', status=status,
            provider='paymongo', provider_fee=provider_fee, net_amount=amount - provider_fee,
        )
        self._debit(
            wallet, 'withdrawal', amount,
            'Cash-out request via GCash', f'WD-{withdrawal.id}',
        )
        if provider_fee > 0:
            self._debit(
                wallet, 'cashout_fee', provider_fee,
                f'Provider fee for cash-out request #{withdrawal.id}', f'WD-{withdrawal.id}-FEE',
            )
        return withdrawal

    def _reverse_withdrawal(self, wallet, withdrawal):
        self._credit(
            wallet, 'withdrawal_reversal', withdrawal.amount,
            f'Reversal of cash-out request #{withdrawal.id}', f'WD-{withdrawal.id}-REV',
        )
        if withdrawal.provider_fee > 0:
            self._credit(
                wallet, 'cashout_fee_reversal', withdrawal.provider_fee,
                f'Provider fee reversal for cash-out request #{withdrawal.id}',
                f'WD-{withdrawal.id}-FEE-REV',
            )

    # ------------------------------------------------------------------ Miguel

    def _apply_miguel_strike(self, tutor):
        # Fetch fresh rather than tutor.wallet -- Tutor's post_save signal
        # (create_tutor_wallet, models.py) already created the Wallet at
        # Tutor.objects.create() time and cached it on the reverse accessor with the
        # DecimalField's raw float default, which blows up Decimal arithmetic below.
        wallet = Wallet.objects.get(tutor=tutor)
        self._debit(
            wallet, 'counted_strike', COUNTED_STRIKE_WALLET_DEDUCTION,
            'Counted Strike Penalty for a Late Cancellation.', 'LT-DEMO',
        )

    def _create_cash_payments(self, tutor, seed_tutee, subject, cash_method):
        slots = list(TutorAvailability.objects.filter(tutor=tutor).order_by('time_slot'))
        if len(slots) < CASH_PAYMENT_COUNT:
            raise CommandError(
                f'{tutor.profile.fname} {tutor.profile.lname} only has {len(slots)} '
                f'availability slots, need {CASH_PAYMENT_COUNT}.'
            )

        today = timezone.localdate()
        for i, slot in enumerate(slots[:CASH_PAYMENT_COUNT]):
            session_date = today - timedelta(days=CASH_PAYMENT_SPACING_DAYS * (i + 1))
            booking = Booking.objects.create(
                student=seed_tutee, tutor=tutor, availability=slot, subject=subject,
                session_date=session_date, session_mode='Online', status='Completed',
                tutee_confirmed=True, tutor_confirmed=True,
            )
            Payment.objects.create(
                booking=booking, method=cash_method, amount=tutor.hourly_rate,
                payment_status='Paid', paid_at=timezone.now(),
            )

    # ------------------------------------------------------------------ output

    def _print_summary(self, isabel, miguel):
        self.stdout.write(self.style.SUCCESS('\nWallet-cases demo seeded:'))

        isabel_wallet = Wallet.objects.get(tutor=isabel)
        self.stdout.write(
            f'  {isabel.profile.fname} {isabel.profile.lname}: balance {isabel_wallet.balance} '
            f'(target {TARGET_BALANCE}) -- '
            f'{WalletTopUp.objects.filter(tutor=isabel).count()} top-ups, '
            f'{WithdrawalRequest.objects.filter(tutor=isabel).count()} withdrawals'
        )

        miguel_wallet = Wallet.objects.get(tutor=miguel)
        debt = 'DEBT BANNER shown (balance < 0)' if miguel_wallet.balance < 0 else 'no debt banner'
        cash_count = Payment.objects.filter(
            booking__tutor=miguel, method__code='CASH', payment_status='Paid',
        ).count()
        self.stdout.write(
            f'  {miguel.profile.fname} {miguel.profile.lname}: balance {miguel_wallet.balance} '
            f'-- {debt}, {cash_count} cash-paid completed sessions'
        )

        self.stdout.write('\nUndo with: python manage.py seed_wallet_cases_demo --remove')

    def _remove(self):
        removed_any = False
        for username in (ISABEL_USERNAME, MIGUEL_USERNAME, SEED_TUTEE_USERNAME):
            profile = UserProfile.objects.filter(user__username=username).first()
            if not profile:
                continue
            user = profile.user
            profile.delete()
            user.delete()
            removed_any = True

        if removed_any:
            self.stdout.write(self.style.SUCCESS(
                'Removed the wallet-cases demo tutors and seed tutee.'
            ))
        else:
            self.stdout.write('Nothing to remove -- no seeded tutors found.')
