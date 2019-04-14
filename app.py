
# Speaker Selector Flask/Python script

from flask import Flask, request, render_template, make_response
import time
import os
import pickle
import json
import datetime

app = Flask(__name__)

@app.route('/', methods=['POST','GET'])
def index():

	spkr_state = ReadSpkrState()
	spkr_count = 0
	error = False
	# If posting, process input from POST
	if request.method == 'POST':
		response = request.form

		if('spkrs_01' in response):
			spkr_state[0] = request.form['spkrs_01']
		if('spkrs_02' in response):
			spkr_state[1] = request.form['spkrs_02']
		if('spkrs_03' in response):
			spkr_state[2] = request.form['spkrs_03']
		if('spkrs_04' in response):
			spkr_state[3] = request.form['spkrs_04']

		# Count number of speakers selected, turn on protection if > 1
		for x in range(4):
			if spkr_state[x] == 'on':
				spkr_count = spkr_count + 1
		if (spkr_count > 1):
			spkr_state[4] = 'on'
		else:
			spkr_state[4] = 'off'

		WriteSpkrState(spkr_state)

	return render_template('index.html', spkr_state=spkr_state, error=error)


@app.route('/admin/<action>', methods=['POST','GET'])
@app.route('/admin', methods=['POST','GET'])
def admin(action=None):
	settings = ReadSettings()

	if (request.method == 'POST') and (action == 'settings'):
		response = request.form
		if('apienable' in response):
			if(response['apienable']=='enabled'):
				# Set in settings.json
				settings['api_settings']['api_enable'] = 'enabled'
				WriteSettings(settings)
			else:
				# Set in settings.json
				settings['api_settings']['api_enable'] = 'disabled'
				WriteSettings(settings)
		if('apigen' in response):
			if(response['apigen']=='requested'):
				settings['api_settings']['api_key'] = gen_api_key(32)
				WriteSettings(settings)

	if action == 'reboot':
		event = "Admin: Reboot"
		os.system("sleep 3 && sudo reboot &")
		return render_template('shutdown.html', action=action)

	elif action == 'shutdown':
		event = "Admin: Shutdown"
		os.system("sleep 3 && sudo shutdown -h now &")
		return render_template('shutdown.html', action=action)

	uptime = os.popen('uptime').readline()

	cpuinfo = os.popen('cat /proc/cpuinfo').readlines()

	ifconfig = os.popen('ifconfig').readlines()

	temp = checkcputemp()

	api_key = settings['api_settings']['api_key']

	api_enable = settings['api_settings']['api_enable']

	return render_template('admin.html', action=action, uptime=uptime, cpuinfo=cpuinfo, temp=temp, ifconfig=ifconfig, apikey=api_key, apienable=api_enable)

@app.route('/manifest')
def manifest():
    res = make_response(render_template('manifest.json'), 200)
    res.headers["Content-Type"] = "text/cache-manifest"
    return res

@app.route('/extapi/<action>', methods=['POST','GET'])
@app.route('/extapi', methods=['POST','GET'])
def extapi(action=None):
	settings = ReadSettings()

	if(action):
		event = "API Call with key: " + str(action)
		WriteLog(event)
	else:
		event = "API Call with no key."
		WriteLog(event)

	if (settings['api_settings']['api_enable'] == 'enabled'):
		if (request.method == 'POST') and (action == settings['api_settings']['api_key']):
			response = request.form
			WriteLog("Key Accepted and Entered POST parsing.")
			spkr_state = ReadSpkrState()
			spkr_count = 0

			if('spkrs_01' in response):
				spkr_state[0] = request.form['spkrs_01']
			if('spkrs_02' in response):
				spkr_state[1] = request.form['spkrs_02']
			if('spkrs_03' in response):
				spkr_state[2] = request.form['spkrs_03']
			if('spkrs_04' in response):
				spkr_state[3] = request.form['spkrs_04']

			# Count number of speakers selected, turn on protection if > 1
			for x in range(4):
				if spkr_state[x] == 'on':
					spkr_count = spkr_count + 1
			if (spkr_count > 1):
				spkr_state[4] = 'on'
			else:
				spkr_state[4] = 'off'

			WriteSpkrState(spkr_state)

			WriteLog("API Call Success.")

			return ('Success.')

	WriteLog("API Call Failed.")

	return ('404 Error.')

def gen_api_key(length):
	# Attribution to Vladimir Ignatyev on Stack Overflow
	# https://stackoverflow.com/questions/41969093/how-to-generate-passwords-in-python-2-and-python-3-securely
    charset="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghijklmnopqrstuvwxyz"
    random_bytes = os.urandom(length)
    len_charset = len(charset)
    indices = [int(len_charset * (ord(byte) / 256.0)) for byte in random_bytes]
    return "".join([charset[index] for index in indices])

def checkcputemp():
	temp = os.popen('vcgencmd measure_temp').readline()
	return temp.replace("temp=","")

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

def ReadSettings():
	# *****************************************
	# Read Switch States from File
	# *****************************************

	# Read all lines of states.json into an list(array)
	try:
		json_data_file = open("settings.json", "r")
		json_data_string = json_data_file.read()
		settings = json.loads(json_data_string)
		json_data_file.close()
	except(IOError, OSError):
		# Issue with reading states JSON, so create one/write new one

		api_key = gen_api_key(32)
		settings = {}

		settings['api_settings'] = {
			'api_enable': 'disabled', # enabled / disabled API interface
			'api_key': api_key, # Randomly Generated API Key
			}

		WriteSettings(settings)

	return(settings)

def WriteSettings(settings):
	# *****************************************
	# Write all control states to JSON file
	# *****************************************
	json_data_string = json.dumps(settings)
	with open("settings.json", 'w') as settings_file:
	    settings_file.write(json_data_string)

def WriteLog(event):
	# *****************************************
	# Function: WriteLog
	# Input: str event
	# Description: Write event to event.log
	#  Event should be a string.
	# *****************************************
	now = str(datetime.datetime.now())
	now = now[0:19] # Truncate the microseconds

	logfile = open("./logs/events.log", "a")
	logfile.write(now + ' ' + event + '\n')
	logfile.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0')
