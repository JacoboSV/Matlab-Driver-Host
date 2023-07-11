from .task_engine.MatlabTaskCaller import MatlabTaskCaller
from .task_engine.TaskCaller import TaskCaller
import json
from celery import Celery
import os
import sys
import traceback
import matlab.engine
from subprocess import Popen

if('linux' in sys.platform):
	P = Popen('nohup python3.6 matlabEngineLauncher.py > MLSession.log 2>&1 &', shell=True)
else:
	P = Popen('python ./tasks/task_engine/mltools/matlabEngineLauncher.py > MLSession.log 2>&1 &', shell=True)

APP_PREFIX = 'tasks' 
#NODE_NAME  = os.getenv('NODE_NAME')
NODE_NAME = 'worker_Matlab'
#app = Celery('worker')
# app = Celery('worker', backend='rpc://', broker='amqp://fusion:fusion@127.0.0.1/fusion_server')
# app = Celery('worker', backend='rpc://', broker='amqp://guest:guest@10.191.6.22/rabbitmq')
app = Celery('worker', backend='rpc://', broker='amqp://guest:guest@127.0.0.1')

def getMachineTaskName(taskname):
	return '{0}.{1}.{2}'.format(APP_PREFIX, NODE_NAME, taskname)

@app.task
def echo(content):
	task = 'myecho'
	session = MatlabTaskCaller(None, dynamic = True)
	response = session.runTask(task, content)
	return response


@app.task
def label(content):
	task = 'label'
	session = MatlabTaskCaller(None, dynamic = True)
	image = content
	response = session.runTask(task, image)
	return response


@app.task
def testme(testvariable):
	response = matlab.engine.find_matlab()
	engine = matlab.engine.connect_matlab()
	result = engine.eval('matlabEcho('+testvariable+')',background=True,nargout = 1)
	response = result.result()
	return response

def runNode(taskCaller, taskname, argsfromexecutor, nodeInfo, bdnodeInfo):
	if(taskname is None):
		return {}
	session = taskCaller(taskname, nodeInfo, bdnodeInfo)
	parameters = session.formatInputs(argsfromexecutor)
	# print("parameters : ", parameters)
	response = session.runTask(parameters)
	return response

#@app.task(name=getMachineTaskName('nodoPython'))
@app.task
def nodoMatlab(taskname, content, bdnodeInfo = {}, nodeInfo = {}):
	return runNode(MatlabTaskCaller, taskname, content, nodeInfo, bdnodeInfo)


