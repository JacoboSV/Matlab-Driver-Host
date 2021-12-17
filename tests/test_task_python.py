import json, os
from celery import Celery
from celery.execute import send_task

app = Celery('test', backend='rpc://', broker=os.getenv('BROKER_URL'))

def printResult(response):
	messageResponse = json.dumps(response, indent=4, sort_keys=True)
	if(len(messageResponse)>600):
		print(messageResponse[0:400] + '(...)')
		print(messageResponse[-200:])
	else:
		print(messageResponse)


def test_nodoPython(image):
	content = json.loads(image)
	result = send_task("tasks.worker_Python.nodoPython", ['basicOps._operation', content])
	response = result.get()
	return response


def test_BinaryNode(taskname, input):
	content = json.loads(input)
	result = send_task("tasks.worker_Python.binaryNode", [taskname, content])
	response = result.get()
	return response

if __name__ == "__main__":
  input = '{"format":"inline","name":"","data":"maximum,2,3"}'
  output = test_nodoPython(input)
  printResult(output)

  output = test_BinaryNode(
		'C/basicOps/run',
  	'{"format":"inline","name":"","data":"maximum,2,4"}'
	)
  printResult(output)

  output = test_BinaryNode(
		'C/FPGA/fpga',
		'{"format":"inline","name":"","data":"code/misdatos/hola_mundo.txt"}'
	)
  printResult(output)