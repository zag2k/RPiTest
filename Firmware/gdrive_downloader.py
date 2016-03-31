#!/usr/bin/python

import httplib2
import pprint
import sys

from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from oauth2client.client import OAuth2WebServerFlow

from oauth2client.file import Storage
from oauth2client.client import flow_from_clientsecrets
from oauth2client.tools import run
from apiclient.discovery import build

import argparse
from oauth2client import tools

import logging
from logging.handlers import RotatingFileHandler
import ConfigParser

import json

# python /home/pi/RPiWebCam/gdrive_downloader.py --noauth_local_webserver "/Lake/Front Roof/Firmware Updates/" test.py "/home/pi/RPiWebCam/Test/" True

configParser = ConfigParser.RawConfigParser()   
configFilePath = '/home/pi/RPiWebCam/Firmware/config.txt'
configParser.read(configFilePath)
camera_name = configParser.get('camera', 'camera_name')
logs_path = configParser.get('camera', 'logs_path')

# Logging
log_file = logs_path + camera_name + '.log'
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(log_file, maxBytes=50000, backupCount=2)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - gdrive_downloader.py - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.addHandler(logging.StreamHandler())

#CALL: python gdrive_uploader.py --noauth_local_webserver /home/pi/RPiWebCam/Test/ test.jpg /Lake/Daily/2015-04-16/ test.jpg False

#RpiWebCam/Lake/Daily/2015-04-15
#RpiWebCam/Lake/Daily/DailyTimeLapse

def get_parent_id_of_gdrive_folder(service, application_folder, folders):
	files = []

	for folder in folders:
		print(folder)

	param = {}
	#q = "title contains 'RPiWebCam'"

	#Get RPiWebCam folder under root
	q = "title = '" + application_folder + "' and 'root' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
	param['q'] = q
	file_items = service.files().list(**param).execute().get('items', [])

	pid = "0"

	if len(file_items) == 1:
		#logger.debug('title: %s', file_items[0]['title'])
		#logger.debug('mimeType: %s', file_items[0]['mimeType'])
		#logger.debug('id: %s', file_items[0]['id'])
		pid = file_items[0]['id']
		logger.debug('ID for RPiWebCam: %s', pid)
 		parent_id = pid

	for folder in folders:
		q = "title = '" + folder + "' and '" + pid + "' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
		logger.debug('q: %s', q)
		param['q'] = q
 		file_items = service.files().list(**param).execute().get('items', [])

		pid = "0"

 		if len(file_items) == 1:
			#logger.debug('title: %s', file_items[0]['title'])
			#logger.debug('mimeType: %s', file_items[0]['mimeType'])
			#logger.debug('id: %s', file_items[0]['id'])
			pid = file_items[0]['id']
			logger.debug('ID for %s: %s', folder, pid)
			parent_id = pid
		else:
			logger.debug('Did not find folder: %s', folder)

	return pid



def get_file_id(service, parent_id, title):
	result = False
	files = []
	param = {}
	id = ""
	content = ""

	logger.debug('parent_id: %s', parent_id)
	logger.debug('title: %s', title)

	q = "title = '" + title + "' and '" + parent_id + "' in parents and trashed = false"
	param['q'] = q
	file_items = service.files().list(**param).execute().get('items', [])

	if len(file_items) > 0:
		result = True
		id = file_items[0]['id']
		
		download_url = file_items[0]['downloadUrl']
		logger.debug('downloadUrl: %s', download_url)

		if download_url:
			resp, content = service._http.request(download_url)
    		if resp.status == 200:
    			print 'Status: %s' % resp
    		else:
				print 'An error occurred: %s' % resp

	return result, id, content

def download_file(service, gdrive_file_name, parent_id, destination_path, remove_after_download="False"):
	logger.debug('remove_after_download: %s', remove_after_download)

	if parent_id != "0":
		exists, id, filecontent = get_file_id(service, parent_id, gdrive_file_name)
		if (exists == True):
			logger.debug('FILE EXISTS ON GOOGLE DRIVE')
			logger.debug('id: %s', id)
			#logger.debug('filecontent: %s', filecontent)

			fo = open(destination_path + gdrive_file_name, "wb")
			fo.write(filecontent)
			fo.close()

			if (remove_after_download == "True"):
				logger.debug('Removing file')
				logger.debug('FileId of file to remove: %s', id)
				try:
					service.files().delete(fileId=id).execute()
				except errors.HttpError, error:
					print 'An error occurred: %s' % error
		else:
			logger.debug('FILE DOES NOT EXIST ON GOOGLE DRIVE')

#Added this line to get rid of the following message:
#No handlers could be found for logger "oauth2client.util"
#logging.basicConfig(filename=log_file,level=logging.DEBUG)

storage = Storage("/home/pi/RPiWebCam/saved_user_creds.dat")
credentials = storage.get()

OAUTH_SCOPE = 'https://www.googleapis.com/auth/drive'

argparser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[tools.argparser])

argparser.add_argument('path', metavar='N', type=str, nargs='+', help='file path')

flags = argparser.parse_args(sys.argv[1:])

logger.debug('Parameters: %s', str(sys.argv))
logger.debug('Flags: %s', flags)
logger.debug('Source: %s', str(flags.path))

gdrive_path = sys.argv[2]
gdrive_file_name = sys.argv[3]
destination_path = sys.argv[4]
remove_after_download = sys.argv[5]
application_folder = "RPiWebCam"

logger.debug('gdrive_path: %s', gdrive_path)
logger.debug('gdrive_file_name: %s', gdrive_file_name)
logger.debug('destination_path: %s', destination_path)
logger.debug('remove_after_download: %s', remove_after_download)

gdrive_path_folders = gdrive_path.strip("/").split("/")

if credentials is None or credentials.invalid:
 	#credentials = run(flow_from_clientsecrets("client_secrets.json", scope=[OAUTH_SCOPE]), storage, flags)
 	credentials = tools.run_flow(flow_from_clientsecrets("/home/pi/RPiWebCam/client_secrets.json", scope=["https://www.googleapis.com/auth/drive"]), storage, flags)
http = credentials.authorize(httplib2.Http())
drive_service = build('drive', 'v2', http=http)
#print service.files().list().execute()


parent_id = get_parent_id_of_gdrive_folder(drive_service, application_folder, gdrive_path_folders)

download_file(drive_service, gdrive_file_name, parent_id, destination_path, remove_after_download)

#result = upload_file(drive_service, source_path, source_file_name, gdrive_file_name, gdrive_file_description, parent_id, new_file_revision)

#logger.debug(result)
#logger.debug('parent_id: %s', parent_id)
