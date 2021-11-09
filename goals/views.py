from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse

import datetime

from .models import Goal, GoalForm
from planner.models import Item

import social.views

# goals log form / current goals
def index(request):
    # check if user is logged in
    if request.user.is_anonymous:
        return HttpResponseRedirect(reverse('home'))

    # form and workout list
    form = None
    latest_goals = Goal.objects.filter(
        user=request.user,
        completeBy__gte=datetime.date.today() - datetime.timedelta(days=1) # get future or recently expired goals
    ).order_by('completeBy')


    if request.method == 'GET':
        form = GoalForm() # create blank (unbound) form

    elif request.method == 'POST':
        form = GoalForm(request.POST) # pull input values from POST request

        # validate
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user;
            goal.reward = goal.calculate_reward()
            goal.save()
            form.save_m2m()
            # FOR PLANNER, adds item
            # MUST add title, start_date (today), end_date (when the goal date is), points (to earn, not reward) user.
            title = goal.name
            start = datetime.date.today()
            end = goal.completeBy
            points = goal.points
            type = goal.aType
            newItem = Item(title=title, start_time=start, end_time=end, points=points, user=request.user, aType=type)
            newItem.save()

            return HttpResponseRedirect(reverse('goals:index'))


    return render(request, 'goals/index.html', {
        'user': request.user,
        'latest_goals': latest_goals,
        'form': form,
        'notifications': social.views.get_notification_count(request.user),
    })
