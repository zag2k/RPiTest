#!/usr/bin/env python

# To be used with WebIOPi <https://code.google.com/p/webiopi/>

import webiopi
import psutil
import os
import json
from threading import Timer
import datetime
import time
from time import strftime
import subprocess
from time import sleep

from webiopi.utils.version import PYTHON_MAJOR

if PYTHON_MAJOR >= 3:
    import configparser as parser
else:
    import ConfigParser as parser

#import sys
#sys.path.append("/home/pi/RPiWebCam/")
#import cam
#import upload

#filename = "/home/pi/RPiWebCam/cam.py"
#directory, module_name = os.path.split(filename)
#module_name = os.path.splitext(module_name)[0]
#path = list(sys.path)
#sys.path.insert(0, directory)
#try:
#    module = __import__(module_name)
#finally:
#    sys.path[:] = path # restore

import sys
sys.path.append("/home/pi/RPiWebCam/Firmware")
import cam
import upload

import logging
from logging.handlers import RotatingFileHandler

configParser = parser.RawConfigParser()   
configFilePath = '/home/pi/RPiWebCam/Firmware/config.txt'
configParser.read(configFilePath)
application_folder = configParser.get('camera', 'application_folder')
camera_location = configParser.get('camera', 'location')
camera_name = configParser.get('camera', 'camera_name')
vflip = configParser.getboolean('camera', 'default_vflip')
hflip = configParser.getboolean('camera', 'default_hflip')
logs_path = configParser.get('camera', 'logs_path')

# Logging
log_file = logs_path + camera_name + '.log'
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(log_file, maxBytes=50000, backupCount=2)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - raspberrypi.py - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.addHandler(logging.StreamHandler())

GPIO = webiopi.GPIO

# setup function is automatically called at WebIOPi startup
def setup():
    # Do nothing
    pass

# loop function is repeatedly called by WebIOPi
def loop():
    # Do Nothing
    # Sleep for 1/10th second. Otherwise WebIOPi uses 100% of the CPU
    sleep(0.1)
    pass

# destroy function is called at WebIOPi shutdown
def destroy():
    # do nothing
    pass

@webiopi.macro
def reboot(t=1):
    Timer(int(t)*60,os.system("sudo reboot")).start()
    return "The system is going DOWN for reboot in %d minute" % t

@webiopi.macro
def getData():
    temp =  round(int(open('/sys/class/thermal/thermal_zone0/temp').read()) / 1e3,1)
    perc = psutil.cpu_percent()
    memAvail = round(psutil.avail_phymem()/1000000,1)
    diskUsage =  psutil.disk_usage('/').percent
    j = {'cpu_temp': temp, 'cpu_perc': perc, 'mem_avail': memAvail, 'disk_usage': diskUsage}
    return json.dumps(j,indent=4, separators=(',', ': '))
    #j = {'cpu_temp': temp}
    #return json.dumps(j,indent=4, separators=(',', ': '))

