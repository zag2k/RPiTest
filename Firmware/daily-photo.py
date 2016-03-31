#!/usr/bin/env python

import os
import ephem
import datetime
import time
from datetime import timedelta
from datetime import date
import sched
from xml.dom import minidom
import urllib2
import json
import logging
from logging.handlers import RotatingFileHandler
import subprocess
import ConfigParser

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
daily_photo = configParser.getboolean('camera', 'daily_photo')
wu_api_key = configParser.get('camera', 'wu_api_key')
wu_state = configParser.get('camera', 'wu_state')
wu_city = configParser.get('camera', 'wu_city')
shutter_speed = configParser.getint('camera', 'default_shutter_speed')

# Logging
log_file = logs_path + camera_name + '.log'
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(log_file, maxBytes=100000, backupCount=5)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - daily-photo.py - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.addHandler(logging.StreamHandler())

# Data URLs
WU_CONDITIONS_URL = 'http://api.wunderground.com/api/' + wu_api_key + '/geolookup/conditions/q/' + wu_state + '/' + wu_city + '.json'
logger.debug('WU Conditions URL: %s', WU_CONDITIONS_URL)

WU_ASTRONOMY_URL = 'http://api.wunderground.com/api/' + wu_api_key + '/astronomy/q/' + wu_state + '/' + wu_city + '.json'
logger.debug('WU Astronomy URL: %s', WU_ASTRONOMY_URL)

NOAA_URL = 'http://water.weather.gov/ahps2/hydrograph_to_xml.php?gage=hopi1&output=xml'
logger.debug('NOAA URL: %s', NOAA_URL)

def solar_noon(name):
	if daily_photo == True:
		logger.debug('Daily Photo Running')

		dom = minidom.parse(urllib2.urlopen(NOAA_URL))
		datums = dom.getElementsByTagName("datum")
		#print datums[0].getElementsByTagName("valid")[0].childNodes[0].data
		LAKE_LEVEL = datums[0].getElementsByTagName("primary")[0].childNodes[0].data + " ft"
		utc = datetime.datetime.strptime(datums[0].getElementsByTagName("valid")[0].childNodes[0].data, '%Y-%m-%dT%H:%M:%S-00:00')
		OBSERVED = utc.strftime("%Y-%m-%d")

		f = urllib2.urlopen(WU_CONDITIONS_URL)
		json_string = f.read()
		parsed_json = json.loads(json_string)
		location = parsed_json['location']['city']
		weather = parsed_json['current_observation']['weather']
		temp_f = parsed_json['current_observation']['temp_f']
		relative_humidity = parsed_json['current_observation']['relative_humidity']
		wind_string = parsed_json['current_observation']['wind_string']
		wind_dir = parsed_json['current_observation']['wind_dir']
		wind_mph = parsed_json['current_observation']['wind_mph']
		wind_gust_mph = parsed_json['current_observation']['wind_gust_mph']
		f.close()

		f = urllib2.urlopen(WU_ASTRONOMY_URL)
		json_string = f.read()
		parsed_json = json.loads(json_string)
		percentIlluminated = parsed_json['moon_phase']['percentIlluminated']
		f.close()

		logger.debug('Weather Data - city: %s; weather: %s; temp_f: %s; relative_humidity: %s; wind_string: %s; wind_dir: %s; wind_mph: %s; wind_gust_mph: %s; percentIlluminated: %s', location, weather, temp_f, relative_humidity, wind_string, wind_dir, wind_mph, wind_gust_mph, percentIlluminated)

		filename = noon.strftime("%Y-%m-%d-%H-%M-%S")

		logger.debug('Taking Photo')
		#os.system("raspistill -w 1920 -h 1080 -vf -hf -o /home/pi/RPiWebCam/SolarNoon/" + filename + ".jpg")
		res = cam.take(vflip=vflip, hflip=hflip, resolution_w=resolution_w, resolution_h=resolution_h, exposure_compensation=0, shutter_speed=shutter_speed, exposure_mode="auto", iso=100, file_name="/home/pi/" + application_folder + "/SolarNoon/" + filename + ".jpg")

		#x = subprocess.check_output(["raspistill -w 1920 -h 1080 -vf -hf -o /home/pi/RPiWebCam/SolarNoon/" + filename + ".jpg"])
		#logger.debug('x: %s', x)

		logger.debug('Adding Overlay to Photo')
		os.system("convert /home/pi/RPiWebCam/SolarNoon/" + filename + ".jpg"
			+ " -strokewidth 0 -fill 'rgba( 140, 140, 140, 0.8 )' -draw 'rectangle 30,1060 750,675'"
			+ " -pointsize 36 -fill white -annotate +40+720 '" + noon.strftime("%m/%d/%Y")
			+ "' -pointsize 36 -fill white -annotate +40+800 'Temperature:"
			+ "' -pointsize 36 -fill white -annotate +275+800 '" + str(temp_f)
			+ "' -pointsize 36 -fill white -annotate +40+840 'Wind: "
			+ "' -pointsize 36 -fill white -annotate +275+840 'From the " + wind_dir + " at " + str(wind_mph) + " MPH"
			+ "' -pointsize 36 -fill white -annotate +40+880 'Lake Level:"
			+ "' -pointsize 36 -fill white -annotate +275+880 '" + LAKE_LEVEL
			+ "' -pointsize 36 -fill white -annotate +40+920 'Sunrise:"
			+ "' -pointsize 36 -fill white -annotate +275+920 '" + sunrise.strftime("%I:%M %p")
			+ "' -pointsize 36 -fill white -annotate +40+960 'Solar Noon:"
			+ "' -pointsize 36 -fill white -annotate +275+960 '" + noon.strftime("%I:%M %p")
			+ "' -pointsize 36 -fill white -annotate +40+1000 'Sunset:"
			+ "' -pointsize 36 -fill white -annotate +275+1000 '" + sunset.strftime("%I:%M %p")
			+ "' -pointsize 36 -fill white -annotate +40+1040 'Moon:"
			+ "' -pointsize 36 -fill white -annotate +275+1040 '" + str(percentIlluminated) + "%"
			+ "' /home/pi/RPiWebCam/SolarNoon/" + filename + "-o.jpg")

		logger.debug('Uploading Photo')
		#os.system("/home/pi/RPiWebCam/daily-photo-upload.py")

		upload.upload_file("/home/pi/RPiWebCam/SolarNoon/", filename + ".jpg", "/" + camera_location + "/" + camera_name + "/Solar Noon/", filename + ".jpg", file_description="Solar Noon Image", new_file_revision=False, delete_after_upload=True, notify=False)
		upload.upload_file("/home/pi/RPiWebCam/SolarNoon/", filename + "-o.jpg", "/" + camera_location + "/" + camera_name + "/Solar Noon/Overlay", filename + "-o.jpg", file_description="Solar Noon Overlay Image", new_file_revision=False, delete_after_upload=True, notify=True)
	else:
		logger.info("Daily Photo disabled in config.txt.")

	logger.removeHandler(handler)


