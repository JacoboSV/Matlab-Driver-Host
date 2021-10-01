# Configure Celery application
from celery import Celery
from callTaskAsync import MatlabTaskCaller
from callTaskAsync import PythonTaskCaller
from remoteFolders import remoteFolders
from dataFormats import ioFormatter
import json

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

@app.task
def nodoMatlab(taskname,content):
	if(taskname is None):
		return {}
	folderHandler = remoteFolders()
	formatter = ioFormatter() 
	session = MatlabTaskCaller(None, folderHandler, formatter, dynamic = True)
	if(isinstance(content,dict)):
		ins = content
	else:
		ins = json.loads(content)
	parameters = session.prepareParameters(ins,taskname)
	print(str(parameters[0:200]))
	session.runTask(taskname, parameters)
	response = session.checkStatus()
	return response

@app.task
def nodoPython(taskname,content):
	if(taskname is None):
		return {}
	else:
		folderHandler = remoteFolders()
		formatter = ioFormatter() 
		session = PythonTaskCaller(None, folderHandler, formatter, dynamic = True)
		if(isinstance(content,dict)):
			ins = content
		else:
			ins = json.loads(content)
		parameters = session.prepareParameters(ins,taskname)
		print(str(parameters[0:200]))
		response = session.runTask(taskname, parameters)
	return response


if __name__ == "__main__":
	image = '{"format":"inline","name":"","data":"plus,2,3"}'
	ins = json.loads(image)
	response = nodoPython('basicOps._operation',ins)
	
	print(json.dumps(response, indent=4, sort_keys=True)[0:300] + '(...)')
	print(json.dumps(response, indent=4, sort_keys=True)[-90:])
	
	image = '{"format":"inline","name":"","data":"\'C15a\',0.001,65988,6"}'
	ins = json.loads(image)
	response = nodoMatlab('remuestrea',ins)
	
	print(json.dumps(response, indent=4, sort_keys=True)[0:300] + '(...)')
	print(json.dumps(response, indent=4, sort_keys=True)[-90:])
	
	
	# # print(json.dumps(response, indent=4, sort_keys=True)[0:300] + '(...)')
	# # print(json.dumps(response, indent=4, sort_keys=True)[-90:])
	
	# #result = nodoMatlab('maximo',response)
	# result = nodoPython('procesadopy._Model_SeriesFeature',response)
	
	# # print(json.dumps(result, indent=4, sort_keys=True)[0:300] + '(...)')
	# # print(json.dumps(result, indent=4, sort_keys=True)[-90:])
	
	# #final = nodoMatlab('visualiza',result)
	# final = nodoPython('procesadopy._Visualization_SeriesFeaturePlot',result)

	# # print(json.dumps(final, indent=4, sort_keys=True)[0:50] + '(...)')
	# # print(json.dumps(final, indent=4, sort_keys=True)[-70:])
	
	# #dataout = base64.b64decode(result['data'])
	# #out_file = open("out-file.zip", "wb")
	# #out_file.write(dataout)
	# #out_file.close()