# if __name__ == "__main__":
	# graph = json.loads('./graph.json')
	# node1_info = {'id': 1, 'name': 'Node 1', 'type': '594a36b7-4ab7-4359-b982-9904c4e1c553', 'properties': [{'name': 'textin', 'value': 'Hello World'}]}
	# node1_bbdd = {'type': '594a36b7-4ab7-4359-b982-9904c4e1c553', 'properties': [{'name': 'textin', 'local_name': 'Text In', 'type': 'String', 'default': "''", 'attributes': 'required|manual|input'}, {'name': 'textout', 'local_name': 'Text Out', 'type': 'String', 'default': "''", 'attributes': 'output'}], 'code': 'textout = textin'}
	# elementDatabaseInfo = {'properties': [{'name': 'textin', 'local_name': 'Text In', 'type': 'String', 'default': "''", 'attributes': 'required|manual|input'}, {'name': 'textout', 'local_name': 'Text Out', 'type': 'String', 'default': "''", 'attributes': 'output'}], 'code': 'textout = textin', 'userDataPath': 'share/run/admin_a2e1fb09-f909-4b8e-b3b2-cc349e81e93c', 'nodePath': '/code/share/run/admin_a2e1fb09-f909-4b8e-b3b2-cc349e81e93c/Node 1_0'}
	# info = {'id': 1, 'name': 'Node 1', 'type': '594a36b7-4ab7-4359-b982-9904c4e1c553', 'properties': [{'name': 'textin', 'value': 'Hello World'}]}
	# taskInput = {'variables': [{'name': 'textin', 'data': 'Hello World', 'type': 'String'}], 'expectedOutputs': ['textout']}
	# taskName = "Node1.userMethod"


	# elementDatabaseInfo= {'properties': [{'name': 'dataset', 'local_name': 'Dataset', 'type': 'array', 'default': '[]', 'attributes': 'required|manual|input'}, {'name': 'maximum', 'local_name': 'Maximum', 'type': 'double', 'default': '0', 'attributes': 'output'}], 'code': 'disp(dataset)\nmaximum = max(dataset)\ndisp(maximum)', 'userDataPath': 'share/run/paco_705a91c8-553e-4254-883e-1f1a65d08969', 'nodePath': '/code/share/run/paco_705a91c8-553e-4254-883e-1f1a65d08969/Node 1_0'}
	# info= {'id': 1, 'name': 'Node 1', 'type': '51068a43-902f-479d-b167-e60b9f300964', 'properties': [{'name': 'dataset', 'value': '[1,2,3,4,5,6]'}]}
	# taskInput= {'variables': [{'name': 'dataset', 'data': '[1,2,3,34,56,4,-6,5,6]', 'type': 'array'}], 'expectedOutputs': ['maximum']}
	# taskName= "Node1.userMethod"


	# elementDatabaseInfo= {'properties': [{'name': 'pathin', 'local_name': 'File Path', 'type': 'String', 'default': "''", 'attributes': 'required|manual|input'}, {'name': 'datasetout', 'local_name': 'Dataset', 'type': 'array', 'default': '[]', 'attributes': 'output'}], 'code': 'csvdata = easyFileAccess(pathin);\n% disp(csvdata)\ndatasetout = csvdata;', 'userDataPath': 'share/run/paco_5cf272bf-009c-4f8d-a493-fdabdc99f980', 'nodePath': 'share/run/paco_5cf272bf-009c-4f8d-a493-fdabdc99f980/Node 1_0'}
	# info= {'id': 1, 'name': 'Node 1', 'type': '1f417a51-4f01-48f6-9415-b6fb73684f1c', 'properties': [{'name': 'pathin', 'value': '/Datos en bruto/C15a/DES_65988_01.txt'}]}
	# taskInput= {'variables': [{'name': 'pathin', 'data': '/Datos en bruto/C15a/DES_65988_01.txt', 'type': 'String'}], 'expectedOutputs': ['datasetout']}
	# taskName= "Node1.userMethod"

	# outs = nodoMatlab(taskName, taskInput, elementDatabaseInfo, info)

	# dataset = outs['data']['output']['datasetout']

	# elementDatabaseInfo =  {'properties': [{'name': 'imageName', 'local_name': 'Name for the Image', 'type': 'String', 'default': "''", 'attributes': 'required|manual|input'}, {'name': 'datasetin', 'local_name': 'Matrix Dataset', 'type': 'array', 'default': '[]', 'attributes': 'required|manual|input'}, {'name': 'imagePath', 'local_name': 'Image Path', 'type': 'String', 'default': "''", 'attributes': 'output'}], 'code': 'fig = figure;\nplot(datasetin(:,1),datasetin(:,2));\nsaveas(fig,imageName,\'png\');\nimagePath=strcat(imageName,\'.png\');', 'userDataPath': 'share/run/paco_da7444c7-37a0-44cd-95b1-d8ba0c4a82a8', 'nodePath': '/code/share/run/paco_da7444c7-37a0-44cd-95b1-d8ba0c4a82a8/Node 2_0'}
	# info =  {'id': 2, 'name': 'Node 2', 'type': 'b572db98-a3da-4639-8b9f-00f61f8f196b', 'properties': [{'name': 'imageName', 'value': "'MatrixPlot'"}, {'name': 'datasetin', 'value': dataset}]}
	# taskInput =  {'variables': [{'name': 'imageName', 'data': "'MatrixPlot'", 'type': 'String'}, {'name': 'datasetin', 'data': dataset, 'type': 'array'}], 'expectedOutputs': ['imagePath']}
	# taskName =  'Node2.userMethod'

	# outs2 = nodoMatlab(taskName, taskInput, elementDatabaseInfo, info)
	# print("OUTS : ", outs2)




	