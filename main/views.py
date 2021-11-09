from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

from logger.models import Workout
from goals.models import Goal
from social.models import Friendship
import social.views

import datetime
import json
import requests
import random

QUICKCHART_URL = 'https://quickchart.io/chart/create'
cutoff_date = datetime.date.today()-datetime.timedelta(days=80) # furthest back in history to graph
colors = [ # colors of series on progress charts - multiple colors needed if including friends
    '#5065dc',
    '#FFCC99',
    '#FF9999',
    '#99FF99',
    '#CCCCFF',
    '#66FFCC',
    '#FFCCCC',
    '#99FF66',
    '#CCCCCC',
    '#00FF99',
    '#66CCFF',
    ]

# users[0] should be primary user (request.user), other users (users[1+]) are friends
def generate_graph(users):
    # create a graph of historical progress for workouts
    graph_url = None
    datasets = {} # datapoints for each user in set
    labels = [] # graph's x-axis labels
    all_workouts = [Workout.objects.filter(
        user=user,
        date__gte=cutoff_date
    ).order_by('date') for user in users]

    if len(all_workouts[0]) == 0:
        return None

    first_date = all_workouts[0][0].date
    last_date = datetime.date.today()

    for i in range(len(all_workouts)):
        workouts = all_workouts[i]
        if len(workouts) > 1:
            point_sum = 0 # for summing point value of all workouts on specifec date

            # sum point total from before cutoff date
            old_workouts = Workout.objects.filter(
                user=users[i],
                date__lt=cutoff_date
            )
            for w in old_workouts:
                point_sum += w.get_points()

            # create graph data
            data = []
            d = first_date
            while d <= last_date: # for each day in range
                w_on_day = workouts.filter(date=d)
                if len(w_on_day) != 0:
                    for w in w_on_day:
                        point_sum += w.get_points()
                data.append(point_sum)

                # label the first of every month as well as start/end dates
                if i == 0:
                    if d.day == 1 or d == workouts[0].date or d == last_date:
                        labels.append(str(d))
                    else:
                        labels.append("")

                d += datetime.timedelta(days=1)

            datasets[users[i].username] = data

    # query quickchart API
    if len(labels) > 1:
        post = {
            'chart': {
                'type': 'line',
                'data': {
                    'labels': labels,
                    'datasets': [{
                        'label': str(key) + (' (You)' if key == users[0].username and len(users) > 1 else ''),
                        'pointStyle': 'line',
                        'data': data,
                        'fill': False,
                        'borderColor': colors[0 if key == users[0].username else (hash(key) % (len(colors)-1))+1],
                    } for key, data in datasets.items()]
                }
            }
        }
        response = requests.post(
            QUICKCHART_URL,
            json=post,
        )
        if response.status_code == 200:
            chart_response = json.loads(response.text)
            return chart_response['url'] # url of img of rendered graph

    return None


# return sum total of user's points earned
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

# compute the total points needed to reach level
def calculate_threshold(level):
    threshold = 0
    while level > 0:
        threshold += int(100 * pow(1.5, level))
        level -= 1
    return threshold

# compute level given number of points
def calculate_level(points):
    level = 0
    while points >= calculate_threshold(level):
        level += 1
    return level

# compile user stat values into dict
def calculate_user_stats(user):
    # calculate user's progress to next level
    points = get_user_points(user)
    level = calculate_level(points)

    b_thresh = calculate_threshold(level-1)
    t_thresh = calculate_threshold(level)

    progress = points - b_thresh # points earned for this level

    stats = {
        'points': points,
        'level': level,
        'progress': progress,
        'threshold': t_thresh - b_thresh,
        'percent': 100.0 * progress / (t_thresh - b_thresh), # percentage of current level
    }
    return stats

def index(request):
    template = loader.get_template('main/index.html')

    # check if user is logged in
    if not request.user.is_anonymous:
        message = None

        context = calculate_user_stats(request.user)
        context['notifications'] = social.views.get_notification_count(request.user)

        users = [request.user]

        friendships = Friendship.objects.filter(user=request.user)
        if friendships:
            users = users + [f.friend for f in friendships]

        # create a graph of historical progress for workouts (for user and for any potential friends)
        graph_url = generate_graph(users)
        context['graph_url'] = graph_url

        if graph_url != None:
            context['message'] = "Keep going!"
        else:
            context['message'] = "Get started!"

        return HttpResponse(template.render(context, request))

    # user not logged in
    else:
        return HttpResponse(template.render({}, request))

def logout(request):
    return render(request, 'main/logout.html', {
        'notifications': social.views.get_notification_count(request.user),
    })
