import sys
import json
import os
from pushbullet import PushBullet
from requests.exceptions import HTTPError

if __name__ == '__main__':
	p = PushBullet("L0Wtxg0coFfVW4majBbORq3sS3xkQmTF")

	devices = p.getDevices()

	# Get a list of contacts
	contacts = p.getContacts()

	# Send a note
	#p.pushNote(devices[0]["iden"], 'Hello world', 'Test body')

	p.pushFile(devices[0]["iden"], "take-photo-test5.jpg", "This is a test file", open("/home/pi/RPiWebCam/Test/take-photo-test5.jpg", "rb"))

    #note = p.pushNote(args.device, args.title, " ".join(args.body))
    #if args.json:
    #    print(json.dumps(note))
    #    return
    #if args.device and args.device[0] == '#':
    #    print("Note broadcast to channel %s" % (args.device))
    #elif not args.device:
    #    print("Note %s sent to all devices" % (note["iden"]))
    #else:
    #    print("Note %s sent to %s" % (note["iden"], note["target_device_iden"]))