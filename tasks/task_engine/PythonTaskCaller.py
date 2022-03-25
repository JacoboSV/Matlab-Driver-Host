import os
from importlib.machinery import SourceFileLoader
import traceback
from .TaskCaller import TaskCaller
import json

class PythonTaskCaller(TaskCaller):


	def runTask(self, name, args, expectedOuts = None):
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
		self.folderHandler.copyTasks(lib)
		pathToScript = os.path.join(self.folderHandler.runFolder, lib)
		try:
			module = SourceFileLoader(meth, pathToScript+".py").load_module()
		except Exception as e:
			print('Error importing method: ' + meth + ", from file: " + pathToScript + ", Error: "  + str(e))
			print(traceback.print_exc())
		self.taskName = name
		
		self.folderHandler.savePreStatus()
		self.log('Task : ' + str(name) + ' and params : ' + str(args))
		try:
			prevDir = os.getcwd()
			os.chdir(self.folderHandler.runFolder)
			try:
				self.asyncTask = getattr(module, meth)(**args)
			except:
				print('Args are not a dict type')
				try:
					self.asyncTask = getattr(module, meth)(*args)
				except:
					print('Args are not aarray type')
					self.asyncTask = getattr(module, meth)(args)
			os.chdir(prevDir)
			
			outputsNames = {}
			print("expectedOuts",expectedOuts)
			for counter, key in enumerate(expectedOuts):
				outputsNames[key] = self.asyncTask.get('output')[counter]
			self.saveOutputsLocally(outputsNames)
			self.asyncTask['output'] = outputsNames
			
			self.asyncTask = self.checkStatus(self.asyncTask)
			return self.asyncTask
		except Exception as e:
			print('Error calling method: ' + meth + ", with arguments: "+ str(args) + ", Error: " + traceback.print_exc())
			return None
		
	def saveOutputsLocally(self,outputsNames):
		''' 
		Attributes
		----------
		name : dict
			Dict of names and values of the variables generated while running the task, it must contain the exact names used in the task
		'''
		
		#outputsNames = {}
		#for counter, key in enumerate(expectedOuts):
		#	outputsNames[key] = self.asyncTask.get('output')[counter]
		#print("outputsNames: ",outputsNames)
		filename = self.folderHandler.runFolder + '/LocalOutputs.json'
		filenpath = os.path.join(self.folderHandler.runFolder, filename)
		my_file = open(filename,'w')
		json.dump(outputsNames,my_file)
		my_file.close()
		