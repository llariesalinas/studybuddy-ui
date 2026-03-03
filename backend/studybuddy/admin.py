from django.contrib import admin
from .models import PaymentMethod, TutorSubjects, UserProfile, Tutor, TutorAvailability, Booking, Payment, Rating,Subjects

admin.site.register(UserProfile)
admin.site.register(Tutor)
admin.site.register(TutorAvailability)
admin.site.register(Booking)
admin.site.register(Payment)
admin.site.register(Rating)
admin.site.register(Subjects)
admin.site.register(TutorSubjects)
admin.site.register(PaymentMethod)