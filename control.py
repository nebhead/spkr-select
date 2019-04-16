# *****************************************
# Speaker Selector Control Python script
# *****************************************
#
# Description: This script will read the states.dat file and set relays/LEDs
# upon any changes to that file.  This script also accepts input from the IR
# sensor and will write the states.dat file and set the relays appropriately.
#
# This script runs as a separate process from the Flask / Gunicorn
# implementation which handles the web interface.
#
# *****************************************

import time
import RPi.GPIO as GPIO
import os
import pickle

LIRC_Enabled = False # Set to True to enable Lirc / Remote Control Functions and False to disable

if (LIRC_Enabled == True):
	import lirc
	sockidc = lirc.init("control", "/home/pi/spkr-select/.lircrc", blocking=False)

# Init GPIO's to default values / behavior
GPIO.setmode(GPIO.BCM)

GPIO.setup(17, GPIO.OUT) # LED 01 - Speakers 1
GPIO.setup(18, GPIO.OUT) # LED 02 - Speakers 2
GPIO.setup(19, GPIO.OUT) # LED 03 - Speakers 3
#GPIO.setup(20, GPIO.OUT) # LED 04 - Not used / connected currently
GPIO.setup(21, GPIO.OUT) # LED 05 - Protection

GPIO.setup(22, GPIO.OUT, initial=0) # Relays (1 & 2) - Speakers 1 (L/R)
GPIO.setup(23, GPIO.OUT, initial=1) # Relays (3 & 4) - Speakers 2 (L/R)
GPIO.setup(24, GPIO.OUT, initial=1) # Relays (5 & 6) - Speakers 3 (L/R)
GPIO.setup(25, GPIO.OUT, initial=1) # Relays (7 & 8) - Protection (L/R)

# Init Global Variable for Speaker Switch States
spkr_state = ['on', 'off', 'off', 'off', 'off']

def SetRelays(spkr_state):
	# *****************************************
	# Function to set relays (and set LEDs if applicable)
	# *****************************************

	if spkr_state[0] == 'on':
		GPIO.output(22, 1) 	#Turn on Relay (0 = On) - Channel 1 Reverse Logic
		GPIO.output(17, 1)  #Turn on LED (1 = On)
	else:
		GPIO.output(22, 0) 	#Turn off Relay (1 = Off) - Channel 1 Reverse Logic
		GPIO.output(17, 0)  #Turn off LED (0 = Off)

	if spkr_state[1] == 'on':
		GPIO.output(23, 0) 	#Turn on Relay (0 = On)
		GPIO.output(18, 1)  #Turn on LED (1 = On)
	else:
		GPIO.output(23, 1) 	#Turn off Relay (1 = Off)
		GPIO.output(18, 0)  #Turn off LED (0 = Off)

	if spkr_state[2] == 'on':
		GPIO.output(24, 0) 	#Turn on Relay (0 = On)
		GPIO.output(19, 1)  #Turn on LED (1 = On)
	else:
		GPIO.output(24, 1) 	#Turn off Relay (1 = Off)
		GPIO.output(19, 0)  #Turn off LED (0 = Off)

	# spkr_state[3] unconnected and disabled
	#if spkr_state[3] == 'on':
		#GPIO.output(xx, 0)  #Turn on Relay (0 = On)
		#GPIO.output(20, 1)  #Turn on LED (1 = On)
	#else:
		#GPIO.output(xx, 1)  #Turn off Relay (1 = On)
		#GPIO.output(20, 0)  #Turn off LED (0 = Off)

	if spkr_state[4] == 'on':
		GPIO.output(25, 0) 	#Turn on Relay, turn on protection - Reverse logic for Protection Relay
		GPIO.output(21, 1)  #Turn on LED (1 = On)
	else:
		GPIO.output(25, 1) 	#Turn on Relay, turn off protection - Reverse logic for Protection Relay
		GPIO.output(21, 0)  #Turn off LED (0 = Off)

def ReadSpkrState():
	# *****************************************
	# Read Speaker State Values from File
	# *****************************************

    # Start with an empty spkr_state list
	spkr_state = []

	# Read all lines of state.dat into an list(array)
	try:
		with open('state.dat', 'rb') as states:
			spkr_state = pickle.load(states)
			states.close()
	# If file not found error, then create state.dat file
	except(IOError, OSError):
		spkr_state = ['on', 'off', 'off', 'off', 'off']
		WriteSpkrState(spkr_state)

	return(spkr_state)

def WriteSpkrState(spkr_state):
	# *****************************************
	# Write Speaker State Values to File
	# *****************************************
	with open('state.dat', 'wb') as states:
		pickle.dump(spkr_state, states, protocol=2)
		states.close()

def CheckRemoteInput(spkr_state):
	# *****************************************
	# Check for input from remote control
	# *****************************************
	button = lirc.nextcode()

	if button:
		if button[0] == 'KEY_1':
			if(spkr_state[0] == 'on'):
				spkr_state[0] = 'off'
			else:
				spkr_state[0] = 'on'
		if button[0] == 'KEY_2':
			if(spkr_state[1] == 'on'):
				spkr_state[1] = 'off'
			else:
				spkr_state[1] = 'on'
		if button[0] == 'KEY_3':
			if(spkr_state[2] == 'on'):
				spkr_state[2] = 'off'
			else:
				spkr_state[2] = 'on'
		if button[0] == 'KEY_4':
			spkr_state = ['on', 'off', 'off', 'off', 'off']
		if button[0] == 'KEY_POWER':
			spkr_state = ['on', 'on', 'on', 'off', 'on']
	# Check if more than one speaker is enabled, then enable protection
		spkr_count = 0
		for x in range(4):
			if spkr_state[x] == 'on':
				spkr_count = spkr_count + 1
		if (spkr_count > 1):
			spkr_state[4] = 'on'
		else:
			spkr_state[4] = 'off'

		WriteSpkrState(spkr_state)
		SetRelays(spkr_state)

# *****************************************
# Main Program Start / Init
# *****************************************

spkr_state = ReadSpkrState()
SetRelays(spkr_state)

# *****************************************
# Main Program Loop
# *****************************************

while True:
	if (spkr_state != ReadSpkrState()):
		spkr_state = ReadSpkrState()
		SetRelays(spkr_state)
	elif (LIRC_Enabled == True):
		CheckRemoteInput(spkr_state)
	time.sleep(0.25)

if (LIRC_Enabled == True):
	lirc.deinit()

GPIO.cleanup()
exit()
