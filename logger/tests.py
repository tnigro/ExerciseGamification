from django.test import TestCase, Client
from .models import *

#class Setup_Class(TestCase):
#    def setUp(self):
#        self.user = User.objects.create(email="user@virginia.edu", password="pass", first_name="tester")

class WorkoutForm_Test(TestCase):
    def test_WorkoutForm_valid(self):
        form = WorkoutForm(data={
            'name': 'Test Workout',
            'date': '2021-01-01',
        })
        self.assertTrue(form.is_valid())

    def test_WorkoutForm_invalid_blank_name(self):
        form = WorkoutForm(data={
            'name': '',
            'date': '2021-01-01',
        })
        self.assertFalse(form.is_valid())

    def test_WorkoutForm_invalid_long_name(self):
        form = WorkoutForm(data={
            'name': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ12345',
            'date': '2021-01-01',
        })
        self.assertFalse(form.is_valid())

    def test_WorkoutForm_invalid_date_1(self):
        form = WorkoutForm(data={
            'name': 'Test Workout',
            'date': '202-01-01',
        })
        self.assertFalse(form.is_valid())

    def test_WorkoutForm_invalid_date_2(self):
        form = WorkoutForm(data={
            'name': 'Test Workout',
            'date': '2020-01-35',
        })
        self.assertFalse(form.is_valid())

class RunForm_Test(TestCase):
    def test_RunForm_valid(self):
        form = RunForm(data={
            'duration': '00:26:30',
            'distance': '16',
            'elevation_gain': '0',
            'units': 'mi',
            'route': '',
        })
        self.assertTrue(form.is_valid())

    def test_RunForm_invalid_neg_distance(self):
        form = RunForm(data={
            'duration': '00:20:00',
            'distance': '-16',
            'elevation_gain': '-14',
            'units': 'mi',
            'route': 'test',
        })
        self.assertFalse(form.is_valid())

    def test_RunForm_invalid_float_distance(self):
        form = RunForm(data={
            'duration': '00:20:00',
            'distance': '26.2',
            'elevation_gain': '14',
            'units': 'mi',
            'route': 'test',
        })
        self.assertFalse(form.is_valid())

    def test_RunForm_invalid_distance(self):
        form = RunForm(data={
            'duration': '00:20:00',
            'distance': 'FAR',
            'elevation_gain': '15',
            'units': 'mi',
            'route': 'test',
        })
        self.assertFalse(form.is_valid())

    def test_RunForm_invalid_units(self):
        form = RunForm(data={
            'duration': '00:20:00',
            'distance': '16',
            'elevation_gain': '14',
            'units': 'yards',
            'route': 'test',
        })
        self.assertFalse(form.is_valid())

    def test_RunForm_invalid_neg_duration(self):
        form = RunForm(data={
            'duration': '-00:20:00',
            'distance': '16',
            'elevation_gain': '0',
            'units': 'mi',
            'route': 'test',
        })
        self.assertFalse(form.is_valid())

    def test_RunForm_invalid_duration(self):
        form = RunForm(data={
            'duration': '00:y0:00',
            'distance': '16',
            'elevation_gain': '100',
            'units': 'mi',
            'route': 'test',
        })
        self.assertFalse(form.is_valid())

    def test_RunForm_invalid_distance(self):
        form = RunForm(data={
            'duration': '00:20:00',
            'distance': '2147483647',
            'elevation_gain': '100',
            'units': 'mi',
            'route': 'test',
        })
        self.assertFalse(form.is_valid())

    def test_RunForm_invalid_route(self):
        form = RunForm(data={
            'duration': '00:20:00',
            'distance': '16',
            'elevation_gain': '25',
            'units': 'mi',
            'route': 'testtesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttest',
        })
        self.assertFalse(form.is_valid())

class SwimForm_Test(TestCase):
    def test_SwimForm_valid(self):
        form = SwimForm(data={
            'duration': '00:26:30',
            'distance': '1600',
            'units': 'm',
            'course': 'sc',
        })
        self.assertTrue(form.is_valid())

    def test_SwimForm_invalid_neg_distance(self):
        form = SwimForm(data={
            'duration': '00:26:30',
            'distance': '-16',
            'units': 'm',
            'course': 'sc',
        })
        self.assertFalse(form.is_valid())

    def test_SwimForm_invalid_duration(self):
        form = SwimForm(data={
            'duration': '00:y0:00',
            'distance': '1600',
            'units': 'm',
            'course': 'sc',
        })
        self.assertFalse(form.is_valid())

    def test_SwimForm_invalid_distance(self):
        form = SwimForm(data={
            'duration': '00:26:30',
            'distance': '2147483647',
            'units': 'm',
            'course': 'sc',
        })
        self.assertFalse(form.is_valid())

    def test_SwimForm_invalid_units(self):
        form = SwimForm(data={
            'duration': '00:26:30',
            'distance': '16',
            'units': 'm ',
            'course': 'sc',
        })
        self.assertFalse(form.is_valid())

    def test_SwimForm_invalid_course(self):
        form = SwimForm(data={
            'duration': '00:26:30',
            'distance': '16',
            'units': 'yd',
            'course': 'sC',
        })
        self.assertFalse(form.is_valid())

