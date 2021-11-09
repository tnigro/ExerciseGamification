from django.test import TestCase, Client
from .models import *

class UserSearchForm_Test(TestCase):
    def test_UserSearchForm_valid(self):
        form = UserSearchForm(data={
            'query': 'token token token token',
        })
        self.assertTrue(form.is_valid())

    def test_UserSearchForm_invalid_blank(self):
        form = UserSearchForm(data={
            'query': '',
        })
        self.assertFalse(form.is_valid())

    def test_UserSearchForm_invalid_query_long(self):
        form = UserSearchForm(data={
            'query': 'token token token token token token token token token token token token token token token token token token token token token token token token token token token token token',
        })
        self.assertFalse(form.is_valid())

class CommentForm_Test(TestCase):
    def test_CommentForm_valid(self):
        form = CommentForm(data={
            'comment': 'test comment',
        })
        self.assertTrue(form.is_valid())

    def test_CommentForm_invalid_blank(self):
        form = CommentForm(data={
            'comment': '',
        })
        self.assertFalse(form.is_valid())

    def test_CommentForm_invalid_long(self):
        form = CommentForm(data={
            'comment': 'Way too long Way too long Way too long Way too long Way too long Way too long Way too long Way too long Way too long Way too long Way too long Way too long Way too long Way too long Way too long Way too long Way too long Way too long',
        })
        self.assertFalse(form.is_valid())
