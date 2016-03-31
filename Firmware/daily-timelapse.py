#!/usr/bin/python

import os
import datetime
import logging
from logging.handlers import RotatingFileHandler
import ConfigParser
import upload

configParser = ConfigParser.RawConfigParser()   
configFilePath = '/home/pi/RPiWebCam/Firmware/config.txt'
configParser.read(configFilePath)
application_folder = configParser.get('camera', 'application_folder')
camera_location = configParser.get('camera', 'location')
camera_name = configParser.get('camera', 'camera_name')
logs_path = configParser.get('camera', 'logs_path')

# Logging
log_file = logs_path + camera_name + '.log'
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(log_file, maxBytes=100000, backupCount=5)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - daily-timelapse.py - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.addHandler(logging.StreamHandler())

now = datetime.datetime.now()

path="/home/pi/RPiWebCam/DailyTimeLapse/"

#GENERATE MOVIE FILE
def generate_video():
	filename = now.strftime("%Y-%m-%d")

	cmd = "mencoder -nosound -ovc lavc -lavcopts vcodec=mpeg4:aspect=16/9:vbitrate=8000000 -vf scale=1920:1080 -o " + path + filename + ".avi -mf type=jpeg:fps=10 mf://" + path + "*.jpg"
	os.system(cmd)
	print ("generate done")

	logger.debug("Success!")
	upload.upload_file(path, filename + ".avi", "/" + camera_location + "/" + camera_name + "/Time-Lapse/Daily/", filename + ".avi", file_description="Daily Timelapse", new_file_revision=False, delete_after_upload=True, notify=True)
	logger.debug("Upload done")

#upload movie
#clean up files

#def upload_files():
#	if not os.path.exists(path):
#		return
#	dir_list = os.listdir(path)
#	for file_name in dir_list:
#		if "avi" in file_name:
#			#print "Uploaded"
#			#cmd = "/home/pi/RPiWebCam/dropbox_uploader.sh upload " + path + file_name + " /NewCam/DailyTimeLapse/" + file_name
#			#os.system(cmd)
#			cmd = 'python /home/pi/RPiWebCam/gdrive_uploader.py "--noauth_local_webserver" ' + path + ' ' + file_name + ' "/Lake/Front Roof/Time-Lapse/Daily/" ' + file_name + ' False True'
#			os.system(cmd)
#			#os.remove(path + file_name)
#		#else:
#			#os.remove(path + file_name)

if __name__ == "__main__":
	generate_video()
	#upload_files()
