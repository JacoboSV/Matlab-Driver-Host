from .task_engine.MatlabTaskCaller import MatlabTaskCaller
from .task_engine.utils.remoteFolders import remoteFolders
from .task_engine.utils.dataFormats import IOFormatter
import json
from celery import Celery
import os
import traceback
import matlab.engine

APP_PREFIX = 'tasks'
#NODE_NAME  = os.getenv('NODE_NAME')
NODE_NAME = 'worker_Matlab'
#app = Celery('worker')
app = Celery('worker', backend='rpc://', broker='amqp://fusion:fusion@127.0.0.1/fusion_server')
#app = Celery('worker', backend='rpc://', broker='amqp://guest:guest@10.191.6.22/rabbitmq')

def getMachineTaskName(taskname):
	return '{0}.{1}.{2}'.format(APP_PREFIX, NODE_NAME, taskname)

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
def testme(testvariable):
	response = matlab.engine.find_matlab()
	engine = matlab.engine.connect_matlab()
	result = engine.eval('matlabEcho('+testvariable+')',background=True,nargout = 1)
	response = result.result()
	return response


@app.task(name=getMachineTaskName('nodoMatlab'))
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

@app.task
def createTask(name, properties, code):
	try:	
		paramsSTR = _properties_to_params(properties)
		outsSTR = _properties_to_outputs(properties)
		paramsCheckCode = _properties_to_code(properties)
		templateFile = open('code/template/template.m')
		if not os.path.exists('code/'+name):
			os.makedirs('code/'+name)
		newFile = open('code/'+name +'/'+ name + '.m','w')
		for line in templateFile:
			if('#{userCode}' in line):
				for cline in code.splitlines():
					newFile.write(line.replace('#{userCode}', '\t'+cline))
			elif('{parameters}' in line):
				line = line.replace('{parameters}', paramsSTR)
				if('{taskName}' in line):
					newFile.write(line.replace('{taskName}', name))
				else:
					newFile.write(line)
			elif('#{outputsCode}' in line):
				newFile.write(line.replace('#{outputsCode}', outsSTR))
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

def _properties_to_outputs(properties):
	propsList = []
	for prop in properties:
		if('required' in prop.get('attributes') and 'output' in prop.get('attributes')):
			propsList.append("'" + prop.get('name') + "'," + prop.get('name'))
	outsSTR = 'struct('+ ','.join(propsList)+')'
	return outsSTR

def _properties_to_params(properties):
	propsList = []
	for prop in properties:
		if('required' in prop.get('attributes') and 'input' in prop.get('attributes')):
			propsList.append(prop.get('name'))
		elif('input' in prop.get('attributes')):
			propsList.append(prop.get('name'))
	paramsSTR = ','.join(propsList)
	return paramsSTR

def _properties_to_code(properties):
	checkcodelines = []
	#===========================================================================
	# checkTypeDict= {
	# 	'python': 'not isinstance',
	# 	'matlab': '~ isa',
	# 	}
	#===========================================================================
	for prop in properties:
		if('required' in prop.get('attributes') and 'input' in prop.get('attributes')):
			paramType = _translate_to_pythonTypes(prop.get('type'))
			checkcodelines.append('\tif(~ isa({0},{1}))'.format(prop.get('name'),paramType))
			checkcodelines.append('\t\terror = "Parameter {0} is of incorrect type;"'.format(prop.get('name')))
			checkcodelines.append('end')
		elif('input' in prop.get('attributes')):
			paramType = _translate_to_pythonTypes(prop.get('type'))
			checkcodelines.append('\tif(exist("{0}","var") & ~ isa({0},{1}))'.format(prop.get('name'),paramType))
			checkcodelines.append('\t\terror = "Parameter {0} is of incorrect type;"'.format(prop.get('name')))
			checkcodelines.append('end')
	return checkcodelines


def _translate_to_pythonTypes(type):
	#TO DO: File must be checked also as a existing File or a existing File identifier
	typeDict = {
		'number': '"float"',
		'array': '"double"',
		'list': '"double"',
		'matrix': '"double"',
		'boolean': '"logical"',
		'string' : '"char"',
		'file'	 : '"char"',
		'integer': '"integer"',
		'OPTION' : '"char"' 
		}
	return typeDict.get(type.split('[')[0])

def _createFormatFiles(name):
	inputFormat = {'data': '', 'name': '', 'format': 'inline'}
	outputFormat = {}
	userMethod = {'data': '', 'name': '', 'format': 'json'}
	userFormat = {}
	userFormat[name] = userMethod
	outputFormat['formats'] = userFormat
	newInputFF = open('code/'+name +'/inputformat.txt','w')
	newInputFF.write(json.dumps(inputFormat))
	newOutputFF = open('code/'+name +'/outputformat.txt','w')
	newOutputFF.write(json.dumps(outputFormat))
	newInputFF.close()
	newOutputFF.close()

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