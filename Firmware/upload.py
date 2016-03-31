#!/usr/bin/env python

import logging
from logging.handlers import RotatingFileHandler
import picamera
from fractions import Fraction
import os
import gdrive_uploader

import sys
if sys.version_info[0] >= 3:
    import configparser as parser
else:
    import ConfigParser as parser

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
handler = RotatingFileHandler(log_file, maxBytes=100000, backupCount=5)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - upload.py - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.addHandler(logging.StreamHandler())

def upload_files_in_folder(source_path, destination_path, file_description, new_file_revision, delete_after_upload, notify):
	result = False
	logger.debug("source_path: %s", source_path)
	logger.debug("destination_path: %s", destination_path)
	logger.debug("new_file_revision: %s", new_file_revision)
	logger.debug("delete_after_upload: %s", delete_after_upload)
	logger.debug("notify: %s", notify)

	if not os.path.exists(source_path):
		return False
	dir_list = os.listdir(source_path)
	for file_name in dir_list:
		if "jpg" in file_name:
			if "jpg~" in file_name:
				logger.debug("skipping file: %s", file_name)
			else:
				logger.debug("Upload jpg")
				#cmd = 'python /home/pi/RPiWebCam/gdrive_uploader.py "--noauth_local_webserver" ' + path + ' ' + file_name + ' "/Lake/Front Roof/InstaPic/' + date.today().strftime("%Y-%m-%d") + '" ' + file_name + ' False True'
				#os.system(cmd)

				res = gdrive_uploader.gdrive_upload(source_path, file_name, destination_path, file_name, file_description, delete_after_upload, notify)

				if res == True and delete_after_upload == True:
					logger.debug("Upload successful so delete file")
					os.remove(source_path + file_name)
					result = True

		if "mp4" in file_name:
			logger.debug("Upload mp4")

			res = gdrive_uploader.gdrive_upload(source_path, file_name, destination_path, file_name, file_description, delete_after_upload, notify)

			if res == True and delete_after_upload == True:
				logger.debug("Upload successful so delete file")
				os.remove(source_path + file_name)
				os.remove(source_path + file_name.replace("mp4", "h264"))

				result = True

	return result

def upload_file(source_path, source_filename, destination_path, destination_filename, file_description, new_file_revision, delete_after_upload, notify):
	result = False

	logger.debug("source_path: %s", source_path)
	logger.debug("source_filename: %s", source_filename)
	logger.debug("destination_path: %s", destination_path)
	logger.debug("destination_filename: %s", destination_filename)
	logger.debug("new_file_revision: %s", new_file_revision)
	logger.debug("delete_after_upload: %s", delete_after_upload)
	logger.debug("notify: %s", notify)

	res = gdrive_uploader.gdrive_upload(source_path, source_filename, destination_path, destination_filename, file_description, delete_after_upload, notify)

	if res == True and delete_after_upload == True:
		logger.debug("Upload successful so delete file")
		os.remove(source_path + source_filename)
		result = True
	elif res == True:
		result = True

	return result


if __name__ == '__main__':
	#res = upload_files_in_folder("/home/pi/RPiWebCam/Test/", "/RPiWebCam/Lake/Front Roof/", new_file_revision=False, delete_after_upload=True, file_description="Test Image", notify=True)
	res = upload_file("/home/pi/RPiWebCam/Test/", "take-photo-test4.jpg", "/Lake/Front Roof/", "take-photo-test4.jpg", file_description="Test Image", new_file_revision=False, delete_after_upload=True, notify=True)

	if res == True:
		logger.debug("Success!")
