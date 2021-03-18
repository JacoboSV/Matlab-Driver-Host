# Configure Celery application
from celery import Celery
from callTaskAsync import MatlabTaskCaller
from callTaskAsync import PythonTaskCaller
import time
import matlab.engine
from subprocess import PIPE, Popen, STDOUT
import json
import base64

app = Celery('mytasks', backend='rpc://', broker='amqp://fusion:fusion@localhost/fusion_server')

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

# @app.task
# def nodo1(content):
	# task = 'procesado'
	# session = MatlabTaskCaller(None, dynamic = True)
	# if(isinstance(content,dict)):
		# ins = content
	# else:
		# ins = json.loads(content)
	# parameters = session.prepareParameters(ins,task)
	# session.runTask(task, parameters)
	# response = session.checkStatus()
	# return response

@app.task
def nodoMatlab(taskname,content):
	if(taskname is None):
		return {}
	session = MatlabTaskCaller(None, dynamic = True)
	if(isinstance(content,dict)):
		ins = content
	else:
		ins = json.loads(content)
	parameters = session.prepareParameters(ins,taskname)
	session.runTask(taskname, parameters)
	response = session.checkStatus()
	return response

@app.task
def nodoPython(taskname,content):
	if(taskname is None):
		return {}
	else:
		session = PythonTaskCaller(None, dynamic = True)
		if(isinstance(content,dict)):
			ins = content
		else:
			ins = json.loads(content)
		#response = taskname(content)
		parameters = session.prepareParameters(ins,taskname)
		response = session.runTask(taskname, parameters)
		#response = session.checkStatus()
	return response

# @app.task
# def nodo2(content):
	# task = 'maximo'
	# session = MatlabTaskCaller(None, dynamic = True)
	# #print(content)
	# if(isinstance(content,dict)):
		# ins = content
	# else:
		# ins = json.loads(content)
	# parameters = session.prepareParameters(ins,task)
	# session.runTask(task, parameters)
	# response = session.checkStatus()
	# return response

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
	response = nodoMatlab('remuestrea',ins)
	
	print(json.dumps(response, indent=4, sort_keys=True)[0:300] + '(...)')
	print(json.dumps(response, indent=4, sort_keys=True)[-90:])
	
	result = nodoMatlab('maximo',response)
	#result = nodoPython('procesadopy._Model_SeriesFeature',response)
	
	print(json.dumps(result, indent=4, sort_keys=True)[0:300] + '(...)')
	print(json.dumps(result, indent=4, sort_keys=True)[-90:])
	
	#final = nodoMatlab('visualiza',result)
	final = nodoPython('procesadopy._Visualization_SeriesFeaturePlot',result)

	print(json.dumps(final, indent=4, sort_keys=True)[0:50] + '(...)')
	print(json.dumps(final, indent=4, sort_keys=True)[-70:])
	
	#dataout = base64.b64decode(result['data'])
	#out_file = open("out-file.zip", "wb")
	#out_file.write(dataout)
	#out_file.close()