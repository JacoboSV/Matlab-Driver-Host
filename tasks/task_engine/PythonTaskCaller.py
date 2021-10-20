import os
from importlib.machinery import SourceFileLoader
import traceback
from .TaskCaller import TaskCaller


class PythonTaskCaller(TaskCaller):

	def __init__(self, taskID, folderHandler, formatter, dynamic=False, verbose=False):
		super().__init__(taskID, folderHandler, formatter, dynamic, verbose)
	
	def updateStatus(self,newStatus):
		super().updateStatus(newStatus)

	def formatOutputs(self, data):
		return super().formatOutputs(data)

	def removeNewFiles(self):
		super().removeNewFiles()

	def prepareParameters(self, params, task=None):
		return super().prepareParameters(params, task)

	def log(self, data):
		super().log(data)
	
	def checkStatus(self,data):
		self.log('Output Variables : ' + str(data))
		self.log('Completed')
		self.updateStatus('completed')
		self.log('Saving outputs')
		self.folderHandler.savePostStatus()
		self.folderHandler.saveIO(data, self.outIO)
		if(self.dynamic):
			outputs = self.formatOutputs(data)
			return outputs
		else:
			self.folderHandler._zipOutputs(keepFolderTree = True)
			return None
	
	def runTask(self, name, args):
		''' Runs a task by its name and using the sent parameters
		Attributes
		----------
		name : string
			name of the task to execute, it must be the exact name of the folder and .m file (/name/name.m) inside the Tasks folder
		args : string or Object
			Path of the file to be used as input or the content of the file
		'''
		module_method = name.split('.')
		lib = module_method[0]
		meth = module_method[1]
		if(self.dynamic):
			self.folderHandler.copyTasks(lib)
		pathToScript = os.path.join(self.folderHandler.runFolder, lib)
		try:
			module = SourceFileLoader(meth, pathToScript+".py").load_module()
		except Exception as e:
			print('Error importing method: ' + meth + ", from file: " + pathToScript + ", Error: "  + str(e))
			traceback.print_exc()
		self.taskName = name
		
		self.folderHandler.savePreStatus()
		self.log('Task : ' + str(name) + ' and params : ' + str(args))
		try:
			prevDir = os.getcwd()
			os.chdir(self.folderHandler.runFolder)
			try:
				self.asyncTask = getattr(module, meth)(args)
			except:
				self.asyncTask = getattr(module, meth)(*args)
			os.chdir(prevDir)
			self.asyncTask = self.checkStatus(self.asyncTask)
			return self.asyncTask
		except Exception as e:
			#print('Error calling method: ' + meth + ", with arguments: "+ str(args) + ", Error: " + str(e))
			traceback.print_exc()
			return None