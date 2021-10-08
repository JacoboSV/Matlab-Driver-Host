# Configure Celery application
from celery import Celery
from callTaskAsync import MatlabTaskCaller
import time
import matlab.engine
from subprocess import PIPE, Popen, STDOUT
#from runUserScript import MatlabSessionLauncher
import json
import base64
from celery.execute import send_task


app = Celery('mytasks', backend='rpc://', broker='amqp://fusion:fusion@62.204.199.200/fusion_server')

@app.task
def echo(content):
	image = '{"format":"inline","name":"","data":"plus,2,3"}'
	content = json.loads(image)

	result = send_task("tasks.echo", ['basicOps._operation'])
	response = result.get()
	#self.send(text_data=response)
	#response = result.get(timeout=0.6)
	#response = nodoPython('basicOps._operation',ins)
	print(json.dumps(response, indent=4, sort_keys=True)[0:300] + '(...)')
	print(json.dumps(response, indent=4, sort_keys=True)[-90:])
	#task = 'myecho'
	#session = MatlabTaskCaller(None, dynamic = True)
	#session.runTask(task, content)
	#response = session.checkStatus()
	
	return response


@app.task
def test():

	image = '{"format":"inline","name":"","data":"plus,2,3"}'
	content = json.loads(image)
	result = send_task("tasks.nodoPython", ['basicOps._operation',content])
	response = result.get(timeout=0.6)
	print(json.dumps(response, indent=4, sort_keys=True)[0:300] + '(...)')
	#print(json.dumps(response, indent=4, sort_keys=True)[-90:])
	return response

@app.task
def basic_operations(operation, operand1, operand2 = None):
	isOneOperand = operand2 is None
	if(isOneOperand):
		data = f'{operation},{operand1}'
		opType ='basicOps._function'
	else:
		data = f'{operation},{operand1},{operand2}'
		opType ='basicOps._operation'
	callParams = {"format":"inline", "name":"", "data": data}
	result = send_task("tasks.nodoPython", [opType,callParams])
	response = result.get(timeout=0.6)
	print(json.dumps(response, indent=4, sort_keys=True)[0:400] + '(...)')
	#print(json.dumps(response, indent=4, sort_keys=True)[-90:])
	
	
	
# @app.task
# def label(content):
	# task = 'label'
	# session = MatlabTaskCaller(None, dynamic = True)
	# image = content
	# session.runTask(task, image)
	# response = session.checkStatus()
	# return response

# @app.task
# def nodo1(content):
	# task = 'procesado'
	# session = MatlabTaskCaller(None, dynamic = True)
	# print(content)
	# ins = json.loads(content)
	# parameters = session.prepareParameters(ins,task)
	# session.runTask(task, parameters)
	# response = session.checkStatus()
	# #session.removeNewFiles()
	# return response

# @app.task
# def nodo2(content):
	# task = 'maximo'
	# session = MatlabTaskCaller(None, dynamic = True)
	# print(content)
	# ins = json.loads(content)
	# parameters = session.prepareParameters(ins,task)
	# session.runTask(task, parameters)
	# response = session.checkStatus()
	# #session.removeNewFiles()
	# return response

# def isMatlabSession():

	# if(not MatlabTaskCaller.searchSharedSession()):
		# #print('Starting Matlab Session')
		# MatlabSessionLauncher.createMLSession()	
	# #else:
		# #print('Not needed to start a Matlab Session')

# if __name__ == "__main__":
	# #isMatlabSession()	
	# image = '{"format":"inline","name":"","data":"\'C15a\',0.001,65988,6"}'
	# ins = json.loads(image)
	# response = nodo1(ins)
	# print(json.dumps(response, indent=4, sort_keys=True)[0:50] + '(...)')
	# print(json.dumps(response, indent=4, sort_keys=True)[-50:])
	# #dataout = base64.b64decode(response['data'])
	# #out_file = open("out-file.mat", "wb")
	# #out_file.write(dataout)
	# #out_file.close()
	
	# result = nodo2(response)
	# #print(result)
	# print(json.dumps(result, indent=4, sort_keys=True)[0:50] + '(...)')
	# print(json.dumps(result, indent=4, sort_keys=True)[-50:])
	
	#dataout = base64.b64decode(result['data'])
	#out_file = open("out-file.zip", "wb")
	#out_file.write(dataout)
	#out_file.close()