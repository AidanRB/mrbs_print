#! /usr/bin/python3.6

import random
import string
import datetime
from itertools import groupby
from operator import itemgetter
from flask import Flask, render_template, request, flash, redirect
from wtforms import Form, TextField, TextAreaField, validators, StringField, PasswordField, SubmitField
from wtforms.fields.html5 import DateField
import getreport
from parse import parse
import defaults

# Set root URL for MRBS
getreport.rootURL = defaults.rootURL
# Global loggedin
loggedin = False


# Define login form
class LoginForm(Form):
    username = StringField('Username:', validators=[validators.DataRequired()])
    password = PasswordField('Password:', validators=[validators.DataRequired()])


# Define form for form page
class DateForm(Form):
    from_date = DateField('The week of:', format='%Y-%m-%d',
                          validators=[validators.DataRequired()])
    areamatch = StringField('Areas:', validators=[validators.DataRequired()])


# Set up flask
app = Flask(__name__)
app.config['SECRET_KEY'] = ''.join(
    random.choice(string.ascii_letters) for i in range(64))

# Root URL
@app.route("/")
def mainpage():
    # Redirect to form if logged in
    if loggedin:
        return redirect("form")
    # Redirect to login if not logged in
    else:
        return redirect("login")


# Login page
@app.route("/login", methods=['GET', 'POST'])
def loginpage(username="", password=""):
    global loggedin
    # Redirect to the form if already logged in
    if loggedin:
        return redirect("form")
    form = LoginForm(request.form)
    # Attempt log in if post recieved
    if request.method == "POST":
        if form.validate() and getreport.login(request.form["username"], request.form["password"]):
            loggedin = True
            # Redirect to form if logged in
            return redirect("form")
        else:
            # Flash error message in case of incorrect user/pass
            flash("Please try again")
            return render_template("login.html", form=form)
    # Show login page if get recieved
    else:
        return render_template("login.html", form=form)


# Form for calendar/rendering calendar
@app.route("/form", methods=['GET'])
def printpage():
    form = DateForm(request.form)
    # If not logged in, redirect to login
    if not loggedin:
        return redirect("login")
    # If logged in, move on to the form/render
    else:
        # Find next monday and set it as the prefilled area in the form
        monday = datetime.date.today()
        monday += datetime.timedelta(days=-
                                     datetime.date.today().weekday(), weeks=1)
        mondaytext = monday.strftime('%Y-%m-%d')
        return render_template("form.html", form=form, last_monday=mondaytext,
                defaultarea=defaults.area, placeholder=defaults.areaplaceholder)


@app.route("/print", methods=['GET'])
def showcal():
    # If not logged in, redirect to login
    if not loggedin:
        return redirect("login")
    # If logged in, show calendar
    elif loggedin:
        # Find next monday for default date if none provided
        monday = datetime.date.today()
        monday += datetime.timedelta(days=-
                                     datetime.date.today().weekday(), weeks=1)
        mondaytext = monday.strftime('%Y-%m-%d')

        # Set defaults
        from_date = request.args.get('from_date', default=mondaytext)
        areamatch = request.args.get('areamatch', default=defaults.area)

        # Set to_data to six days after from_date
        from_date_dt = datetime.datetime.strptime(from_date, '%Y-%m-%d')
        to_date_dt = from_date_dt + datetime.timedelta(days=6)
        to_date = to_date_dt.strftime('%Y-%m-%d')
        prev_week_dt = from_date_dt - datetime.timedelta(days=7)
        prev_week = prev_week_dt.strftime('%Y-%m-%d')
        next_week_dt = from_date_dt + datetime.timedelta(days=7)
        next_week = next_week_dt.strftime('%Y-%m-%d')

        # Get and parse report
        rawreport = getreport.getreport(from_date, to_date, areamatch)
        report = parse(rawreport)

        # Create arrays to send to template
        days = []
        weekdays = []
        daynumbers = []
        months = []
        month = from_date_dt.strftime('%B') + ' ' + from_date_dt.strftime('%Y')
        weeknumber = int(from_date_dt.strftime('%W')) + 1
        for i in range(7):
            currentdate = from_date_dt + datetime.timedelta(days=i)
            days += [currentdate]
            weekdays += [currentdate.strftime('%a').lower()]
            daynumbers += [currentdate.strftime('%d')]
            months += [currentdate.strftime('%b')]

        # Create empty array of events
        events = [[], [], [], [], [], [], []]
        # Go through report and add events to events
        for event in report:
            # nth day of the report (ie, 0-6)
            number = (event['start'] - from_date_dt).days
            # String for displayed times
            times = ''
            # Start time - Ignore minutes if they're 0
            if(event['start'].minute == 0):
                times += event['start'].strftime('%-I%p').lower()
            else:
                times += event['start'].strftime('%-I:%M%p').lower()
            times += '-'
            # End time
            if(event['end'].minute == 0):
                times += event['end'].strftime('%-I%p').lower()
            else:
                times += event['end'].strftime('%-I:%M%p').lower()

            # Array for rooms with numbers
            roomnumbers = []
            # Array for rooms with alpha names
            roomstrings = []
            # Add numbers to roomnumbers and strings to roomstrings
            for room in event['rooms']:
                try:
                    roomnumbers += [int(room)]
                except ValueError:
                    roomstrings += [room]
            # Array for runs of numbers (eg 1,2,3 or 13,14,15)
            roomsequences = []
            # Separate rooms into sequences and add to roomsequences
            for k, g in groupby(enumerate(roomnumbers), lambda ix: ix[0] - ix[1]):
                roomsequences += [list(map(itemgetter(1), g))]
            # Array for comma-separated values to print
            finalrooms = []
            # Add sequences to finals
            for sequence in roomsequences:
                # Turn 13,14,15 into 13-15, etc
                if len(sequence) > 1:
                    roomstring = str(sequence[0])
                    roomstring += '-'
                    roomstring += str(sequence[-1])
                # Single rooms
                else:
                    roomstring = str(sequence[0])
                # Add current sequence to finals
                finalrooms += [roomstring]
            # Add non-numeric rooms to finals and join them all with commas
            rooms = ', '.join(finalrooms + roomstrings)

            # Get name of event
            name = event['name']
            # Add event to events[]
            events[number] += [[times, rooms, name]]

        return render_template("week.html", from_date=from_date, events=events,
                               weekdays=weekdays, daynumbers=daynumbers,
                               month=month, months=months, weeknumber=weeknumber,
                               prevweek=prev_week, nextweek=next_week, areas=areamatch)


if __name__ == "__main__":
    app.run()
