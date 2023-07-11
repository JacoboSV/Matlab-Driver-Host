from .task_engine.PythonTaskCaller import PythonTaskCaller
from .task_engine.BinaryTaskCaller import BinaryTaskCaller
from .task_engine.BinaryTaskCaller import TaskCaller
import json
from celery import Celery
import os
import traceback

APP_PREFIX = 'tasks'
NODE_NAME  = os.getenv('NODE_NAME')
app = Celery('worker', backend='rpc://', broker='amqp://fusion:fusion@127.0.0.1/fusion_server')

def getMachineTaskName(taskname):
	return '{0}.{1}.{2}'.format(APP_PREFIX, NODE_NAME, taskname)

def runNode(taskCaller, taskname, argsfromexecutor, nodeInfo, bdnodeInfo):
	if(taskname is None):
		return {}
	session = taskCaller(taskname, nodeInfo, bdnodeInfo)
	print("argsfromexecutor : ", argsfromexecutor)
	parameters = session.formatInputs(argsfromexecutor)
	print("parameters : ", parameters)
	response = session.runTask(parameters)
	return response

#@app.task(name=getMachineTaskName('nodoPython'))
@app.task
def nodoPython(taskname, content, bdnodeInfo = {}, nodeInfo = {}):
	return runNode(PythonTaskCaller, taskname, content, nodeInfo, bdnodeInfo)

@app.task(name=getMachineTaskName('binaryNode'))
def binaryNode(taskname, content):
	return runNode(BinaryTaskCaller, taskname, content)
