from datetime import datetime, timedelta, date
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.urls import reverse
from django.utils.safestring import mark_safe
from logger.models import Workout, ACTIVITIES
from goals.models import Goal
import calendar
from .models import *
from .utils import Calendar
import social.views

def index(request):
    return HttpResponse("hey")

# This code (next_month, prev_month, get_date, and get_context methods) was
# largely based off the following tutorial. It's all modified to fit Gamercise,
# but this file along with utils.py and base.html used code from the tutorial
# as a base.

#######################################################################
# REFERENCE:
# Title: "How to Create a Calendar Using Django"
# Author: Hui Wen
# Date: 24 July 2018
# URL: https://www.huiwenteo.com/normal/2018/07/24/django-calendar.html
# License: 3-Clause BSD
########################################################################

class CalendarView(generic.ListView):
    model = Item
    template_name = 'planner/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # use today's date for the calendar
        d = get_date(self.request.GET.get('month', None))

        # Instantiate our calendar class with today's year and date
        cal = Calendar(d.year, d.month)

        # Call the formatmonth method, which returns our calendar as a table
        html_cal = cal.formatmonth(self.request.user, get_user_points(self.request.user), withyear=True) #added self.request.user to pass user argument in
        context['calendar'] = mark_safe(html_cal)
        context['prev_month'] = prev_month(d)
        context['next_month'] = next_month(d)
        context['notifications'] = social.views.get_notification_count(self.request.user)
        return context

def get_date(req_day):
    if req_day:
        year, month = (int(x) for x in req_day.split('-'))
        return date(year, month, day=1)
    return datetime.today()


def prev_month(d):
    first = d.replace(day=1)
    prev_month = first - timedelta(days=1)
    month = 'month=' + str(prev_month.year) + '-' + str(prev_month.month)
    return month

def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    month = 'month=' + str(next_month.year) + '-' + str(next_month.month)
    return month



# Same method as in main/views.py
#TODO: only access points from desired activity type
def get_user_points(user):
    points = 0

    workouts = Workout.objects.filter(user=user)
    for w in workouts:
        points += w.get_points()

    goals = Goal.objects.filter(user=user)
    for g in goals:
        if g.points <= 0:
            points += g.reward

    return points
