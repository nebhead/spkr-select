
# Speaker Selector Flask/Python script

from flask import Flask, request, render_template
import time
import os
import pickle

app = Flask(__name__)

@app.route('/', methods=['POST','GET'])
def index():

	spkr_state = ReadSpkrState()
	spkr_count = 0
	error = False
	# If posting, process input from POST
	if request.method == 'POST':
		spkr_state[0] = request.form['spkrs_01']
		spkr_state[1] = request.form['spkrs_02']
		spkr_state[2] = request.form['spkrs_03']
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


@app.route('/admin/<action>')
@app.route('/admin')
def admin(action=None):
	if action == 'reboot':
		os.system("sudo shutdown -r now")
		return 'Rebooting...'
	if action == 'shutdown':
		os.system("sudo shutdown -h now")
		return 'Shutting Down...'

	temp = checkcputemp()

	return render_template('admin.html', temp=temp, action=action)

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
		spkr_state = ['on', 'off', 'off', 'on', 'off']
		WriteSpkrState(spkr_state)

	return(spkr_state)

def WriteSpkrState(spkr_state):
	# *****************************************
	# Write Speaker State Values to File
	# *****************************************
	with open('state.dat', 'wb') as states:
		pickle.dump(spkr_state, states, protocol=2)
		states.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0')
