from .task_engine.PythonTaskCaller import PythonTaskCaller
from .task_engine.BinaryTaskCaller import BinaryTaskCaller
from .task_engine.utils.remoteFolders import remoteFolders
from .task_engine.utils.dataFormats import IOFormatter
import json
from celery import Celery
import os
import traceback

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
	print('Prepared parameters : {0}'.format(parameters))
	response = session.runTask(taskname, parameters)
	return response


@app.task(name=getMachineTaskName('nodoPython'))
def nodoPython(taskname, content):
	print("parameters = {0},{1}".format(taskname, content))
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
				newFile.write(line.replace('#{userCode}', code))
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
			paramType = _translate_to_pythonTypes(prop.get('type'))
			checkcodelines.append('\tif(not isinstance({0},{1})):'.format(prop.get('name'),paramType))
			checkcodelines.append('\t\t_error = "Parameter {0} is of incorrect type"'.format(prop.get('name')))
		elif('input' in prop.get('attributes')):
			paramType = _translate_to_pythonTypes(prop.get('type'))
			checkcodelines.append('\tif({0} is not None and not isinstance({0},{1})):'.format(prop.get('name'),paramType))
			checkcodelines.append('\t\t_error = "Parameter {0} is of incorrect type"'.format(prop.get('name')))
	return checkcodelines


def _translate_to_pythonTypes(type):
	#TO DO: File must be checked also as a existing File or a existing File identifier
	typeDict = {
		'Number': 'float',
		'Boolean': 'bool',
		'String' : 'str',
		'File'	 : 'str',
		'Integer': 'int',
		'OPTION' : 'str' 
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
	image = '{"format":"inline","name":"","data":"plus,2,3"}'
	ins = json.loads(image)
	response = nodoPython('basicOps._operation', ins)
	print(json.dumps(response, indent=4, sort_keys=True)[0:500] + '(...)')

	image = '{"format":"inline","name":"","data":"maximum,2,3"}'
	ins = json.loads(image)
	response = binaryNode('basicOps._operation', ins)
	print(json.dumps(response, indent=4, sort_keys=True)[0:500] + '(...)')