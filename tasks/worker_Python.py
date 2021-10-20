from .task_engine.PythonTaskCaller import PythonTaskCaller
from .task_engine.utils.remoteFolders import remoteFolders
from .task_engine.utils.dataFormats import ioFormatter
import json
from celery import Celery

app = Celery('tasks')

@app.task
def nodoPython(taskname, content):
	if(taskname is None):
		return {}
	else:
		folderHandler = remoteFolders()
		formatter = ioFormatter()
		session = PythonTaskCaller(None, folderHandler, formatter, dynamic = True)
		if(isinstance(content, dict)):
			ins = content
		else:
			ins = json.loads(content)
		parameters = session.prepareParameters(ins, taskname)
		response = session.runTask(taskname, parameters)
	return response


if __name__ == "__main__":
	image = '{"format":"inline","name":"","data":"plus,2,3"}'
	ins = json.loads(image)
	response = nodoPython('basicOps._operation', ins)
	
	print(json.dumps(response, indent=4, sort_keys=True)[0:500] + '(...)')