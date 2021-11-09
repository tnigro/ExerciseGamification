from django.db import models
from django import forms
from django.forms import ModelForm, TextInput, DateInput, DateTimeInput, NumberInput, Select, Textarea
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from logger.models import Workout

import re
import datetime
from datetime import date

class FriendRequest(models.Model):
    requester = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL,
        related_name="friend_requester",
    )
    receiver = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL,
        related_name="request_receiver",
    )
    date = models.DateField(blank=True, null=True, auto_now=True)

    def __str__(self):
        return "Friend request"

class Friendship(models.Model):
    user = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL,
        related_name="user",
    )
    friend = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL,
        related_name="friend",
    )
    date = models.DateField(blank=True, null=True, auto_now=True)

    def __str__(self):
        return "Friendship"

class Comment(models.Model):
    user = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL,
    )
    workout = models.ForeignKey(
        Workout,
        null=True,
        on_delete=models.SET_NULL,
    )
    timestamp = models.DateTimeField(blank=True, null=True, auto_now=True)
    comment = models.CharField(max_length=128, blank=False, null=True)

    def __str__(self):
        return "%s: %s" % (user.username, str(self.comment))

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']
        widgets = {
            'comment': Textarea(attrs={
                'class': 'form-control mb-2',
                'style': 'height: 150px;',
                'placeholder': 'Leave a public comment. Remember to be kind!',
            }),
        }

class UserSearchForm(forms.Form):
    query = forms.CharField(label="Search", max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username or name'}))
