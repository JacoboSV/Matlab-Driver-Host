from .task_engine.PythonTaskCaller import PythonTaskCaller
from .task_engine.BinaryTaskCaller import BinaryTaskCaller
from .task_engine.utils.remoteFolders import remoteFolders
from .task_engine.utils.dataFormats import IOFormatter
import json
from celery import Celery
import os

APP_PREFIX = 'tasks'
NODE_NAME  = os.getenv('NODE_NAME')
app = Celery('worker')

def getMachineTaskName(taskname):
	return '{0}.{1}.{2}'.format(APP_PREFIX, NODE_NAME, taskname)

def runNode(taskCaller, taskname, content):
	if(taskname is None):
		return {}
	folderHandler = remoteFolders()
	formatter = IOFormatter()
	session = taskCaller(None, folderHandler, formatter, dynamic = True)
	if(isinstance(content, dict)):
		ins = content
	else:
		ins = json.loads(content)
	parameters = session.prepareParameters(ins, taskname)
	response = session.runTask(taskname, parameters)
	return response


@app.task(name=getMachineTaskName('nodoPython'))
def nodoPython(taskname, content):
	return runNode(PythonTaskCaller, taskname, content)


@app.task(name=getMachineTaskName('binaryNode'))
def binaryNode(taskname, content):
	return runNode(BinaryTaskCaller, taskname, content)

if __name__ == "__main__":
	image = '{"format":"inline","name":"","data":"plus,2,3"}'
	ins = json.loads(image)
	response = nodoPython('basicOps._operation', ins)
	print(json.dumps(response, indent=4, sort_keys=True)[0:500] + '(...)')

	image = '{"format":"inline","name":"","data":"maximum,2,3"}'
	ins = json.loads(image)
	response = binaryNode('basicOps._operation', ins)
	print(json.dumps(response, indent=4, sort_keys=True)[0:500] + '(...)')