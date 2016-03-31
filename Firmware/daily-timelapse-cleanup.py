#!/usr/bin/python

#print "Starting"

import os

path="/home/pi/RPiWebCam/DailyTimeLapse/"

def cleanup_files():
	if not os.path.exists(path):
		return
	dir_list = os.listdir(path)
	for file_name in dir_list:
		os.remove(path + file_name)

if __name__ == "__main__":
	cleanup_files()
