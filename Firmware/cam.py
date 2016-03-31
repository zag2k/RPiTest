#!/usr/bin/env python

import logging
from logging.handlers import RotatingFileHandler
import picamera
from fractions import Fraction
import os

import sys
if sys.version_info[0] >= 3:
    import configparser as parser
else:
    import ConfigParser as parser

import time

second new feature

configParser = parser.RawConfigParser()   
configFilePath = '/home/pi/RPiWebCam/Firmware/config.txt'
configParser.read(configFilePath)
location = configParser.get('camera', 'location')
camera_name = configParser.get('camera', 'camera_name')
logs_path = configParser.get('camera', 'logs_path')

# Logging
log_file = logs_path + camera_name + '.log'
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(log_file, maxBytes=50000, backupCount=2)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - cam.py - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.addHandler(logging.StreamHandler())

def take(vflip, hflip, resolution_w, resolution_h, exposure_compensation, shutter_speed, exposure_mode, iso, file_name):
	result = False
	logger.debug("take called")
	logger.debug("before camera")

	logger.debug("vflip: %s", vflip)
	logger.debug("hflip: %s", hflip)
	logger.debug("resolution_w: %s", resolution_w)
	logger.debug("resolution_h: %s", resolution_h)
	logger.debug("exposure_compensation: %s", exposure_compensation)
	logger.debug("shutter_speed: %s", shutter_speed)
	logger.debug("exposure_mode: %s", exposure_mode)
	logger.debug("iso: %s", iso)
	logger.debug("file_name: %s", file_name)
	try:
		camera = picamera.PiCamera()
		try:
			camera.vflip = vflip
			logger.debug("vflip set")
			camera.hflip = hflip
			logger.debug("hflip set")
			camera.resolution = (resolution_w, resolution_h)
			logger.debug("resolution set")
			#camera.brightness = 55 #0 to 100, default 50
			#camera.exposure_compensation = 12 #-25 to 24, default 0
			camera.exposure_compensation = exposure_compensation
			logger.debug("exposure_compensation set")
			if shutter_speed == 6000000:
				camera.framerate = Fraction(1, 6)
			camera.shutter_speed = shutter_speed
			logger.debug("shutter_speed set")
			camera.exposure_mode = exposure_mode
			logger.debug("exposure_mode set")
			camera.iso = iso
			logger.debug("iso set")
			camera.capture(file_name)
		except:
			logger.debug('Error with camera settings.')
		finally:
			camera.close()
			result = True
	except:
		logger.debug('something went wrong with the camera!')
		#wait a few seconds and try again?
	logger.debug("camera done")

	logger.removeHandler(handler)

	return result

def burst(vflip, hflip, resolution_w, resolution_h, exposure_compensation, shutter_speed, exposure_mode, iso, file_name, number_of_images):
	result = False
	logger.debug("burst called")

	res = take(vflip, hflip, resolution_w, resolution_h, exposure_compensation, shutter_speed, exposure_mode, iso, "/home/pi/RPiWebCam/Test/take-photo-test1.jpg")
	time.sleep(5)
	res = take(vflip, hflip, resolution_w, resolution_h, exposure_compensation, shutter_speed, exposure_mode, iso, "/home/pi/RPiWebCam/Test/take-photo-test2.jpg")
	time.sleep(5)
	res = take(vflip, hflip, resolution_w, resolution_h, exposure_compensation, shutter_speed, exposure_mode, iso, "/home/pi/RPiWebCam/Test/take-photo-test3.jpg")
	time.sleep(5)
	res = take(vflip, hflip, resolution_w, resolution_h, exposure_compensation, shutter_speed, exposure_mode, iso, "/home/pi/RPiWebCam/Test/take-photo-test4.jpg")
	time.sleep(5)
	res = take(vflip, hflip, resolution_w, resolution_h, exposure_compensation, shutter_speed, exposure_mode, iso, "/home/pi/RPiWebCam/Test/take-photo-test5.jpg")

	logger.debug("burst done")

	logger.removeHandler(handler)

	return result


def takeVid(vflip, hflip, resolution_w, resolution_h, exposure_compensation, seconds, exposure_mode, iso, file_name):
	result = False
	logger.debug("take called")
	logger.debug("before camera")

	logger.debug("vflip: %s", vflip)
	logger.debug("hflip: %s", hflip)
	logger.debug("resolution_w: %s", resolution_w)
	logger.debug("resolution_h: %s", resolution_h)
	logger.debug("exposure_compensation: %s", exposure_compensation)
	logger.debug("seconds: %s", seconds)
	logger.debug("exposure_mode: %s", exposure_mode)
	logger.debug("iso: %s", iso)
	logger.debug("file_name: %s", file_name)
	try:
		camera = picamera.PiCamera()
		try:
			camera.vflip = vflip
			logger.debug("vflip set")
			camera.hflip = hflip
			logger.debug("hflip set")
			camera.resolution = (resolution_w, resolution_h)
			logger.debug("resolution set")
			camera.exposure_compensation = exposure_compensation
			logger.debug("exposure_compensation set")
			camera.exposure_mode = exposure_mode
			logger.debug("exposure_mode set")
			camera.iso = iso
			logger.debug("iso set")
			camera.start_recording(file_name)
			camera.wait_recording(seconds)
			camera.stop_recording()
		except:
			logger.debug('Error with camera settings.')
		finally:
			camera.close()
			#Convert to mp4
			os.system("MP4Box -fps 30 -add " + file_name + " " + file_name.replace("h264", "mp4"))
			result = True
	except:
		logger.debug('something went wrong with the camera!')
		#wait a few seconds and try again?
	logger.debug("camera done")

	logger.removeHandler(handler)

	return result

if __name__ == '__main__':
	res = take(True, True, 2592, 1944, 0, 1200, "auto", 100, "/home/pi/RPiWebCam/take-photo-test-1200.jpg")
	#res = burst(True, True, 1920, 1080, 0, 0, "auto", 800, "/home/pi/RPiWebCam/Test/take-photo-test.jpg", 5)
	#res = takeVid(True, True, 1280, 720, 0, 6, "auto", 800, "/home/pi/RPiWebCam/Test/test.h264")

	if res == True:
		logger.debug("Success!")