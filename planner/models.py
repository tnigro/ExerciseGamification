from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User


class Item(models.Model):
    # Each Item on the planner represents a goal. Whenever a goal is created, so too is an Item
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

    title = models.CharField(max_length=200)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField() # this is date it appears on planner
    points = models.IntegerField(blank=False, null=False, default=0) # points to earn
    points_earned = models.IntegerField(blank=False, null=False, default=0) # progress
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

    #link to goals if clicked, kinda useless but hey
    @property
    def get_html_url(self):
        url = reverse('goals:index')
        return f'<a href="{url}"> {self.title} </a>'

    def __str__(self):
        return self.title