from abc import abstractmethod
import io
import time
from datetime import datetime
from .utils.remoteFolders import remoteFolders
from .utils.dataFormats import IOFormatter
#from .utils.taskCreator import TaskCreator
import sys
import os
import json
import builtins

class TaskCaller(object):

	def __init__(self, taskname, nodeInfo, bdnodeInfo, verbose=True):
		testing = True
		userDataPath = bdnodeInfo["userDataPath"]
		if(testing):
			print("----------WARNING----------- Testing is activated", file=sys.stderr)
			self.userDataPath = userDataPath
			nodePath = bdnodeInfo["nodePath"].replace('/code','.')
		else:
			self.userDataPath = '/code/' + userDataPath
			nodePath = bdnodeInfo["nodePath"]
		builtins._userDataPath = '/code/' + userDataPath
		code = bdnodeInfo["code"]
		properties = bdnodeInfo["properties"]
		self.expectedOuts = []
		self.taskName = taskname.split('.')[0]
		self.verbose = verbose
		self.outIO = io.StringIO()
		sys.stdout = self.outIO
		self.getInOutTypes(bdnodeInfo)
		self.log('Calling createTask')
		self.folderHandler = remoteFolders(userDataPath = nodePath)
		self.createTask(properties, code)
		self.formatter =  IOFormatter(nodeInfo, bdnodeInfo, nodePath, self.IO_types, self.language)
		self.log('Creating Folders')
		self.checkCreateFolders()
		self.taskID = self.getTaskID()
		self.initTime = time.time()
		self.log('Initialization Complete')
	
	def getInOutTypes(self,bdnodeInfo):
		'''Obtain the pairs name: type, from the graph info. 
		bdnodeInfo : dict
			Info that defines the nodes used in the graph, including type, name, nickname and code
		'''
		#self.log('bdnodeInfo = {0}'.format(bdnodeInfo))
		self.IO_types = {}
		for propert in bdnodeInfo.get('properties'):
			self.IO_types[propert['name']] = propert['type'].lower().split('[')[0]
		self.log('Input and Output types: {0}'.format(self.IO_types))

	def checkStatus(self, data=None, isError = False):
		''' Reads the status of the current work.
		This method only finishes when the task is completed or canceled
		(due to error or if the file kill.txt exists)
		'''
		self.log('Output Variables : ' + str(data))
		if(isError):
			self.updateStatus('Completed with errors')
		else:
			self.updateStatus('Completed')
		self.log('Saving outputs')
		self.savePostStatus()
		self.saveIO(data)
		outputs = self.formatOutputs(data)
		builtins._userDataPath = ''
		return outputs
		
	def updateStatus(self, newStatus):
		''' Stores the actual status in a status file
		Attributes
		----------
		newStatus : string
			New status to be logged in the status.txt file
		'''
		self.log(newStatus)
		self.folderHandler.saveData(newStatus, 'status' + str(self.taskID), self.folderHandler.paths['temp'])
		self.folderHandler.saveData(newStatus, 'status', self.folderHandler.userDataPath+'/status')
		
	def formatOutputs(self, data):
		''' Call to a formatter code that adapts the outputs from the user code to serializable data and saves it into a workspace folder 
		Attributes
		----------
		data : dict
			Outputs and information from the node code, contain two keys, output and error. Output comprises a dict with all the output 
			variables in the code. Error is empty if the code run successfully, and a stack trace if not. 
		'''
		files = None
		filepath = self._zipOutputs()
		files = self.getNewFilesPathSize()
		now = time.time()
		duration = (now - self.initTime)
		return self.formatter.formatOutputs(data, files, duration, self.initTime, now)

	def removeNewFiles(self):
		''' Removes the files created during the execution of the node from the run folder
		'''
		self.folderHandler.removeNewFiles()

	# def copyTasks(self,lib):
	# 	''' Copies the code files and manages the user libraries. 
	# 	'''
	# 	self.folderHandler.copyTasks(lib)

	def saveIO(self,data):
		''' Saves all the new data, outputs and variables after the execution of the task
		Attributes
		----------
		data : object
			The object that is returned by the task
		'''
		self.folderHandler.saveIO(data, self.outIO)
	
	def getNewFilesPathSize(self):
		'''Gets the absolute path of files in the run folder
		'''
		return self.folderHandler.getNewFilesPathSize()

	def savePreStatus(self):
		''' Makes a copy of the folder tree structure in the <runFolder> to check if something changes
		'''
		self.folderHandler.savePreStatus()

	def savePostStatus(self):
		''' Makes a copy of the folder tree structure in the <runFolder> to check if something changes
		'''
		self.folderHandler.savePostStatus()

	def _zipOutputs(self,keepFolderTree = None):
		''' Create a zip with all the files and folders inside the results folder
		'''
		self.folderHandler._zipOutputs(keepFolderTree)

	def checkCreateFolders(self):
		''' Create the main folders needed to run the scripts and store outputs
		'''
		self.folderHandler.checkCreateFolders()

	def getTaskID(self):
		return self.folderHandler.taskID

	def getRunFolder(self):
		return self.folderHandler.runFolder

	def getUserLibPath(self): 
		return self.folderHandler.userLibPath

	def getResultsFolder(self):
		return self.folderHandler.resultsFolder	
		
	# def getCodeFolder(self):
	# 	return self.folderHandler.runFolder
	# 	#return self.folderHandler.paths['tasks']

	def getCodeFolder(self):
		return self.folderHandler.paths['code']

	def killTask(self):
		''' Kills a running task
		'''
		pass
		
	def errorAnswer(self, expectedOuts, errormsg):
		'''Adapts the outputs and the error message. All the outputs are replaced with the 'Error' String,
		 the error code is added to the structure and also the message is logged into the log file. 
		 ----------
		expectedOuts : List
			COntain the names of the outputs that the graph expect
		errormsg : string
			Information about the error
		'''
		errorOutput = {} 
		self.log(errormsg, isError = True)
		for output in expectedOuts:
			errorOutput[output] = 'Error'
		errorAnswer = {'output': errorOutput, 'error': errormsg}
		self.saveIO(errorAnswer)
		return errorAnswer


	def formatInputs(self,params):
		self.log('Checking inputs')
		self.expectedOuts = params.get('expectedOutputs')
		return self.formatter.formatInputs(params, self.taskName)
	
	@abstractmethod
	def saveOutputsLocally(self,outputsNames):
		''' 
		Attributes
		----------
		outputsNames : list
			List of names of the variables generated while running the task, it must contain the exact names used in the task
		'''
		
	@abstractmethod
	def loadInputsLocally(self,inputPath, variableToLoad=None):
		''' 
		Attributes
		----------
		inputPath : string
			Path where the file that contains the variables has been saved 
		variableToLoad: string
			Name or list of names of the variables to load while running the task to be used as inputs, it must contain the exact names used in the task that collected it
		'''
		
	@abstractmethod
	def runTask(self, args):
		''' Runs a task by its name and using the sent parameters
		Attributes
		----------
		args : string or Object
			Path of the file to be used as input or the content of the file
		'''
		
	@abstractmethod
	def createTask(self, properties, code, userDataPath):
		''' 
		Attributes
		----------
		properties : list
			List of names and characteristics of the parameters to be sent/gathered to/from the task
		code : string
			Code to be run by the task
		userDataPath : string
			Shared path to put files, outputs and data 
		'''

	def log(self, data, isError = False):
		''' Print data along with the time to be used in a log file or similar
		Attributes
		----------
		data : string
			name of the task to execute, it must be the exact name of the folder and .m file (/name/name.m) inside the Tasks folder
		'''
		if(self.verbose):
			datetimestr = datetime.now()
			if(isError):
				print('[' + datetimestr.strftime("%X %x") + '] : ' + str(data))
			else:
				print('[' + datetimestr.strftime("%X %x") + '] : ' + json.dumps(str(data))[0:100])