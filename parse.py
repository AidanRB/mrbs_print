#!/usr/bin/python3

from datetime import datetime

# Open and read the file
#filename = input("input filename: ")
#csvfile = open(filename, 'r').read()

def parse(csvtext):
    # Split the file into rows/items
    lines = csvtext.split('"\n"')
    fulllines = []
    for line in lines:
        fulllines += [line.split('","')]

    # Delete extra characters
    del fulllines[0]
    fulllines[-1][-1] = fulllines[-1][-1][:-2]

    # Parse raw CSV data into name, area/s, room/s, start time, end time
    events = []
    for neweventraw in fulllines:
        # Create new event as dictionary
        newevent = {}
        newevent['name'] = neweventraw[0]
        newevent['areas'] = [neweventraw[1]]
        newevent['rooms'] = [neweventraw[2]]
        newevent['start'] = datetime.strptime(neweventraw[3], '%I:%M%p - %A %d %B %Y')
        newevent['end'] = datetime.strptime(neweventraw[4], '%I:%M%p - %A %d %B %Y')

        # Merge with existing event in case of multiple rooms
        adding = True
        for event in events:
            if [event['name'], event['start'], event['end']] == [newevent['name'], newevent['start'], newevent['end']]:
                adding = False
                if newevent['areas'][0] not in event['areas']:
                    event['areas'] += newevent['areas']
                if newevent['rooms'][0] not in event['rooms']:
                    event['rooms'] += newevent['rooms']
                break

        # Add event if not merging
        if adding:
            events += [newevent]

    # Sort events by start time
    events = sorted(events, key = lambda i: i['start'])

    return events