location      = ephem.Observer()
location.date = datetime.date.today()

mid = ephem.Date(date.today().strftime("%Y-%m-%d 9:00")) # should really calculate midnight taking into acount DST
logger.debug('Midnight: %s', mid)
logger.debug('Local Midnight: %s', ephem.localtime(mid))

logger.debug('Current Date: %s', location.date)

location.lon  = str(-116.456619) 	# Note that lon should be in string format
location.lat  = str(48.241664)		# Note that lat should be in string format
location.elev = 645		# Elevation in Meters 631
location.pressure = 0
location.horizon = '-0:34'

logger.debug('Location Data - lon: %s; lat: %s; elev: %s; pressure: %s; horizon: %s', location.lon, location.lat, location.elev, location.pressure, location.horizon)

noon = ephem.localtime(location.next_transit(ephem.Sun(), start=mid))			#Solar noon
sunrise = ephem.localtime(location.next_rising(ephem.Sun(), start=mid))			#Sunrise
sunset = ephem.localtime(location.next_setting(ephem.Sun(), start=mid))			#Sunset

logger.debug('Time Data - Solar Noon: %s; Sunrise: %s; Sunset: %s;', noon.strftime('%a %b %d %H:%M:%S %Y'), sunrise.strftime('%a %b %d %H:%M:%S %Y'), sunset.strftime('%a %b %d %H:%M:%S %Y'))

scheduler = sched.scheduler(time.time, time.sleep)

t = time.mktime(time.strptime(noon.strftime('%a %b %d %H:%M:%S %Y'), '%a %b %d %H:%M:%S %Y'))
scheduler.enterabs(t, 1, solar_noon, ('first',))

scheduler.run()
logger.info('Daily photo scheduled for: %s;', noon.strftime('%a %b %d %H:%M:%S %Y'))

# for debugging/testing
#solar_noon('first')

#logger.removeHandler(handler)
