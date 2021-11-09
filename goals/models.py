from django.db import models
from django import forms
from django.forms import ModelForm, TextInput, DateInput, NumberInput, Select
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

import re
import datetime
from datetime import date

DATE_PATTERN = "[0-9][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9]"
TIME_PATTERN = "[0-2][0-9]:[0-5][0-9]:[0-5][0-9]"

date_pattern = re.compile(DATE_PATTERN)
time_pattern = re.compile(TIME_PATTERN)

# a goal for the user, which we will award points by
class Goal(models.Model):
    RUN = "Run"
    SWIM = "Swim"
    BIKE = "Bike"
    LIFT = "Lift"
    CHOICES = [
        (RUN, "Run"),
        (SWIM, "Swim"),
        (BIKE, "Bike"),
        (LIFT, "Lift"),
    ]

    name = models.CharField(max_length=25) # title user gives to this goal
    completeBy = models.DateField(blank=False, null=True)
    points = models.IntegerField(blank=False, null=False, default=0) # target points to earn
    reward = models.IntegerField(blank=True, null=False, default=0) # reward for meeting goal
    aType = models.CharField(
        max_length=4,
        choices=CHOICES,
        default=1,
    )
    user = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL
    )

    def __str__(self):
        return self.name

    def calculate_reward(self):
        now = date.today()
        delta = max((self.completeBy - now).days, 0) + 1
        return int(self.points * 1.5 / delta)

    def get_points(self):
        if self.points <= 0:
            return "Achieved!"
        else:
            return self.points

#form to create a new goal
class GoalForm(ModelForm):
    class Meta:
        model = Goal
        fields = ['name', 'points', 'aType', 'completeBy']
        widgets = {
            'name': TextInput(attrs={
                'class': 'form-control mb-2',
                'placeholder': 'Goal title',
                }),
            'points': NumberInput(attrs={
                'class': 'form-control mb-2',
                'min': '0',
                'max': '1000000',
                }),
            'aType': Select(attrs={
                'class': 'form-control mb-2',
                }),
            'completeBy': DateInput(attrs={
                'class': 'form-control mb-2',
                'type': 'date',
                'min': date.today().isoformat(),
                }),
        }
        labels = {
            'points' : 'Points to earn',
            'completeBy': 'Goal completion date',
            'aType' : 'Activity progress to track',
        }

    def clean(self):
        c_data = super().clean()

        aType = c_data.get('aType')
        if not (aType == "Run" or aType == "Swim" or aType == "Lift" or aType == "Bike"):
            self.add_error('aType', "Invalid activity type")

        if not date_pattern.search(str(c_data.get('completeBy'))):
            self.add_error('completeBy', "Invalid date format")

        if str(c_data.get('completeBy')) == "None" or datetime.datetime.strptime(str(c_data.get('completeBy')), "%Y-%m-%d").date() < date.today():
            self.add_error('completeBy', "Invalid completion date")

        if int(c_data.get('points')) <= 0 or int(c_data.get('points')) > 1000000:
            self.add_error('points', "Invalid point value")