class LiftForm_Test(TestCase):
    def test_LiftForm_valid(self):
        form = LiftForm(data={
            'movement': 'SN',
            'sets': '3',
            'reps': '2',
            'load': '58',
            'units': 'kg',
        })
        self.assertTrue(form.is_valid())

    def test_LiftForm_invalid_movement(self):
        form = LiftForm(data={
            'movement': 'run',
            'sets': '3',
            'reps': '2',
            'load': '12',
            'units': 'kg',
        })
        self.assertFalse(form.is_valid())

    def test_LiftForm_invalid_sets(self):
        form = LiftForm(data={
            'movement': 'OH',
            'sets': '-1',
            'reps': '1',
            'load': '10',
            'units': 'lb',
        })
        self.assertFalse(form.is_valid())

    def test_LiftForm_invalid_reps(self):
        form = LiftForm(data={
            'movement': 'PU',
            'sets': '10',
            'reps': '-1',
            'load': '10',
            'units': 'lb',
        })
        self.assertFalse(form.is_valid())

    def test_LiftForm_invalid_load(self):
        form = LiftForm(data={
            'movement': 'CJ',
            'sets': '3',
            'reps': '2',
            'load': '1.2',
            'units': 'kg',
        })
        self.assertFalse(form.is_valid())

    def test_LiftForm_invalid_units(self):
        form = LiftForm(data={
            'movement': 'BS',
            'sets': '2',
            'reps': '1',
            'load': '12',
            'units': 'kgs',
        })
        self.assertFalse(form.is_valid())

class BikeForm_Test(TestCase):
    def test_BikeForm_valid(self):
        form = BikeForm(data={
            'duration': '00:26:30',
            'distance': '16',
            'elevation_gain': '-100',
            'units': 'mi',
            'route': '',
        })
        self.assertTrue(form.is_valid())

    def test_BikeForm_invalid_neg_distance(self):
        form = BikeForm(data={
            'duration': '00:20:00',
            'distance': '-16',
            'elevation_gain': '100',
            'units': 'mi',
            'route': 'test',
        })
        self.assertFalse(form.is_valid())

    def test_BikeForm_invalid_float_distance(self):
        form = BikeForm(data={
            'duration': '00:20:00',
            'distance': '26.2',
            'elevation_gain': '100',
            'units': 'mi',
            'route': 'test',
        })
        self.assertFalse(form.is_valid())

    def test_BikeForm_invalid_distance(self):
        form = BikeForm(data={
            'duration': '00:20:00',
            'distance': 'FAR',
            'elevation_gain': '100',
            'units': 'mi',
            'route': 'test',
        })
        self.assertFalse(form.is_valid())

    def test_BikeForm_invalid_units(self):
        form = BikeForm(data={
            'duration': '00:20:00',
            'distance': '16',
            'elevation_gain': '100',
            'units': 'yards',
            'route': 'test',
        })
        self.assertFalse(form.is_valid())

    def test_BikeForm_invalid_neg_duration(self):
        form = BikeForm(data={
            'duration': '-00:20:00',
            'distance': '16',
            'elevation_gain': '100',
            'units': 'mi',
            'route': 'test',
        })
        self.assertFalse(form.is_valid())

    def test_BikeForm_invalid_duration(self):
        form = BikeForm(data={
            'duration': '00:y0:00',
            'distance': '16',
            'elevation_gain': '100',
            'units': 'mi',
            'route': 'test',
        })
        self.assertFalse(form.is_valid())

    def test_BikeForm_invalid_distance(self):
        form = BikeForm(data={
            'duration': '00:20:00',
            'distance': '2147483647',
            'elevation_gain': '100',
            'units': 'mi',
            'route': 'test',
        })
        self.assertFalse(form.is_valid())

    def test_BikeForm_invalid_route(self):
        form = BikeForm(data={
            'duration': '00:20:00',
            'distance': '16',
            'elevation_gain': '100',
            'units': 'mi',
            'route': 'testtesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttest',
        })
        self.assertFalse(form.is_valid())

class OtherForm_Test(TestCase):
    def test_OtherForm_valid_1(self):
        form = otherActivityForm(data={
            'duration': '00:23:50',
            'description': 'Bazinga'
        })
        self.assertTrue(form.is_valid())

    def test_OtherForm_valid_2(self):
        form = otherActivityForm(data={
            'duration': '00:76:90',
            'description': 'Here is my activity'
        })
        self.assertTrue(form.is_valid())

    def test_OtherForm_invalid_duration(self):
        form = otherActivityForm(data={
            'duration': '0I:76:90',
            'description': 'Here is my activity'
        })
        self.assertFalse(form.is_valid())

