from django.test import TestCase
from .models import *


class Planner_Test(TestCase):
    def setUpRunItem(cls):
            # Set up non-modified objects used by all test methods
            Item.create(title = 'workout', start_time = '2021-02-01', end_time = '2021-03-03',
                                points = '10', points_earned = '10', aType = 'Run')

    def test_title_representation(self):
        entry = Item(title="My entry title")
        self.assertEqual(str(entry), entry.title)

    def test_start_time_representation(self):
        entry = Item(start_time="2021-02-01")
        self.assertNotEqual(str(entry), entry.start_time)

    def test_end_time_representation(self):
        entry = Item(end_time="2021-02-01")
        self.assertNotEqual(str(entry), entry.end_time)

    def test_points_representation(self):
        entry = Item(points="10")
        self.assertNotEqual(str(entry), entry.points)

    def test_points_earned_representation(self):
        entry = Item(points_earned="10")
        self.assertNotEqual(str(entry), entry.points_earned)

    def test_Run_representation(self):
        entry = Item(aType="Run")
        self.assertNotEqual(str(entry), entry.aType)

    def test_Swim_representation(self):
        entry = Item(aType="Swim")
        self.assertNotEqual(str(entry), entry.aType)

    def test_Bike_representation(self):
        entry = Item(aType="Bike")
        self.assertNotEqual(str(entry), entry.aType)

    def test_Lift_representation(self):
        entry = Item(aType="Lift")
        self.assertNotEqual(str(entry), entry.aType)

    def test_verbose_name_plural(self):
        self.assertEqual(str(Item._meta.verbose_name_plural), "items")