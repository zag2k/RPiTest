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

import argparse
from oauth2client import tools

import logging
from logging.handlers import RotatingFileHandler
import ConfigParser

import json

import httplib
import urllib

configParser = ConfigParser.RawConfigParser()   
configFilePath = '/home/pi/RPiWebCam/Firmware/config.txt'
configParser.read(configFilePath)
camera_location = configParser.get('camera', 'location')
application_folder = configParser.get('camera', 'application_folder')
camera_name = configParser.get('camera', 'camera_name')
logs_path = configParser.get('camera', 'logs_path')
pushover_notifications = configParser.getboolean('camera', 'pushover_notifications')

# Logging
log_file = logs_path + camera_name + '.log'
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler(log_file, maxBytes=50000, backupCount=2)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - gdrive_uploader.py - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.addHandler(logging.StreamHandler())

#CALL: python gdrive_uploader.py --noauth_local_webserver /home/pi/RPiWebCam/Test/ test.jpg /Lake/Daily/2015-04-16/ test.jpg False

#RpiWebCam/Lake/Daily/2015-04-15
#RpiWebCam/Lake/Daily/DailyTimeLapse

def get_parent_id_of_dest_folder(service, application_folder, folders):
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
		folder_link = ""

		if len(file_items) == 1:
			#logger.debug('title: %s', file_items[0]['title'])
			#logger.debug('mimeType: %s', file_items[0]['mimeType'])
			#logger.debug('id: %s', file_items[0]['id'])
			pid = file_items[0]['id']
			logger.debug('ID for %s: %s', folder, pid)
			parent_id = pid

			logger.debug(file_items[0]["alternateLink"])
			folder_link = file_items[0]["alternateLink"]

		else:
			logger.debug('Did not find folder: %s', folder)
			logger.debug('Creating folder: %s', folder)
 			#create folder if it doesn't exist
			body = {
				"title": folder,
				"mimeType": "application/vnd.google-apps.folder",
				"parents": [{
					"id": parent_id
					}]
				}

			file = service.files().insert(body=body).execute()
			logger.debug('ID of new folder: %s', file['id'])
			pid = file['id']
			parent_id = pid
			folder_link = file["alternateLink"]

	return pid, folder, folder_link



def file_exists_in_folder(service, parent_id, title):
	result = False
	files = []
	param = {}
	id = ""

	logger.debug('parent_id: %s', parent_id)
	logger.debug('title: %s', title)

	q = "title = '" + title + "' and '" + parent_id + "' in parents and trashed = false"
	param['q'] = q
	file_items = service.files().list(**param).execute().get('items', [])

	if len(file_items) > 0:
		result = True
		id = file_items[0]['id']

	return result, id

def upload_file(service, source_path, source_file_name, gdrive_file_name, gdrive_file_description, parent_id, new_revision=False):
	file = ""
	result = False
	logger.debug('new_revision: %s', new_revision)

	if new_revision == 'True':
		nr = True
	else:
		nr = False

	if parent_id != "0":
		exists, id = file_exists_in_folder(service, parent_id, gdrive_file_name)
		if (exists == True):
			logger.debug('FILE EXISTS')
			logger.debug('id: %s', id)

			file = service.files().get(fileId=id).execute()

			# File's new content.
			mime_type=""

			if ".avi" in source_file_name:
				mime_type="video/x-msvideo"
			elif ".jpeg" in source_file_name:
				mime_type="image/jpeg"
			elif ".jpg" in source_file_name:
				mime_type="image/jpeg"
			elif ".log" in source_file_name:
				mime_type="text/plain"
			elif ".txt" in source_file_name:
				mime_type="text/plain"
			elif ".mp4" in source_file_name:
				mime_type="video/mp4"
			else: 
				mime_type=""

			if ".avi" in source_file_name:
				#delete previous and upload as new file
				service.files().delete(fileId=id).execute()

				media_body = MediaFileUpload(source_path + source_file_name, mimetype=mime_type, resumable=True)
				body = {
					"title": gdrive_file_name,
					"description": gdrive_file_description,
					"mimeType": mime_type,
					"parents": [{
						"kind": "drive#fileLink",
						"id": parent_id
					}]
				}
				
				file = drive_service.files().insert(body=body, media_body=media_body).execute()
			else:
	
				media_body = MediaFileUpload(source_path + source_file_name, mimetype=mime_type, resumable=True)

				logger.debug('mime_type: %s', mime_type)

				# Send the request to the API.
				file = service.files().update(fileId=id, body=file, newRevision=nr, media_body=media_body).execute()

			result = True
		else:
			logger.debug('FILE DOES NOT EXIST')
			logger.debug('Uploading File')
			# Insert a file
			
			#if ".log" in source_file_name:
			#	media_body = MediaFileUpload(source_path + source_file_name, mimetype="text/plain", resumable=True)
			#else:
			#	media_body = MediaFileUpload(source_path + source_file_name, resumable=True)

			mime_type=""

			if ".avi" in source_file_name:
				mime_type="video/x-msvideo"
			elif ".jpeg" in source_file_name:
				mime_type="image/jpeg"
			elif ".jpg" in source_file_name:
				mime_type="image/jpeg"
			elif ".log" in source_file_name:
				mime_type="text/plain"
			elif ".txt" in source_file_name:
				mime_type="text/plain"
			elif ".mp4" in source_file_name:
				mime_type="video/mp4"
			else: 
				mime_type=""
	
			media_body = MediaFileUpload(source_path + source_file_name, mimetype=mime_type, resumable=True)
			body = {
				"title": gdrive_file_name,
				"description": gdrive_file_description,
				"mimeType": mime_type,
				"parents": [{
					"kind": "drive#fileLink",
					"id": parent_id
				}]
			}

			logger.debug('mime_type: %s', mime_type)

			file = service.files().insert(body=body, media_body=media_body).execute()

			result = True

		#logger.debug('file: %s', file["alternateLink"])
		#pprint.pprint(file)
	return result, file

