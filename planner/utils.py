from datetime import datetime, timedelta
from calendar import HTMLCalendar
from .models import Item


#################################################################################################################
# This Code is largely based on Hui Wen's Django Calendar tutorial. See planner/view.py for the full citation
#################################################################################################################


# This overrides some of the existing django Calendar class methods.
class Calendar(HTMLCalendar):
	def __init__(self, year=None, month=None):
		self.year = year
		self.month = month
		super(Calendar, self).__init__()

	# formats a day as a td
	# filter events by day
	def formatday(self, day, events, points_earned):
		events_per_day = events.filter(end_time__day=day)
		d = ''


		#displays a link for each event
		for event in events_per_day:
			if(event.points_earned >= event.points): # if the event (goal item) is complete, say COMPLETE
				d += f'<li> {event.get_html_url} (COMPLETE) </li>'  # if complete, dont display fraction
			else: # goal is not comlete, display progress as a fraction
				d += f'<li> {event.get_html_url} ({event.points_earned}/{event.points}) </li>' # displays fraction

		if day != 0:
			return f"<td><span class='date'>{day}</span><ul> {d} </ul></td>"
		return '<td></td>'

	# formats a week as a tr
	def formatweek(self, theweek, events, points_earned):
		week = ''
		for d, weekday in theweek:
			# pass to formatday above
			week += self.formatday(d, events, points_earned)
		return f'<tr> {week} </tr>'

	# formats a month as a table
	# filter events by year and month
	def formatmonth(self, user, points_earned, withyear=True):
		# get Items (calendar events) for this user and that are for the month being displayed
		events = Item.objects.filter(
			end_time__year=self.year,
			end_time__month=self.month,
			user = user,
		)
		cal = f'<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'
		cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
		cal += f'{self.formatweekheader()}\n'
		# send to formatweek above, along with list of events and the points earned from user (calculated in view)
		for week in self.monthdays2calendar(self.year, self.month):
			cal += f'{self.formatweek(week, events, points_earned)}\n'
		return cal