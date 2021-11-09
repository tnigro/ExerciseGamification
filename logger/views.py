from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse

import datetime

from .models import Workout, Activity, Run, Swim, Lift, Bike, otherActivity
from .models import WorkoutForm, RunForm, SwimForm, LiftForm, BikeForm, otherActivityForm
from .models import ACTIVITIES
from goals.models import Goal
from social.models import Comment
import social.views
from planner.models import Item

# workout log form / recent workouts table
def index(request):
    # check if user is logged in
    if request.user.is_anonymous:
        return HttpResponseRedirect(reverse('home'))

    # form and workout list
    form = None
    latest_workouts = Workout.objects.filter(user=request.user).order_by('-date')[:14]

    if request.method == 'GET':
        form = WorkoutForm() # create blank (unbound) form

    elif request.method == 'POST':
        form = WorkoutForm(request.POST) # pull input values from POST request

        # validate
        if form.is_valid():
            workout = form.save(commit=False)
            workout.user = request.user;
            workout.save()
            form.save_m2m()
            return HttpResponseRedirect(reverse('logger:detail', args=(workout.id,)))

    return render(request, 'logger/index.html', {
        'user': request.user,
        'latest_workouts': latest_workouts,
        'form': form,
        'notifications': social.views.get_notification_count(request.user),
    })

# return workout instance
def detail(request, workout_id):
    # check if user is logged in
    if request.user.is_anonymous:
        return HttpResponseRedirect(reverse('home'))

    # get workout object
    workout = None
    try:
        workout = get_object_or_404(Workout, pk=workout_id, user=request.user)
    except:
        raise Http404('Selected workout log does not exist')

    # create blank forms (one for each activity type)
    forms = {} # all the forms available
    forms['run_form'] = RunForm()
    forms['swim_form'] = SwimForm()
    forms['lift_form'] = LiftForm()
    forms['bike_form'] = BikeForm()
    forms['otherActivity_form'] = otherActivityForm()

    type = None
    messages = []

    # create form with data if POST request
    if request.method == 'POST':
        type = request.POST['activity_type']
        form = None # the form to create an Activity object from
        if type == "run":
            form = RunForm(request.POST)
        elif type == "swim":
            form = SwimForm(request.POST)
        elif type == "lift":
            form = LiftForm(request.POST)
        elif type == "bike":
            form = BikeForm(request.POST)
        elif type == "otherActivity":
            form = otherActivityForm(request.POST)
        else:
            raise Http404('Invalid activity type selected')

        # validate
        if form.is_valid():
            activity = form.save(commit=False)
            activity.workout = workout
            points = activity.calculate_points()
            activity.points = points
            activity.save()
            form.save_m2m()
            messages.append('Activity logged!')

            # update goals
            goals = Goal.objects.filter(
                user=request.user,
                aType=str(type).capitalize(),
                completeBy__gte=datetime.date.today() # only get goals that haven't expired
            ).order_by('-completeBy')

            for goal in goals: # check progress of all goals
                print("goal:", goal.name)
                if goal.points > 0: # check if goal is applicable
                    if goal.points <= points: # this activity's points acheived goal
                        messages.append("Goal achieved!")
                        goal.points = 0 # goal is reached when points <= 0
                    else:
                        goal.points -= points # decreasing "points needed to acheive goal"
                    goal.save()


            # update planner Items
            items = Item.objects.filter(
                user=request.user,
                aType=str(type).capitalize()
            )
            # adds points for this log into points_earned
            for item in items:
                print("item", item.title, points)
                item.points_earned += points
                item.save()


        else:
            # set forms dictionary to fill with POST data so it doesn't dissapear to client
            forms[type+'_form'] = form

    elif request.method == 'GET':
        type = 'run' # default exercise type when page loads
    else:
        raise Http404('Invalid HTTP action for this page')

    # get all Activity objects associated with workout
    activities = []
    for a in ACTIVITIES:
        list = a.objects.filter(workout=workout)
        activities += list
    if len(activities) > 5:
        etc = len(activities) - 5
        activities = activities[:5]
        if etc > 0:
            activities += ["and %d more..." % etc]

    context = {
        'user': request.user,
        'workout': workout,
        'activities': activities, # list of previous activities
        'activity_type': type,
        'messages': messages,
        'notifications': social.views.get_notification_count(request.user),
    }
    context.update(forms) # include forms in context

    return render(request, 'logger/detail.html', context)

def delete_activity(request, type, activity_id):
    # check if user is logged in
    if request.user.is_anonymous:
        return HttpResponseRedirect(reverse('home'))

    # get activity
    if type == "run":
        type = ACTIVITIES[0]
    elif type == "swim":
        type = ACTIVITIES[1]
    elif type == "lift":
        type = ACTIVITIES[2]
    elif type == "bike":
        type = ACTIVITIES[3]
    elif type == "other":
        type = ACTIVITIES[4]
    else:
        raise Http404('Invalid activity type')

    try:
        act = get_object_or_404(type, pk=activity_id)
        workout = act.workout
    except:
        raise Http404('Activity does not exist')

    if workout.user != request.user:
        raise Http404('Activity does not exist')

    # confirm with user
    if request.method == "GET":
        return render(request, 'logger/delete_activity.html', {'activity': act})

    # delete
    elif request.method == 'POST':
        act.delete()
        return HttpResponseRedirect(reverse('logger:detail', args=(workout.id,)))

    else:
        raise Http404('Invalid HTTP action')

def delete_workout(request, workout_id):
    # check if user is logged in
    if request.user.is_anonymous:
        return HttpResponseRedirect(reverse('home'))

    try:
        workout = get_object_or_404(Workout, pk=workout_id, user=request.user)
    except:
        raise Http404('Workout log does not exist')

    if request.method == 'POST':
        # delete activities
        for act in ACTIVITIES:
            list = act.objects.filter(workout=workout)
            for a in list:
                a.delete()
        # delete comments
        comments = Comment.objects.filter(workout=workout)
        for c in comments:
            c.delete()

        workout.delete()

        return HttpResponseRedirect(reverse('logger:index'))

    elif request.method == 'GET':
        return render(request, 'logger/delete_workout.html', {'workout': workout})

    raise Http404('Invalid HTTP action')
