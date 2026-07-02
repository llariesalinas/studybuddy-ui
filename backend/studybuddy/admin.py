from django.contrib import admin
from .models import (
    Booking,
    Course,
    AdminAccountRequest,
    InstitutionRequest,
    Notification,
    PartnerInstitution,
    Payment,
    PaymentMethod,
    Preference,
    Rating,
    Strand,
    Subjects,
    Tutor,
    TutorAvailability,
    TutorAvailabilityOverride,
    TutorSubjects,
    UserProfile,
    Wallet,
    Transaction,
    WithdrawalRequest,
)

admin.site.register(UserProfile)
admin.site.register(Tutor)
admin.site.register(TutorAvailability)
admin.site.register(TutorAvailabilityOverride)
admin.site.register(Booking)
admin.site.register(Notification)
admin.site.register(Payment)
admin.site.register(Rating)
admin.site.register(Subjects)
admin.site.register(TutorSubjects)
admin.site.register(PaymentMethod)
admin.site.register(Preference)
admin.site.register(Strand)
admin.site.register(Course)
admin.site.register(InstitutionRequest)
admin.site.register(AdminAccountRequest)


admin.site.register(Wallet)
admin.site.register(Transaction)


@admin.register(WithdrawalRequest)
class WithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = (
        'tutor',
        'amount',
        'provider_fee',
        'method',
        'provider_status',
        'provider_reference_number',
        'status',
        'requested_at',
        'processed_at'
    )
    list_filter = ('status', 'method', 'provider_status')
    search_fields = (
        'tutor__profile__fname',
        'tutor__profile__lname',
        'account_number',
        'account_name',
        'provider_reference_number',
        'provider_wallet_transaction_id'
    )
    readonly_fields = ('tutor', 'amount', 'method', 'account_number', 'account_name', 'bank_name', 'requested_at')
    actions = ['mark_processed', 'mark_rejected']

    def mark_processed(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='processed', processed_at=timezone.now())
    mark_processed.short_description = 'Mark selected withdrawals as Processed'

    def mark_rejected(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='rejected', processed_at=timezone.now())
    mark_rejected.short_description = 'Mark selected withdrawals as Rejected'


@admin.register(PartnerInstitution)
class PartnerInstitutionAdmin(admin.ModelAdmin):
    list_display = ('institution_name', 'school_email_domain', 'is_active', 'contact_person', 'date_added')
    list_filter = ('is_active', 'date_added')
    search_fields = ('institution_name', 'school_email_domain', 'contact_person')
