from django.contrib import admin
from .models import (
    Booking,
    Course,
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
)

admin.site.register(UserProfile)
admin.site.register(Tutor)
admin.site.register(TutorAvailability)
admin.site.register(TutorAvailabilityOverride)
admin.site.register(Booking)
admin.site.register(Payment)
admin.site.register(Rating)
admin.site.register(Subjects)
admin.site.register(TutorSubjects)
admin.site.register(PaymentMethod)
admin.site.register(Preference)
admin.site.register(Strand)
admin.site.register(Course)


@admin.register(PartnerInstitution)
class PartnerInstitutionAdmin(admin.ModelAdmin):
    list_display = ('institution_name', 'school_email_domain', 'is_active', 'contact_person', 'date_added')
    list_filter = ('is_active', 'date_added')
    search_fields = ('institution_name', 'school_email_domain', 'contact_person')
