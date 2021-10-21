from .task_engine.MatlabTaskCaller import MatlabTaskCaller
from .task_engine.utils.remoteFolders import remoteFolders
from .task_engine.utils.dataFormats import IOFormatter
import json


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


@app.task
def nodoMatlab(taskname, content):
	if(taskname is None):
		return {}
	folderHandler = remoteFolders()
	formatter = IOFormatter() 
	session = MatlabTaskCaller(None, folderHandler, formatter, dynamic = True)
	if(isinstance(content,dict)):
		ins = content
	else:
		ins = json.loads(content)
	parameters = session.prepareParameters(ins, taskname)
	session.runTask(taskname, parameters)
	response = session.checkStatus()
	return response


if __name__ == "__main__":
	image = '{"format":"inline","name":"","data":"\'C15a\',0.001,65988,6"}'
	ins = json.loads(image)

	response = nodoMatlab('remuestrea', ins)
	print(json.dumps(response, indent=4, sort_keys=True)[0:300] + '(...)')
	print(json.dumps(response, indent=4, sort_keys=True)[-500:])
	
	result = nodoMatlab('maximo', response)	
	print(json.dumps(result, indent=4, sort_keys=True)[0:300] + '(...)')
	print(json.dumps(result, indent=4, sort_keys=True)[-500:])
	
	final = nodoMatlab('visualiza', result)
	print(json.dumps(final, indent=4, sort_keys=True)[0:300] + '(...)')
	print(json.dumps(final, indent=4, sort_keys=True)[-500:])