#!/usr/bin/env python

import os
import ephem
import datetime
import time
from datetime import timedelta
from datetime import date
import sched

# Make an observer
location      = ephem.Observer()

#print "hello"

# PyEphem takes and returns only UTC times.
#location.date = "2013-09-04 15:00:00"
location.date = datetime.date.today()

# should really calculate midnight taking into acount DST
mid = ephem.Date(date.today().strftime("%Y-%m-%d 9:00"))
#print "Midnight = ", mid
#print "Local Midnight = ", ephem.localtime(mid)

# Debug
#print "current date: ", location.date

location.lon  = str(-116.456619) 	# Note that lon should be in string format
location.lat  = str(48.241664)		# Note that lat should be in string format

# Elevation
# 630.801 m or 2069.558 feet
location.elev = 631		# Elevation in Meters

# To get U.S. Naval Astronomical Almanac values, use these settings
location.pressure = 0
location.horizon = '-7'

end_astronomical_twilight = ephem.localtime(location.next_setting(ephem.Sun(), use_center=True, start=mid))

print 'Civil Twilight: ', end_astronomical_twilight
print 'Civil Twilight', end_astronomical_twilight.strftime('%a %b %d %H:%M:%S %Y')

scheduler = sched.scheduler(time.time, time.sleep)

def timelapse(name):
	os.system("/home/pi/RPiWebCam/Firmware/daily-timelapse.py")

print 'START:', time.time()

#
#t = time.mktime(time.strptime("wed oct 15 21:30:00 2014", '%a %b %d %H:%M:%S %Y'))
t = time.mktime(time.strptime(end_astronomical_twilight.strftime('%a %b %d %H:%M:%S %Y'), '%a %b %d %H:%M:%S %Y'))
scheduler.enterabs(t, 1, timelapse, ('first',))
#scheduler.enter(3, 1, print_event, ('secnd',))
#

print t

scheduler.run()
