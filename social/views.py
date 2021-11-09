from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse

import datetime

from django.db.models import Q
from django.contrib.auth.models import User
from .models import FriendRequest, Friendship, Comment, CommentForm, UserSearchForm
import logger.models

#from main.views import generate_graph, get_user_points, calculate_threshold, calculate_level
import main.views

# return queryset of a list of users' workouts
def get_feed(users):
    ret = None
    for user in users:
        workouts = logger.models.Workout.objects.filter(
            user=user,
            date__gte=datetime.date.today() - datetime.timedelta(days=7), # filter workouts from past few days
        )
        ret = ret | workouts if ret != None else workouts
    if ret != None:
        ret = ret.order_by('-date')
    return ret

# return number of social notifications for user
def get_notification_count(user):
    notifs = len(FriendRequest.objects.filter(receiver=user))
    if notifs == 0:
        return None
    elif notifs < 10:
        return notifs
    else:
        return "9+"

# pre: "user" and "friend" are valid user objects
# res: create a two-way Friendship relationship (two Frienship objects)
def create_friendship(user, f):
    # check that user is not friends with themselves
    if user.id == f.id:
        return

    if not Friendship.objects.filter(user=user,friend=f)[:1]: # check that friendship does not already exist
        # user considers f a friend
        fship1 = Friendship()
        fship1.user = user
        fship1.friend = f
        fship1.save()

    if not Friendship.objects.filter(user=f,friend=user)[:1]: # check that friendship does not already exist
        # f considers user a friend
        fship2 = Friendship()
        fship2.user = f
        fship2.friend = user
        fship2.save()

# main "friends" page: user search, friend request listing, etc.
def index(request):
    # check if user is logged in
    if request.user.is_anonymous:
        return HttpResponseRedirect(reverse('home'))

    # get friend requests sent to user
    reqs = FriendRequest.objects.filter(receiver=request.user).order_by('-date')

    # process friend request approvals/rejections
    if request.method == "POST":
        for r in reqs:
            group = "group_%d" % r.id
            if group in request.POST:
                if request.POST[group] == "accept":
                    # create friendship
                    create_friendship(r.requester, r.receiver)

                reqs = reqs.exclude(id=r.id)
                r.delete()

    # get list of friendships
    friendships = Friendship.objects.filter(user=request.user).order_by('-date')

    context = {
        'requests': reqs,
        'friendships': friendships,
        'feed': get_feed([f.friend for f in friendships]) # friends activity feed
    }
    return render(request, 'social/index.html', context)

# search function for finding users
def search(request):
    # check if user is logged in
    if request.user.is_anonymous:
        return HttpResponseRedirect(reverse("provider_login_url 'google'"))

    context = {}

    if request.method == "POST":
        form = UserSearchForm(request.POST)

        if form.is_valid():
            # get list of users
            tokens = str(form.cleaned_data['query']).lower().split(" ") # could be first OR last name OR username OR email
            users = None
            for t in tokens:
                if users == None:
                    users = User.objects.filter(Q(username=t) | Q(first_name=t.capitalize()) | Q(last_name=t.capitalize()) | Q(email=t))
                else:
                    users = users | User.objects.filter(Q(username=t) | Q(first_name=t.capitalize()) | Q(last_name=t.capitalize()) | Q(email=t))

            if users:
                context['users'] = users
            else:
                context['message'] = "No users matching your search found."

    else:
        form = UserSearchForm()

    context['form'] = form
    context['notifications'] = get_notification_count(request.user)

    return render(request, 'social/search.html', context)

# some user's public profile
def detail(request, username):
    # check if user is logged in
    if request.user.is_anonymous:
        return HttpResponseRedirect(reverse('home'))

    context = {}

    # get user
    user = None
    try:
        user = get_object_or_404(User, username=username)
        if request.user.id == user.id: # user looking at their own page
            context['self'] = True
    except:
        raise Http404('User does not exist')

    context['user'] = user

    # check if a friend request from request.user to user pending
    friend_request = FriendRequest.objects.filter(requester=request.user, receiver=user)[:1]

    # process friend request generation
    if request.method == "POST":
        if len(friend_request) == 0 and not 'self' in context:
            req = FriendRequest()
            req.requester = request.user
            req.receiver = user
            req.save() # save model

            friend_request = [req] # track that request has been created

    # calculate user's stats
    context.update(main.views.calculate_user_stats(user))

    # get recent activity
    context['feed'] = get_feed([user])

    # get notification badge
    context['notifications'] = get_notification_count(request.user)

    # friendship model(s)
    friendship = Friendship.objects.filter(user=request.user,friend=user)[:1]

    if len(friendship) > 0:
        context['friendship'] = friendship[0]
    if len(friend_request) > 0:
        context['friend_request'] = friend_request[0]

    if len(friendship) > 0 or request.user.username == username:
        context['graph_url'] = main.views.generate_graph([user])

    return render(request, 'social/detail.html', context)

# confirm/execute unfriend request
# username of user to unfriend
def unfriend(request, username):
    # check if user is logged in
    if request.user.is_anonymous:
        return HttpResponseRedirect(reverse('home'))

    try:
        toUnfriend = get_object_or_404(User, username=username)
    except:
        raise Http404('User does not exist')

#    if toUnfriend.username == request.user.username:
#        raise Http404('Invalid user to unfriend')

    # confirmed
    if request.method == "POST":
        friendship = Friendship.objects.filter(Q(user=request.user, friend=toUnfriend) | Q(user=toUnfriend, friend=request.user))
        for f in friendship:
            f.delete()
        return HttpResponseRedirect(reverse("social:index"))

    else:
        return render(request, 'social/unfriend.html', {
            'user': toUnfriend,
            'notifications': get_notification_count(request.user),
        })

# show a friend's workout post
def post_detail(request, workout_id):
    # check if user is logged in
    if request.user.is_anonymous:
        return HttpResponseRedirect(reverse('home'))

    # get workout object
    try:
        workout = get_object_or_404(logger.models.Workout, pk=workout_id)
    except:
        raise Http404('Post does not exist')

    # check if friends
    if workout.user != request.user and len(Friendship.objects.filter(user=request.user, friend=workout.user)) == 0:
        raise Http404('Post does not exist')

    # retrieve activities info
    activities = []
    for a in logger.models.ACTIVITIES:
        list = a.objects.filter(workout=workout)
        activities += list

    # handle comment form
    if request.method == "POST":
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.workout = workout
            comment.save()
            form.save_m2m()

            form = CommentForm()

    else:
        form = CommentForm()

    context = {
        'user': request.user,
        'workout': workout,
        'activities': activities,
        'form': form,
        'comments': Comment.objects.filter(workout=workout).order_by('-timestamp'),
        'notifications': get_notification_count(request.user),
    }

    return render(request, 'social/post.html', context)

# confirm/execute comment deletion
def delete_comment(request, comment_id):
    # check if user is logged in
    if request.user.is_anonymous:
        return HttpResponseRedirect(reverse('home'))

    try:
        comment = get_object_or_404(Comment, user=request.user, pk=comment_id)
    except:
        raise Http404('Comment does not exist')

    # confirmed
    if request.method == "POST":
        workout = comment.workout
        comment.delete()
        return HttpResponseRedirect(reverse("social:post", args=[workout.id]))

    else:
        return render(request, 'social/delete_comment.html', {
            'comment': comment,
            'notifications': get_notification_count(request.user),
        })

