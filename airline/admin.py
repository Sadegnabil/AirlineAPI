from django.contrib import admin
from airline.models import *

# Register your models here.
admin.site.register(Aircraft)
admin.site.register(Airport)
admin.site.register(Flight)
admin.site.register(Booking)
admin.site.register(Passenger)
admin.site.register(PaymentProvider)
admin.site.register(Invoice)