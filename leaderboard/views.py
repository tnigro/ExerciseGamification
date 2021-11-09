from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse

import datetime
import operator

from django.contrib.auth.models import User
import logger.models
from social.models import Friendship

import main.views
import social.views

# Create your views here.
def index(request):
    # check if user is logged in
    if request.user.is_anonymous:
        return HttpResponseRedirect(reverse('home'))

    # get set of user's friends + request.user
    fships = Friendship.objects.filter(user=request.user)
    users = [request.user] + [f.friend for f in fships]

    # get user details
    arr = []
    for user in users:
        my_dict = {}
        my_dict['first_name'] = user.first_name
        my_dict['last_name'] = user.last_name
        my_dict['username'] = user.username
        my_dict['email'] = user.email

        points = main.views.get_user_points(user)
        my_dict['points'] = points
        my_dict['level'] = main.views.calculate_level(points)

        arr.append(my_dict)

    # sort for table display
    arr.sort(key=operator.itemgetter('points'),reverse=True)

    context = {
        'user': request.user,
        'users': arr,
        'notifications': social.views.get_notification_count(request.user),
    }
    return render(request, 'leaderboard/index.html', context)