#Added this line to get rid of the following message:
#No handlers could be found for logger "oauth2client.util"
#logging.basicConfig(filename=log_file,level=logging.DEBUG)

def gdrive_upload(source_path, source_file_name, gdrive_path, gdrive_file_name, file_description, new_file_revision=False, notify=False):
	result = False
	storage = Storage("/home/pi/RPiWebCam/saved_user_creds.dat")
	credentials = storage.get()

	OAUTH_SCOPE = 'https://www.googleapis.com/auth/drive'

	#argparser = argparse.ArgumentParser(
	#    description=__doc__,
	#    formatter_class=argparse.RawDescriptionHelpFormatter,
	#    parents=[tools.argparser])

	#argparser.add_argument('path', metavar='N', type=str, nargs='+', help='file path')

	#flags = argparser.parse_args(sys.argv[1:])

	#logger.debug('Parameters: %s', str(sys.argv))
	#logger.debug('Flags: %s', flags)
	#logger.debug('Source: %s', str(flags.path))

	#source_path = sys.argv[2]
	#source_file_name = sys.argv[3]
	#gdrive_path = sys.argv[4]
	#gdrive_file_name = sys.argv[5]
	#new_file_revision = sys.argv[6]
	#notify = sys.argv[7]
	#gdrive_file_description = "RPiWebCam Image"
	#application_folder = "RPiWebCam"

	logger.debug('source_path: %s', source_path)
	logger.debug('source_file_name: %s', source_file_name)
	logger.debug('gdrive_path: %s', gdrive_path)
	logger.debug('gdrive_file_name: %s', gdrive_file_name)
	logger.debug('file_description: %s', file_description)
	logger.debug('new_file_revision: %s', new_file_revision)
	logger.debug('notify: %s', notify)

	gdrive_path_folders = gdrive_path.strip("/").split("/")

	try:	
		if credentials is None or credentials.invalid:
		 	#credentials = run(flow_from_clientsecrets("client_secrets.json", scope=[OAUTH_SCOPE]), storage, flags)
		 	credentials = tools.run_flow(flow_from_clientsecrets("/home/pi/RPiWebCam/client_secrets.json", scope=["https://www.googleapis.com/auth/drive"]), storage, flags)
		http = credentials.authorize(httplib2.Http())
		drive_service = build('drive', 'v2', http=http)
		#print service.files().list().execute()


		parent_id, folder_name, folder_link = get_parent_id_of_dest_folder(drive_service, application_folder, gdrive_path_folders)

		logger.debug('folder_name: %s', folder_name)
		logger.debug('folder_link: %s', folder_link)

		success, res = upload_file(drive_service, source_path, source_file_name, gdrive_file_name, application_folder + " " + file_description, parent_id, new_file_revision)

		if success:
			#logger.debug('file alternateLink: ', result["alternateLink"])
			result = True

			if notify == True and pushover_notifications == True:
				logger.debug("send notification")
				conn = httplib.HTTPSConnection("api.pushover.net:443")
				logger.debug("created connection")
				conn.request("POST", "/1/messages.json",
					urllib.urlencode({
						"token": "a6Eaohfy4mbSBQoyH7uUY3N5MTtRhA",
						"user": "uRLHufGx9JjiDxRbgsXEsSe7esGwP8",
						"title": camera_location.upper() + " | " + camera_name,
						"message": "<a href='googledrive://" + res["alternateLink"] + "'>" + res["title"] + "</a> in <a href='googledrive://" + folder_link + "'>" + folder_name + "</a>",
						#"url": "googledrive://" + result["alternateLink"],
						"html": 1,
					}), { "Content-type": "application/x-www-form-urlencoded" })
				logger.debug("before getresponse")
				conn.getresponse()

	except:
		logger.debug("something went wrong with upload")
		result = False

	return result

#logger.debug(result)
#logger.debug('parent_id: %s', parent_id)


if __name__ == '__main__':
	res = gdrive_upload("/home/pi/RPiWebCam/", "test.jpg", "/" + camera_location + "/" + camera_name + "/Test/", "test.jpg", "Test Image", False, True)

	if res == True:
		logger.debug("Success!")