@webiopi.macro
def takePic(ss=0, w=1920, h=1080):

    logger.debug('takePic Called')

    shutter = int(ss)*1000000
    res_w = int(w)
    res_h = int(h)

    logger.debug('Parameters - shutter: %s; w: %s; h: %s', shutter, w, h)

    #ts = datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")

    #cmd = 'raspistill -w {0} -h {1} -ex auto -o /home/pi/RPiWebCam/InstaPic/{2}.jpg'.format(w, h, ts)

    if ss == 0:
        #command1 = "raspistill -w " + str(w) + " -h " + str(h) + " -ex auto -o /home/pi/RPiWebCam/InstaPic/" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + ".jpg"
        #p1 = subprocess.Popen(command1, stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
        #command2 = "/home/pi/RPiWebCam/instapic-upload.py"
        #p2 = subprocess.Popen(command2, stdout=subprocess.PIPE, shell=False, preexec_fn=os.setsid)
        #p1.wait()
        #p2.wait()
        filename = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        logger.debug('filename: %s', filename)
        #os.system("raspistill -w " + str(w) + " -h " + str(h) + " -ex auto -vf -hf -o /home/pi/RPiWebCam/InstaPic/" + filename + ".jpg")
        
        res = cam.take(vflip=vflip, hflip=hflip, resolution_w=res_w, resolution_h=res_h, exposure_compensation=0, shutter_speed=shutter, exposure_mode="auto", iso=100, file_name="/home/pi/" + application_folder + "/SmartThings/" + filename + ".jpg")
        upload.upload_files_in_folder("/home/pi/RPiWebCam/SmartThings/", "/" + camera_location + "/" + camera_name + "/SmartThings/" + datetime.date.today().strftime("%Y-%m-%d") + "/", file_description="SmartThings Image", new_file_revision=False, delete_after_upload=True, notify=True)
        
        #sleep(5)
        #os.system("/home/pi/RPiWebCam/instapic-upload.py")
    else:
        #command1 = "raspistill -w " + str(w) + " -h " + str(h) + " -ex auto -ss " + str(shutter) + " -o /home/pi/RPiWebCam/InstaPic/" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + ".jpg"
        #p1 = subprocess.Popen(command1, stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
        #command2 = "/home/pi/RPiWebCam/instapic-upload.py"
        #p2 = subprocess.Popen(command2, stdout=subprocess.PIPE, shell=False, preexec_fn=os.setsid)
        #p1.wait()
        
        #p2.wait()
        #command = "raspistill -w " + str(w) + " -h " + str(h) + " -ex auto -o /home/pi/RPiWebCam/InstaPic/" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + ".jpg"
        #subprocess.Popen(command).wait()
        #command = "/home/pi/RPiWebCam/instapic-upload.py"
        #subprocess.Popen(command).wait()
        filename = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        logger.debug('filename: %s', filename)
        #os.system("raspistill -w " + str(w) + " -h " + str(h) + " -ex auto -ss " + str(shutter) + " -vf -hf -o /home/pi/RPiWebCam/InstaPic/" + filename + ".jpg")
        
        res = cam.take(vflip=vflip, hflip=hflip, resolution_w=res_w, resolution_h=res_h, exposure_compensation=0, shutter_speed=shutter, exposure_mode="auto", iso=100, file_name="/home/pi/" + application_folder + "/SmartThings/" + filename + ".jpg")
        upload.upload_files_in_folder("/home/pi/RPiWebCam/SmartThings/", "/" + camera_location + "/" + camera_name + "/SmartThings/" + datetime.date.today().strftime("%Y-%m-%d") + "/", file_description="SmartThings Image", new_file_revision=False, delete_after_upload=True, notify=True)
        
        #sleep(20)
        #os.system("/home/pi/RPiWebCam/instapic-upload.py")
    
    logger.removeHandler(handler)

    j = {'result': 'pic taken'}
    return json.dumps(j,indent=4, separators=(',', ': '))


