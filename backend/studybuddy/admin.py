from django.contrib import admin
<<<<<<< HEAD
from .models import PaymentMethod, TutorSubjects, UserProfile, Tutor, TutorAvailability, Booking, Payment, Rating,Subjects,Preference,Strand,Course
=======
from .models import PaymentMethod, TutorSubjects, UserProfile, Tutor, TutorAvailability, Booking, Payment, Rating,Subjects
>>>>>>> 32c6f3b (Before Merging to Another Branch)

admin.site.register(UserProfile)
admin.site.register(Tutor)
admin.site.register(TutorAvailability)
admin.site.register(Booking)
admin.site.register(Payment)
admin.site.register(Rating)
admin.site.register(Subjects)
admin.site.register(TutorSubjects)
<<<<<<< HEAD
admin.site.register(PaymentMethod)
admin.site.register(Preference)
admin.site.register(Strand)
admin.site.register(Course)
=======
admin.site.register(PaymentMethod)
>>>>>>> 32c6f3b (Before Merging to Another Branch)
