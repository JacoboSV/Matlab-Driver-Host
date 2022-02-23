from abc import abstractmethod
import io
import time
from datetime import datetime


class TaskCaller(object):


	def __init__(self, taskID, folderHandler, formatter, dynamic=False, verbose=False):
		self.dynamic = dynamic
		self.verbose = verbose
		self.outIO = io.StringIO()
		self.errIO = io.StringIO()
		self.folderHandler = folderHandler
		self.formatter = formatter
		if(dynamic):
			self.log('Dynamic Task')
		self.folderHandler.checkCreateFolders()
		self.taskID = self.folderHandler.taskID
		self.initTime = time.time()
	
	def checkStatus(self, data=None):
		''' Reads the status of the current work.
		This method only finishes when the task is completed or canceled
		(due to error or if the file kill.txt exists)
		'''
		self.log('Output Variables : ' + str(data))
		self.log('Completed')
		self.updateStatus('completed')
		self.log('Saving outputs')
		self.folderHandler.savePostStatus()
		self.folderHandler.saveIO(data, self.outIO)
		if(self.dynamic):
			outputs = self.formatOutputs(data)
			#print(outputs)
			return outputs
		else:
			self.folderHandler._zipOutputs(keepFolderTree = True)
			return None
		
	def updateStatus(self, newStatus):
		''' Stores the actual status in a status file
		Attributes
		----------
		newStatus : string
			New status to be logged in the status.txt file
		'''
		self.folderHandler.saveData(newStatus, 'status' + str(self.taskID), self.folderHandler.paths['temp'])
		
	def formatOutputs(self, data):
		#outForm = self.formatter.readOutputFormat(self.taskName)
		files = None
		runfolder = self.folderHandler.runFolder
		resultsfolder = self.folderHandler.resultsFolder
		filepath = self.folderHandler._zipOutputs()
		files = self.folderHandler.getNewFilesPathSize()
		now = time.time()
		duration = now - self.initTime 
		return self.formatter.formatOutputs(runfolder, resultsfolder, data, files, duration, self.initTime, now)

	def removeNewFiles(self):
		self.folderHandler.removeNewFiles()
		
	def killTask(self):
		''' Kills a running task
		'''
		pass
		
	def prepareParameters(self,params, task = None):
		#self.log('Params format: ' + str(params['format']))
		path = self.folderHandler.runFolder
		return self.formatter.formatInputs(params, task, path)
	
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
	def runTask(self, name, args, expectedOuts = None):
		''' Runs a task by its name and using the sent parameters
		Attributes
		----------
		name : string
			name of the task to execute, it must be the exact name of the folder and .m file (/name/name.m) inside the Tasks folder
		args : string or Object
			Path of the file to be used as input or the content of the file
		'''
				
	def log(self, data):
		''' Print data along with the time to be used in a log file or similar
		Attributes
		----------
		data : string
			name of the task to execute, it must be the exact name of the folder and .m file (/name/name.m) inside the Tasks folder
		'''
		if(self.verbose):
			datetimestr = datetime.now()
			print('[' + datetimestr.strftime("%X %x") + '] : ' + str(data)[0:200])