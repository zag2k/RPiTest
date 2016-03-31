#!/usr/bin/env python

import subprocess
#import smtplib
#import socket
#from email.mime.text import MIMEText
import datetime
import os
from time import sleep
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
log_file = logs_path + camera_name + '-SysInfo.log'
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(log_file, maxBytes=50000, backupCount=2)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - system-info.py - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.addHandler(logging.StreamHandler())

# Change to your own account information
#to = 'me@example.com'
#gmail_user = 'test@gmail.com'
#gmail_password = 'yourpassword'
#smtpserver = smtplib.SMTP('smtp.gmail.com', 587)
#smtpserver.ehlo()
#smtpserver.starttls()
#smtpserver.ehlo
#smtpserver.login(gmail_user, gmail_password)
#today = datetime.date.today()
# Very Linux Specific


def get_up_stats():
    try:
        s=subprocess.check_output(["uptime"])
        #load_split = s.split('load average: ')
        #load_five = float(load_split[1].split(',')[1])
        #up = load_split[0]
        #up_pos = up.rfind(',',0,len(up)-4)
        #up = up[:up_pos].split('up ')[1]
        return (s.split('\n')) 
    except:
        return ( "" )

def get_ram():
    #Returns a tuple (total ram, available ram) in megabytes. See www.linuxatemyram.com
    try:
        s = subprocess.check_output(["free","-m"])
        lines = s.split('\n')       
        return ( int(lines[1].split()[1]), int(lines[2].split()[3]) )
    except:
        return 0

arg='ip route list'
p=subprocess.Popen(arg,shell=True,stdout=subprocess.PIPE)
data = p.communicate()
split_data = data[0].split()
ipaddr = split_data[split_data.index('src')+1]
#my_ip = 'Your ip is %s' %  ipaddr
#print my_ip

datestr = datetime.date.today().strftime("%Y-%m-%d")

#fo = open("/home/pi/RPiWebCam/SystemInfo-" + datestr + ".txt", "w")
#fo = open("/home/pi/RPiWebCam/IPAddress.txt", "a")
#print "Name of the file: ", fo.name

df = subprocess.Popen(["df"], stdout=subprocess.PIPE)
output = df.communicate()[0]
#device, size, used, available, percent, mountpoint = \
#    output.split("\n")[1].split()

#fo.write( datestr + "\n\n" )

#fo.write( ipaddr + "\n\n" )

#fo.write( output + "\n" )

#fo.close()

logger.info('IP Address: %s', ipaddr)

#temp = subprocess.Popen(["vcgencmd measure_temp"], stdout=subprocess.PIPE)
temp = subprocess.check_output(["/opt/vc/bin/vcgencmd","measure_temp"]).split('=')[1][:-3]
#temp_output = temp.communicate()[0]

logger.info("CPU Core Temperature: %s'C", temp)

logger.info('Up Time: %s', get_up_stats())

logger.info('Free RAM: %s', str(get_ram()[1]) + " (" + str(get_ram()[0]) + " total)")

logger.info('Disk Filesystem (df):\n%s\n', output)

#cmd = "/home/pi/RPiWebCam/dropbox_uploader.sh upload /home/pi/RPiWebCam/" + camera_name + "-SysInfo.log /" + camera_name + "/Logs/" + camera_name + "-SysInfo.log.txt"
#os.system(cmd)
#cmd = 'python /home/pi/RPiWebCam/gdrive_uploader.py "--noauth_local_webserver" /home/pi/RPiWebCam/ "' + camera_name + '-SysInfo.log" "/' + location + '/' + camera_name + '/Logs/" "' + camera_name + '-SysInfo.log" False False'
#os.system(cmd)

upload.upload_file(logs_path, camera_name + "-SysInfo.log", "/" + camera_location + "/" + camera_name + "/Logs/", camera_name + "-SysInfo.log", file_description="Log File", new_file_revision=False, delete_after_upload=False, notify=False)

#Upload script log also
#cmd = "/home/pi/RPiWebCam/dropbox_uploader.sh upload /home/pi/RPiWebCam/" + camera_name + ".log /" + camera_name + "/Logs/" + camera_name + "-Scripts.log.txt"
#os.system(cmd)
#cmd = 'python /home/pi/RPiWebCam/gdrive_uploader.py "--noauth_local_webserver" /home/pi/RPiWebCam/ "' + camera_name + '.log" "/' + location + '/' + camera_name + '/Logs/" "' + camera_name + '.log" False False'
#os.system(cmd)

upload.upload_file(logs_path, camera_name + ".log", "/" + camera_location + "/" + camera_name + "/Logs/", camera_name + ".log", file_description="Log File", new_file_revision=False, delete_after_upload=False, notify=False)

#sleep(5)

#os.system("rm /home/pi/RPiWebCam/SystemInfo-" + datestr + ".txt")

#msg = MIMEText(my_ip)
#msg['Subject'] = 'IP For RaspberryPi on %s' % today.strftime('%b %d %Y')
#msg['From'] = gmail_user
#msg['To'] = to
#smtpserver.sendmail(gmail_user, [to], msg.as_string())
#smtpserver.quit()

logger.removeHandler(handler)