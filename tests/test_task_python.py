import json
from celery import Celery
from celery.execute import send_task

app = Celery('test', backend='rpc://', broker='amqp://guest:guest@localhost')

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


if __name__ == "__main__":
  input = '{"format":"inline","name":"","data":"plus,2,3"}'
  output = test_nodoPython(input)
  printResult(output)