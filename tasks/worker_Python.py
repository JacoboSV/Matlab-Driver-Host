from .task_engine.PythonTaskCaller import PythonTaskCaller
from .task_engine.BinaryTaskCaller import BinaryTaskCaller
from .task_engine.utils.remoteFolders import remoteFolders
from .task_engine.utils.dataFormats import IOFormatter
import json
from celery import Celery
import os
import traceback

APP_PREFIX = 'tasks'
#NODE_NAME  = os.getenv('NODE_NAME')
NODE_NAME = 'worker_Python'
#app = Celery('worker')
app = Celery('worker', backend='rpc://', broker='amqp://fusion:fusion@127.0.0.1/fusion_serverpython')

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
	#print('Prepared parameters : {0}'.format(parameters))
	response = session.runTask(taskname, parameters, content.get('expectedOutputs'))
	return response


@app.task(name=getMachineTaskName('nodoPython'))
def nodoPython(taskname, content):
	print("parameters = {0},{1}".format(taskname, content))
	print('---------------------------------------------')
	return runNode(PythonTaskCaller, taskname, content)

@app.task
def createTask(name, properties, code):
	try:	
		paramsSTR = _properties_to_params(properties)
		paramsCheckCode = _properties_to_code(properties)
		templateFile = open('code/template/template.py')
		if not os.path.exists('code/'+name):
			os.makedirs('code/'+name)
		newFile = open('code/'+name +'/'+ name + '.py','w')
		for line in templateFile:
			if('#{userCode}' in line):
				for cline in code.splitlines():
					newFile.write(line.replace('#{userCode}', '\t'+cline))
			elif('{parameters}' in line):
				newFile.write(line.replace('{parameters}', paramsSTR))
			elif('{parametersInFunction}' in line):
				params_in_call = paramsSTR.replace(' = None','')
				newFile.write(line.replace('{parametersInFunction}', params_in_call))
			elif('{Check params}' in line):
				newFile.write('\n'.join(paramsCheckCode)+'\n')
			else:
				newFile.write(line)
		newFile.close()
		templateFile.close()
		_createFormatFiles(name)
		return {'error': False, 'errorCode': ''}
	except Exception as e:
		print('Exception when creating new task')
		print(traceback.format_exc())
		return {'error': True, 'errorCode': str(e)}

def _properties_to_params(properties):
	propsList = []
	for prop in properties:
		if('required' in prop.get('attributes') and 'input' in prop.get('attributes')):
			propsList.append(prop.get('name'))
		elif('input' in prop.get('attributes')):
			propsList.append(prop.get('name') + ' = None')
	paramsSTR = ','.join(propsList)
	return paramsSTR

def _properties_to_code(properties):
	checkcodelines = []
	for prop in properties:
		if('required' in prop.get('attributes') and 'input' in prop.get('attributes')):
			paramType = _translate_to_pythonTypes(prop.get('type').lower())
			checkcodelines.append('\tif(not isinstance({0},{1})):'.format(prop.get('name'),paramType))
			checkcodelines.append('\t\t_error = "Parameter {0} is of incorrect type"'.format(prop.get('name')))
		elif('input' in prop.get('attributes')):
			paramType = _translate_to_pythonTypes(prop.get('type').lower())
			checkcodelines.append('\tif({0} is not None and not isinstance({0},{1})):'.format(prop.get('name'),paramType))
			checkcodelines.append('\t\t_error = "Parameter {0} is of incorrect type"'.format(prop.get('name')))
	return checkcodelines


def _translate_to_pythonTypes(type):
	#TO DO: File must be checked also as a existing File or a existing File identifier
	typeDict = {
		'number': '"float"',
		'array': '"list"',
		'list': '"list"',
		'matrix': '"list"',
		'boolean': '"logical"',
		'string' : '"char"',
		'file'	 : '"char"',
		'integer': '"integer"',
		'OPTION' : '"char"' 
		}
	return typeDict.get(type.split('[')[0])

def _createFormatFiles(name):
	inputFormat = {'data': '', 'name': '', 'format': 'inline'}
	outputFormat = {"formats": {'userMethod' : {'data': '', 'name': '', 'format': 'json'}}}
	newInputFF = open('code/'+name +'/inputformat.txt','w')
	newInputFF.write(json.dumps(inputFormat))
	newOutputFF = open('code/'+name +'/outputformat.txt','w')
	newOutputFF.write(json.dumps(outputFormat))
	newInputFF.close()
	newOutputFF.close()

@app.task(name=getMachineTaskName('binaryNode'))
def binaryNode(taskname, content):
	return runNode(BinaryTaskCaller, taskname, content)

if __name__ == "__main__":
	image = '{"variables":[{"name": "input1","type": "float", "subtype": "","location": "inline","data": 5.5},{"name": "input2","type": "array", "subtype": "","location": "inline","data": [1,2,3,4,5]},{"name": "input3","type": "file", "subtype": "txt","location": "server","data": "c:/Users/Jacob/.EjsConsole.txt"},{"name": "input4","type": "file", "subtype": "txt","location": "inline","data": "SmF2YVJvb3Q9Ckxhbmd1YWdlPUxvY2FsZQpVcGRhdGU9QUxXQVlTCkxhc3RVcGRhdGU9MTYyMTg1OTc2MTM0NgpJZ25vcmVVcGRhdGVWZXJzaW9uPQpNaW5pbWl6ZWQ9ZmFsc2UKWm9vbUxldmVsPTAKVXNlckRpcj1EOi9Vc2Vycy9Xb3Jrc3BhY2UvCkV4dGVybmFsQXBwcz1mYWxzZQpMb2FkTGFzdEZpbGU9ZmFsc2UKUHJvZ3JhbW1pbmdMYW5ndWFnZT1KQVZBU0NSSVBUCk1hdGxhYkRpcj0KVk1wYXJhbXM9LVhteDI1Nm0KQXJndW1lbnRzPQpMb29rQW5kRmVlbD1OaW1idXMKU2NyZWVuPTAKV2lkdGg9NzkzCkhlaWdodD0yODQK"}], "expectedOutputs":["a","b","c","d"]}'
	
	ins = json.loads(image)
	response = nodoPython('basicOps._tester', ins)
	print(json.dumps(response, indent=4, sort_keys=True)[0:900] + '(...)')

	#===========================================================================
	# image = '{"format":"inline","name":"","data":"maximum,2,3"}'
	# ins = json.loads(image)
	# response = binaryNode('basicOps._operation', ins)
	# print(json.dumps(response, indent=4, sort_keys=True)[0:500] + '(...)')
	#===========================================================================