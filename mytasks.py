# Configure Celery application
from celery import Celery
from callTaskAsync import MatlabTaskCaller
import time
import matlab.engine
from subprocess import PIPE, Popen, STDOUT
from runUserScript import MatlabSessionLauncher
import json

import base64

app = Celery('tasks', backend='rpc://', broker='amqp://fusion:fusion@localhost/myvhost')

@app.task
def echo(content):
	task = 'myecho'
	session = MatlabTaskCaller(None, dynamic = True)
	session.runTask(task, content)
	response = session.checkStatus()
	return response

@app.task
def label(content):
	task = 'label'
	session = MatlabTaskCaller(None, dynamic = True)
	image = content
	session.runTask(task, image)
	response = session.checkStatus()
	return response

def nodo1(content):
	task = 'procesado'
	session = MatlabTaskCaller(None, dynamic = True)
	parameters = session.prepareParameters(content,task)
	session.runTask(task, parameters)
	response = session.checkStatus()
	#session.removeNewFiles()
	return response

def nodo2(content):
	task = 'maximo'
	session = MatlabTaskCaller(None, dynamic = True)
	parameters = session.prepareParameters(content,task)
	session.runTask(task, parameters)
	response = session.checkStatus()
	#session.removeNewFiles()
	return response

# def isMatlabSession():

	# if(not MatlabTaskCaller.searchSharedSession()):
		# #print('Starting Matlab Session')
		# MatlabSessionLauncher.createMLSession()	
	# #else:
		# #print('Not needed to start a Matlab Session')

if __name__ == "__main__":
	#isMatlabSession()	
	image = '{"format":"inline","name":"","data":"\'C15a\',0.001,65988,6"}'
	ins = json.loads(image)
	response = nodo1(ins)
	print(json.dumps(response, indent=4, sort_keys=True)[0:50] + '(...)')
	print(json.dumps(response, indent=4, sort_keys=True)[-50:])
	#dataout = base64.b64decode(response['data'])
	#out_file = open("out-file.mat", "wb")
	#out_file.write(dataout)
	#out_file.close()
	
	result = nodo2(response)
	#print(result)
	print(json.dumps(result, indent=4, sort_keys=True)[0:50] + '(...)')
	print(json.dumps(result, indent=4, sort_keys=True)[-50:])
	
	#dataout = base64.b64decode(result['data'])
	#out_file = open("out-file.zip", "wb")
	#out_file.write(dataout)
	#out_file.close()