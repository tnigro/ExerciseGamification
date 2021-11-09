from django.contrib import admin
from .models import Workout, Run, Swim, Lift, Bike, otherActivity

admin.site.register(Workout)
admin.site.register(Run)
admin.site.register(Swim)
admin.site.register(Lift)
admin.site.register(Bike)
admin.site.register(otherActivity)
