import os
from importlib.machinery import SourceFileLoader
import traceback
from .TaskCaller import TaskCaller
import json
from .utils.taskCreator import TaskCreator


class PythonTaskCaller(TaskCaller):

	def __init__(self,taskID, nodeInfo, bdnodeInfo, sessionID = None, verbose = True):
		self.language = 'python'
		super().__init__(taskID, nodeInfo, bdnodeInfo)
		

	def runTask(self, args):
		''' Runs a task by its name and using the sent parameters
		Attributes
		----------
		args : string or Object
			Path of the file to be used as input or the content of the file
		'''
		self.updateStatus('Started')
		methodName = 'userMethod'
		#self.copyTasks(self.taskName)
		self.updateStatus('Preparing Data')
		pathToScript = os.path.join(self.getRunFolder(), self.taskName)
		try:
			module = SourceFileLoader(methodName, pathToScript+".py").load_module()
		except Exception as e:
			errormsg = 'Error importing method: ' + methodName + ", from file: " + pathToScript + ", Error: "  + traceback.format_exc()
			return self.errorAnswer(self.expectedOuts, errormsg)
		self.savePreStatus()
		self.log('Task : ' + str(self.taskName) + ' and params : ' + (str(args)))
		self.updateStatus('Running task')
		try:
			prevDir = os.getcwd()
			os.chdir(self.getRunFolder())
			self.asyncTask = getattr(module, methodName)(**args)
			os.chdir(prevDir)
			self.updateStatus('Task ended, gathering outputs')
			outputsNames = {}
			self.log("Expected Outputs to recover from Node: {0}".format(self.expectedOuts))
			for counter, key in enumerate(self.expectedOuts):
				outputsNames[key] = self.asyncTask.get('output')[counter]
			self.saveOutputsLocally(outputsNames)
			self.asyncTask['output'] = outputsNames
			self.asyncTask = self.checkStatus(self.asyncTask)
			return self.asyncTask
		except Exception as e:
			errormsg = 'Error: ' + traceback.format_exc()
			return self.checkStatus(self.errorAnswer(self.expectedOuts, errormsg))
	

	def saveOutputsLocally(self,outputsNames):
		''' 
		Attributes
		----------
		name : dict
			Dict of names and values of the variables generated while running the task, it must contain the exact names used in the task
		'''
		filename = self.getRunFolder() + '/LocalOutputs.json'
		#filenpath = os.path.join(self.getRunFolder(), filename)
		my_file = open(filename,'w')
		
		outputValues = {}
		for name in outputsNames:
			outputValues[name] = self.formatter.checkTypes(outputsNames.get(name))
		
		my_file.write(json.dumps(outputValues))
		my_file.close()

	def createTask(self, properties, code):
		'''Creates a file to run the node code from a template. 
		 ----------
		properties : List
			COntain the names of the outputs that the graph expect
		code : string
			Information about the error
		'''
		taskCreator = TaskCreator()
		taskCreator.createTask(self.taskName, properties, code, self.getCodeFolder(), self.getRunFolder())