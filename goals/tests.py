from django.test import TestCase, Client
from .models import *

class GoalForm_Test(TestCase):
    def test_GoalForm_valid(self):
        form = GoalForm(data={
            'name': 'Test Goal',
            'points': '100',
            'completeBy': '2099-01-01',
            'aType' : 'Bike'
        })
        self.assertTrue(form.is_valid())

    def test_GoalForm_invalid_blank_name(self):
        form = GoalForm(data={
            'name': '',
            'points': '100',
            'completeBy': '2099-01-01',
        })
        self.assertFalse(form.is_valid())


    def test_GoalForm_invalid_zero_points(self):
        form = GoalForm(data={
            'name': 'Test Goal',
            'points': '0',
            'completeBy': '2099-01-01',
        })
        self.assertFalse(form.is_valid())

    def test_GoalForm_invalid_negative_points(self):
        form = GoalForm(data={
            'name': 'Test Goal',
            'points': '-1',
            'completeBy': '2099-01-01',
        })
        self.assertFalse(form.is_valid())

    def test_GoalForm_invalid_date(self):
        form = GoalForm(data={
            'name': 'Test Goal',
            'points': '100',
            'completeBy': '2021-01-01',
        })
        self.assertFalse(form.is_valid())

    def test_GoalForm_blank_date(self):
        form = GoalForm(data={
            'name': 'Test Goal',
            'points': '100',
            'completeBy': '',
        })
        self.assertFalse(form.is_valid())