@webiopi.macro
def takePicOverlay(ss=0, w=1920, h=1080):

    logger.debug('takePicOverlay Called')

    shutter = int(ss)*1000000
    res_w = int(w)
    res_h = int(h)

    logger.debug('Parameters - shutter: %s; w: %s; h: %s', shutter, w, h)

    #ts = datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")

    #cmd = 'raspistill -w {0} -h {1} -ex auto -o /home/pi/RPiWebCam/InstaPic/{2}.jpg'.format(w, h, ts)

    if ss == 0:
        #command1 = "raspistill -w " + str(w) + " -h " + str(h) + " -ex auto -o /home/pi/RPiWebCam/InstaPic/" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + ".jpg"
        #p1 = subprocess.Popen(command1, stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
        #command2 = "/home/pi/RPiWebCam/instapic-upload.py"
        #p2 = subprocess.Popen(command2, stdout=subprocess.PIPE, shell=False, preexec_fn=os.setsid)
        #p1.wait()
        #p2.wait()
        #filename = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        #os.system("raspistill -w " + str(w) + " -h " + str(h) + " -ex auto -vf -hf -o /home/pi/RPiWebCam/InstaPic/" + filename + ".jpg")
        filename = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        logger.debug('filename: %s', filename)
        res = cam.take(vflip=vflip, hflip=hflip, resolution_w=res_w, resolution_h=res_h, exposure_compensation=0, shutter_speed=shutter, exposure_mode="auto", iso=100, file_name="/home/pi/" + application_folder + "/SmartThings/" + filename + ".jpg")

        sleep(2)
        os.system("convert /home/pi/RPiWebCam/SmartThings/" + filename + ".jpg -pointsize 36 -fill white -annotate +40+1040 '" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M") + "' /home/pi/RPiWebCam/SmartThings/" + filename + "-dt.jpg")

        upload.upload_files_in_folder("/home/pi/RPiWebCam/SmartThings/", "/" + camera_location + "/" + camera_name + "/SmartThings/" + datetime.date.today().strftime("%Y-%m-%d") + "/", file_description="SmartThings Image", new_file_revision=False, delete_after_upload=True, notify=True)
        
        #sleep(5)
        #os.system("/home/pi/RPiWebCam/instapic-upload.py")
    else:
        #command1 = "raspistill -w " + str(w) + " -h " + str(h) + " -ex auto -ss " + str(shutter) + " -o /home/pi/RPiWebCam/InstaPic/" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + ".jpg"
        #p1 = subprocess.Popen(command1, stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
        #command2 = "/home/pi/RPiWebCam/instapic-upload.py"
        #p2 = subprocess.Popen(command2, stdout=subprocess.PIPE, shell=False, preexec_fn=os.setsid)
        #p1.wait()
        
        #p2.wait()
        #command = "raspistill -w " + str(w) + " -h " + str(h) + " -ex auto -o /home/pi/RPiWebCam/InstaPic/" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + ".jpg"
        #subprocess.Popen(command).wait()
        #command = "/home/pi/RPiWebCam/instapic-upload.py"
        #subprocess.Popen(command).wait()
        #filename = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        #os.system("raspistill -w " + str(w) + " -h " + str(h) + " -ex auto -ss " + str(shutter) + " -vf -hf -o /home/pi/RPiWebCam/InstaPic/" + filename + ".jpg")
        #sleep(2)
        #os.system("/usr/bin/convert /home/pi/RPiWebCam/InstaPic/" + filename + ".jpg -pointsize 36 -fill white -annotate +40+1040 '" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M") + "' /home/pi/RPiWebCam/InstaPic/" + filename + "-dt.jpg")
        filename = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        logger.debug('filename: %s', filename)
        res = cam.take(vflip=vflip, hflip=hflip, resolution_w=res_w, resolution_h=res_h, exposure_compensation=0, shutter_speed=shutter, exposure_mode="auto", iso=100, file_name="/home/pi/" + application_folder + "/SmartThings/" + filename + ".jpg")

        sleep(2)
        os.system("convert /home/pi/RPiWebCam/SmartThings/" + filename + ".jpg -pointsize 36 -fill white -annotate +40+1040 '" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M") + "' /home/pi/RPiWebCam/SmartThings/" + filename + "-dt.jpg")

        upload.upload_files_in_folder("/home/pi/RPiWebCam/SmartThings/", "/" + camera_location + "/" + camera_name + "/SmartThings/" + datetime.date.today().strftime("%Y-%m-%d") + "/", file_description="SmartThings Image", new_file_revision=False, delete_after_upload=True, notify=True)
        
        #sleep(20)
        #os.system("/home/pi/RPiWebCam/instapic-upload.py")

    logger.removeHandler(handler)
    
    return "Photo taken"

@webiopi.macro
def takeBurst(ss=0, w=1920, h=1080):

    logger.debug('takeBurst Called')

    shutter = int(ss)*1000000
    res_w = int(w)
    res_h = int(h)

    logger.debug('Parameters - shutter: %s; w: %s; h: %s', shutter, w, h)

    res = cam.take(vflip=vflip, hflip=hflip, resolution_w=res_w, resolution_h=res_h, exposure_compensation=0, shutter_speed=shutter, exposure_mode="auto", iso=100, file_name="/home/pi/" + application_folder + "/SmartThings/" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + ".jpg")
    res = cam.take(vflip=vflip, hflip=hflip, resolution_w=res_w, resolution_h=res_h, exposure_compensation=0, shutter_speed=shutter, exposure_mode="auto", iso=100, file_name="/home/pi/" + application_folder + "/SmartThings/" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + ".jpg")
    res = cam.take(vflip=vflip, hflip=hflip, resolution_w=res_w, resolution_h=res_h, exposure_compensation=0, shutter_speed=shutter, exposure_mode="auto", iso=100, file_name="/home/pi/" + application_folder + "/SmartThings/" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + ".jpg")

    upload.upload_files_in_folder("/home/pi/RPiWebCam/SmartThings/", "/" + camera_location + "/" + camera_name + "/SmartThings/" + datetime.date.today().strftime("%Y-%m-%d") + "/", file_description="SmartThings Image", new_file_revision=False, delete_after_upload=True, notify=False)
    
    logger.removeHandler(handler)
    
    return "Burst taken"

@webiopi.macro
def takeVid(l=6, w=1920, h=1080):
    logger.debug('takeVid Called')

    res_w = int(w)
    res_h = int(h)
    length = int(l)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

    res = cam.takeVid(True, True, res_w, res_h, 0, length, "auto", 800, "/home/pi/RPiWebCam/SmartThings/" + timestamp + ".h264")

    logger.debug('takeVid Returned')

    #sleep(15)
    logger.debug('takeVid Upload called')
    upload.upload_files_in_folder("/home/pi/RPiWebCam/SmartThings/", "/" + camera_location + "/" + camera_name + "/SmartThings/" + datetime.date.today().strftime("%Y-%m-%d") + "/", file_description="SmartThings Video", new_file_revision=False, delete_after_upload=True, notify=True)
    logger.debug('takeVid Upload done')

    logger.removeHandler(handler)

    return "Video taken"
