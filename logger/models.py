from django.db import models
from django import forms
from django.forms import ModelForm, TextInput, DateInput, NumberInput, Select, Textarea
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

import re
import math
import datetime
from datetime import date

# Django API referenced for logger/models.py
# https://docs.djangoproject.com/en/3.1/ref/models/fields/
# (MAR 2021)

# time format that inputs must follow
DATE_PATTERN = "[0-9][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9]"
TIME_PATTERN = "[0-9][0-9]:[0-9][0-9]:[0-9][0-9]"

date_pattern = re.compile(DATE_PATTERN)
time_pattern = re.compile(TIME_PATTERN)

# UNIT CONVERSION (MULTIPLY with value to convert from A_TO_B)
MI_TO_KM = 1.609344
LB_TO_KG = 0.4535924
YD_TO_M  = 0.9144

# a user's workout - can be associated with several activities (e.g. swim AND bike AND run)
class Workout(models.Model):
    name = models.CharField(max_length=25) # title user gives to this workout
    date = models.DateField(blank=False, null=True)
    description = models.CharField(max_length=128, blank=True, null=True) # brief description of workout given by user
    user = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL
    )

    def __str__(self):
        return self.name

    # get/return the total point value of activities associated with particular workout
    def get_points(workout):
        points = 0
        for act_type in ACTIVITIES:
            logs = act_type.objects.filter(workout=workout) # get all activities of certain type that correspond to workout
            for activity in logs:
                points += activity.points
        return points


# referenced https://medium.com/swlh/how-to-style-your-django-forms-7e8463aae4fa
class WorkoutForm(ModelForm):
    class Meta:
        model = Workout
        fields = ['name', 'date', 'description']
        widgets = {
            'name': TextInput(attrs={
                'class': 'form-control mb-2',
                'placeholder': 'Workout name',
                }),
            'date': DateInput(attrs={
                'class': 'form-control mb-2',
                'type': 'date',
                'max': date.today().isoformat(),
                }),
            'description': Textarea(attrs={
                'class': 'form-control mb-2',
                'style': 'height:125px;',
                'placeholder': 'A brief description of your workout (optional)',
                }),
        }

    def clean(self):
        c_data = super().clean()

        if not date_pattern.search(str(c_data.get('date'))):
            self.add_error('date', "Invalid date format. YYYY-MM-DD required.")

        elif str(c_data.get('date')) == "None" or datetime.datetime.strptime(str(c_data.get('date')), "%Y-%m-%d").date() > date.today():
            self.add_error('date', "Invalid date value. Enter a date earlier than or the same as today.")

# abstract activity model (could be a run OR swim OR bike etc.) - associated with a workout
class Activity(models.Model):
    workout = models.ForeignKey( # the workout that this activity is a part of
        Workout,
        null=True,
        on_delete=models.SET_NULL
    )
    points = models.IntegerField(blank=False, null=False, default=0)

    class Meta:
        abstract = True

# a run
class Run(Activity):
    # distance units
    KM = "km"
    MI = "mi"
    UNITS = [
        (KM, "kilometers"),
        (MI, "miles"),
    ]
    # maybe add run types here (fartlek, sprints, etc.)
    duration = models.DurationField(blank=False, null=True)
    distance = models.IntegerField(blank=False, null=False, default=0)
    elevation_gain = models.IntegerField(blank=False, null=False, default=0)
    units = models.CharField(
        max_length=2,
        choices=UNITS,
        default=1,
    )
    route = models.CharField(max_length=25, blank=True, null=True) # what running route the user followed

    def __str__(self):
        return "Ran %d %s in %s" % (self.distance, self.units, str(self.duration))

    def type(self):
        return "run"

    def calculate_points(self):
        dist = self.distance # get distance logged
        elevation = self.elevation_gain
        if self.units == "mi": # convert to metric
            dist *= MI_TO_KM
            elevation *= YD_TO_M / 3  # feet to meters

        duration = self.duration.seconds / 3600.0 # duration of activity in hours

        return int(dist * 2 + duration + elevation*0.02)

