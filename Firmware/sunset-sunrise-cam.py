#!/usr/bin/env python

import os
import ephem
import datetime
import time
from datetime import timedelta
from datetime import date
import logging
from logging.handlers import RotatingFileHandler
import ConfigParser
from fractions import Fraction
import cam
import upload

configParser = ConfigParser.RawConfigParser()   
configFilePath = '/home/pi/RPiWebCam/Firmware/config.txt'
configParser.read(configFilePath)
application_folder = configParser.get('camera', 'application_folder')
camera_location = configParser.get('camera', 'location')
camera_name = configParser.get('camera', 'camera_name')
vflip = configParser.getboolean('camera', 'default_vflip')
hflip = configParser.getboolean('camera', 'default_hflip')
resolution_w = configParser.getint('camera', 'default_resolution_w')
resolution_h = configParser.getint('camera', 'default_resolution_h')
logs_path = configParser.get('camera', 'logs_path')
sunset_sunrise = configParser.getboolean('camera', 'sunset_sunrise')

# Logging
log_file = logs_path + camera_name + '.log'
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(log_file, maxBytes=100000, backupCount=5)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - sunset-sunrise-cam.py - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.addHandler(logging.StreamHandler())

location      = ephem.Observer()
location.date = datetime.date.today()
# should really calculate midnight taking into acount DST
mid = ephem.Date(date.today().strftime("%Y-%m-%d 9:00"))

# Lake
# As Degrees Minutes Dir
# lat 48 14'3
# lon 116 27'23.8"W
#
# As Decimal
# lat 48.241664
# lon -116.456619
#
# Time zone -8
location.lon  = str(-116.456619) 	# Note that lon should be in string format
location.lat  = str(48.241664)		# Note that lat should be in string format

# Elevation
# 630.801 m or 2069.558 feet
location.elev = 631		# Elevation in Meters

# To get U.S. Naval Astronomical Almanac values, use these settings
location.pressure = 0
location.horizon = '-0:34'

sunrise = ephem.localtime(location.next_rising(ephem.Sun(), start=mid))			#Sunrise
noon = ephem.localtime(location.next_transit(ephem.Sun(), start=mid))			#Solar noon
sunset = ephem.localtime(location.next_setting(ephem.Sun(), start=mid))			#Sunset

# Relocate the horizon to get twilight times - -6=civil twilight, -12=nautical, -18=astronomical
location.horizon = '-18'
beg_astronomical_twilight = ephem.localtime(location.next_rising(ephem.Sun(), use_center=True, start=mid))
end_astronomical_twilight = ephem.localtime(location.next_setting(ephem.Sun(), use_center=True, start=mid))
location.horizon = '-12'
beg_nautical_twilight = ephem.localtime(location.next_rising(ephem.Sun(), use_center=True, start=mid))
end_nautical_twilight = ephem.localtime(location.next_setting(ephem.Sun(), use_center=True, start=mid))
location.horizon = '-6'
beg_civil_twilight = ephem.localtime(location.next_rising(ephem.Sun(), use_center=True, start=mid))
end_civil_twilight = ephem.localtime(location.next_setting(ephem.Sun(), use_center=True, start=mid))

# Debug
logger.debug('Date: %s', location.date)
logger.debug('astronomical twilight begin local: %s', beg_astronomical_twilight)
logger.debug('nautical twilight begin local: %s', beg_nautical_twilight)
logger.debug('civil twilight begin local: %s', beg_civil_twilight)
logger.debug('sunrise local: %s', sunrise)
logger.debug('solar noon local: %s', noon)
logger.debug('sunset local: %s', sunset)
logger.debug('civil twilight end local: %s', end_civil_twilight)
logger.debug('nautical twilight end local: %s', end_nautical_twilight)
logger.debug('astronomical twilight end local: %s', end_astronomical_twilight)

current_time = ephem.Date(datetime.datetime.now()).datetime()

if sunset_sunrise == True:
	if current_time >= end_nautical_twilight or current_time <= beg_nautical_twilight:
		res = cam.take(vflip=vflip, hflip=hflip, resolution_w=resolution_w, resolution_h=resolution_h, exposure_compensation=0, shutter_speed=6000000, exposure_mode="verylong", iso=800, file_name="/home/pi/" + application_folder + "/Daily/" + current_time.strftime("%Y-%m-%d-%H-%M-6") + ".jpg")

		if res == True:
			logger.debug("Success!")
			#os.system("/home/pi/RPiWebCam/sunset-sunrise-upload.py")
			upload.upload_files_in_folder("/home/pi/RPiWebCam/Daily/", "/" + camera_location + "/" + camera_name + "/Daily/" + date.today().strftime("%Y-%m-%d") + "/", file_description="Sunset-Sunrise Image", new_file_revision=False, delete_after_upload=True, notify=False)
			logger.debug("Upload done")
else:
	logger.info("Sunset Sunrise disabled in config.txt.")