class RunForm(ModelForm):
    class Meta:
        model = Run
        fields = ['duration', 'distance', 'elevation_gain','units', 'route']
        widgets = {
            'duration': TextInput(attrs={
                'class': 'form-control mb-2',
                'pattern': TIME_PATTERN,
                'placeholder': 'Duration of your run',
                }),
            'distance': NumberInput(attrs={
                'class': 'form-control mb-2',
                'placeholder': 'Distance you ran',
                'min': '1',
                'max': '10000',
                }),
            'elevation_gain': NumberInput(attrs={
                'class': 'form-control mb-2',
                'placeholder': 'Elevation gain during your session',
                'min': '-10000',
                'max': '10000',
            }),
            'units': Select(attrs={
                'class': 'form-control mb-2',
                }),
            'route': TextInput(attrs={
                'class': 'form-control mb-2',
                'placeholder': 'Route Name (optional)',
                }),
        }
        labels = {
            'duration': 'Duration (HH:MM:SS format)',
            'units': 'Distance Units',
        }

    def clean(self):
        c_data = super().clean()

        d = c_data.get('duration')
        if not d:
            self.add_error('duration', "Invalid duration value. Make sure all values are integers.")
        else:
            d = '{:02}:{:02}:{:02}'.format(
                int(d.total_seconds() // 3600),
                int((d.total_seconds() % 3600) // 60),
                int((d.total_seconds() % 3600) % 60),
            )

            if not time_pattern.search(d):
                self.add_error('duration', "Invalid duration format. HH:MM:SS required.")

        try:
            if not c_data.get('distance'):
                raise ValueError

            load = int(c_data.get('distance'))
            if int(c_data.get('distance')) <= 0:
                self.add_error('distance', "Invalid distance value. Distance value must be positive.")
            elif int(c_data.get('distance')) > 10000:
                self.add_error('distance', "Invalid distance value. Distance value must be less than or equal to 10000.")

        except ValueError:
            self.add_error('distance', "Invalid distance value (integer value required)")

# a swim
class Swim(Activity):
    # distance units
    YD = "yd"
    M  = "m"
    UNITS = [
        (YD, "yards"),
        (M,  "meters"),
    ]
    # pool course types (long course (50 m/yd), short course (25 m/yd), open water)
    LC = "lc"
    SC = "sc"
    OW = "ow"
    COURSES = [
        (LC, "Long Course"),
        (SC, "Short Course"),
        (OW, "Open Water"),
    ]
    duration = models.DurationField(blank=False, null=True)
    distance = models.IntegerField(blank=False, null=False, default=0)
    units = models.CharField(
        max_length=2,
        choices=UNITS,
        default=0,
    )
    course = models.CharField(
        max_length=2,
        choices=COURSES,
        default=0,
    )

    def __str__(self):
        course_name = None
        for tuple in self.COURSES:
            if tuple[0] == self.course:
                course_name = tuple[1]
                break
        return "Swam %d %s (%s) in %s" % (self.distance, self.units, course_name, str(self.duration))

    def type(self):
        return "swim"

    def calculate_points(self):
        dist = self.distance # get distance logged
        if self.units == "yd": # convert to metric
            dist *= YD_TO_M

        duration = self.duration.seconds / 3600.0 # duration of activity in hours
        course_mult = 1.1 if self.course == "lc" or self.course == "ow" else 1 # give bonus points for swimming in a longer pool

        return int((dist / 1000.0) * course_mult * 2.5 + duration)

class SwimForm(ModelForm):
    class Meta:
        model = Swim
        fields = ['duration', 'distance', 'units', 'course']
        widgets = {
            'duration': TextInput(attrs={
                'class': 'form-control mb-2',
                'pattern': TIME_PATTERN,
                'placeholder': 'Duration of your swim',
                }),
            'distance': NumberInput(attrs={
                'class': 'form-control mb-2',
                'placeholder': 'Distance you swam',
                'min': '1',
                'max': '10000',
                }),
            'units': Select(attrs={
                'class': 'form-control mb-2',
                }),
            'course': Select(attrs={
                'class': 'form-control mb-2',
                }),
        }
        labels = {
            'duration': 'Duration (HH:MM:SS format)',
            'units': 'Distance Units',
        }

    def clean(self):
        c_data = super().clean()

        d = c_data.get('duration')
        if not d:
            self.add_error('duration', "Invalid duration value. Make sure all values are integers.")
        else:
            d = '{:02}:{:02}:{:02}'.format(
                int(d.total_seconds() // 3600),
                int((d.total_seconds() % 3600) // 60),
                int((d.total_seconds() % 3600) % 60),
            )

            if not time_pattern.search(d):
                self.add_error('duration', "Invalid duration format. HH:MM:SS required.")

        try:
            if not c_data.get('distance'):
                raise ValueError

            load = int(c_data.get('distance'))
            if int(c_data.get('distance')) <= 0:
                self.add_error('distance', "Invalid distance value. Distance value must be positive.")
            elif int(c_data.get('distance')) > 10000:
                self.add_error('distance', "Invalid distance value. Distance value must be less than or equal to 10000.")

        except ValueError:
            self.add_error('distance', "Invalid distance value (integer value required)")

# a weight trainings
class Lift(Activity):
    # weight/mass units
    LB = "lb"
    KG = "kg"
    UNITS = [
        (LB, "pounds"),
        (KG, "kilograms"),
    ]
    # lift modalities
    BACK_SQT = "BS"
    BENCH_PS = "BN"
    DEADLIFT = "DL"
    FRNT_SQT = "FS"
    OHP      = "OH"
    SNATCH   = "SN"
    CN_N_JRK = "CJ"
    PULLUP   = "PU"
    LIFTS = [
        (BACK_SQT, 'Back Squat'),
        (BENCH_PS, 'Bench Press'),
        (DEADLIFT, 'Deadlift'),
        (FRNT_SQT, 'Front Squat'),
        (OHP,      'Overhead Press'),
        (SNATCH,   'Snatch'),
        (CN_N_JRK, 'Clean and Jerk'),
        (PULLUP,   'Pullup'),
    ]

    movement = models.CharField(
        max_length=2,
        choices=LIFTS,
        default=0,
    )
    sets = models.IntegerField(blank=False, null=False, default=0)
    reps = models.IntegerField(blank=False, null=False, default=0)
    load = models.IntegerField(blank=False, null=False, default=0)
    units = models.CharField(
        max_length=2,
        choices=UNITS,
        default=0,
    )

    def __str__(self):
        lift_name = None
        for tuple in self.LIFTS:
            if tuple[0] == self.movement:
                lift_name = tuple[1]
                break
        if lift_name == "Pullup":
            past_tense = lift_name
        elif lift_name.endswith("uat"): # squat -> squatted
            past_tense = lift_name + "ted"
        else:
            past_tense = lift_name + "ed"

        return "Lift: %s %d %s for %dx%d" % (past_tense, self.load, self.units, self.sets, self.reps)

    def type(self):
        return "lift"

    def calculate_points(self):
        load = self.load
        if self.units == "lb":
            load *= LB_TO_KG

        m = self.movement
        mov_mult = 1 # movement multiplier (to adjust for relative difficulty of lifts)

        if m == "BS":
            mov_mult = 1
        elif m == "BN":
            mov_mult = 0.9
        elif m == "DL":
            mov_mult = 0.8
        elif m == "FS":
            mov_mult = 1.2
        elif m == "OH":
            mov_mult = 1.3
        elif m == "SN":
            mov_mult = 1.6
        elif m == "CJ":
            mov_mult = 1.7
        elif m == "PU":
            mov_mult = 10
            load += 50

        return int(load * math.sqrt(self.sets * self.reps) * mov_mult / 10.0)

class LiftForm(ModelForm):
    class Meta:
        model = Lift
        fields = ['movement', 'sets', 'reps', 'load', 'units']
        widgets = {
            'movement': Select(attrs={
                'class': 'form-control mb-2',
                }),
            'sets': NumberInput(attrs={
                'class': 'form-control mb-2',
                'min': '1',
                'max': '10000',
                }),
            'reps': NumberInput(attrs={
                'class': 'form-control mb-2',
                'min': '1',
                'max': '10000',
                }),
            'load': NumberInput(attrs={
                'class': 'form-control mb-2',
                'min': '0',
                'max': '10000',
                }),
            'units': Select(attrs={
                'class': 'form-control mb-2',
                }),
        }
        labels = {
            'units': 'Weight/Mass Units'
        }

    def clean(self):
        c_data = super().clean()

        if int(c_data.get('sets')) <= 0 or int(c_data.get('sets')) > 10000:
            self.add_error('sets', "Invalid number of sets")

        if int(c_data.get('reps')) <= 0 or int(c_data.get('reps')) > 10000:
            self.add_error('reps', "Invalid number of reps")

        try:
            if not c_data.get('load'):
                raise ValueError

            load = int(c_data.get('load'))
            if load < 0:
                self.add_error('load', "Invalid load value. Load value must be at least 0.")
            elif load > 10000:
                self.add_error('load', "Invalid load value. Load value must be less than 10000.")

        except ValueError:
            self.add_error('load', "Invalid load value (integer value required)")

class Bike(Activity):
    # distance units
    KM = "km"
    MI = "mi"
    UNITS = [
        (KM, "kilometers/meters"),
        (MI, "miles/feet"),
    ]
    duration = models.DurationField(blank=False, null=True)
    elevation_gain = models.IntegerField(blank=False, null=False, default=0)
    distance = models.IntegerField(blank=False, null=False, default=0)
    units = models.CharField(
        max_length=2,
        choices=UNITS,
        default=1,
    )
    route = models.CharField(max_length=25, blank=True, null=True) # what bike route the user followed

    def __str__(self):
        return "Biked %d %s in %s" % (self.distance, self.units, str(self.duration))

    def type(self):
        return "bike"

    def calculate_points(self):
        dist = self.distance # get distance logged
        elevation_gain = self.elevation_gain

        if self.units == "mi": # convert to metric
            dist *= MI_TO_KM
            elevation_gain *= YD_TO_M / 3 # feet to meters

        duration = self.duration.seconds / 3600.0

        return int(dist / 2.0 + duration + elevation_gain * 0.015)

class BikeForm(ModelForm):
    class Meta:
        model = Bike
        fields = ['duration', 'distance', 'elevation_gain', 'units', 'route']
        widgets = {
            'duration': TextInput(attrs={
                'class': 'form-control mb-2',
                'pattern': TIME_PATTERN,
                'placeholder': 'Duration you biked',
                }),
            'distance': NumberInput(attrs={
                'class': 'form-control mb-2',
                'placeholder': 'Distance you biked',
                'min': '1',
                'max': '10000',
                }),
            'units': Select(attrs={
                'class': 'form-control mb-2',
                }),
            'elevation_gain': NumberInput(attrs={
                'class': 'form-control mb-2',
                'placeholder': 'Elevation gain during your session',
                'min': '-10000',
                'max': '10000',
                }),
            'route': TextInput(attrs={
                'class': 'form-control mb-2',
                'placeholder': 'Route Name (optional)',
                }),
        }
        labels = {
            'duration': 'Duration (HH:MM:SS format)',
            'units': 'Distance Units',
        }

    def clean(self):
        c_data = super().clean()

        d = c_data.get('duration')
        if not d:
            self.add_error('duration', "Invalid duration value. Make sure all values are integers.")
        else:
            d = '{:02}:{:02}:{:02}'.format(
                int(d.total_seconds() // 3600),
                int((d.total_seconds() % 3600) // 60),
                int((d.total_seconds() % 3600) % 60),
            )

            if not time_pattern.search(d):
                self.add_error('duration', "Invalid duration format. HH:MM:SS required.")

        try:
            if not c_data.get('distance'):
                raise ValueError

            load = int(c_data.get('distance'))
            if int(c_data.get('distance')) <= 0:
                self.add_error('distance', "Invalid distance value. Distance value must be positive.")
            elif int(c_data.get('distance')) > 10000:
                self.add_error('distance', "Invalid distance value. Distance value must be less than or equal to 10000.")

        except ValueError:
            self.add_error('distance', "Invalid distance value (integer value required)")

class otherActivity(Activity):
    duration = models.DurationField(blank=False, null=True)
    description = models.CharField(max_length=200)

    def __str__(self):
        return "Other activity (%s)" % str(self.duration)

    def type(self):
        return "other"

    def calculate_points(self):
        duration = self.duration.seconds / 3600.0
        return int(duration * 1.005)

class otherActivityForm(ModelForm):
    class Meta:
        model = otherActivity
        fields = ['duration', 'description']
        widgets = {
            'duration': TextInput(attrs={
                'class': 'form-control mb-2',
                'pattern': TIME_PATTERN,
                'placeholder': 'Duration of activity',
            }),
            'description': TextInput(attrs={
                'class': 'form-control mb-2',
                'placeholder': 'A short description of your activity',
            }),
        }
        labels = {
            'duration': 'Duration (HH:MM:SS format)',
        }


    def clean(self):
        c_data = super().clean()

        d = c_data.get('duration')
        if not d:
            self.add_error('duration', "Invalid duration value. Make sure all values are integers.")
        else:
            d = '{:02}:{:02}:{:02}'.format(
                int(d.total_seconds() // 3600),
                int((d.total_seconds() % 3600) // 60),
                int((d.total_seconds() % 3600) % 60),
            )

            if not time_pattern.search(d):
                self.add_error('duration', "Invalid duration format. HH:MM:SS required.")


# all activity types
ACTIVITIES = (Run, Swim, Lift, Bike, otherActivity)

