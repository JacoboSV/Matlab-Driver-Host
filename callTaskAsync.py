import sys
import getopt
import os
import matlab.engine
import io
import zipfile
import random
import time
from subprocess import PIPE, Popen
from datetime import datetime
import shutil
from remoteFolders import remoteFolders
import pandas as pd
import scipy.io
import importlib
from importlib.machinery import SourceFileLoader
import json
from runUserScript import sessionLauncher

class TaskCaller(object):
	def __init__(self,taskID, dynamic =False, verbose = False):
		self.dynamic = dynamic
		self.verbose = verbose;
		self.outIO = io.StringIO()
		self.errIO = io.StringIO()
		self.folderHandler = remoteFolders(taskID)
		if(dynamic):
			self.log('Dynamic Task')
		self.folderHandler.checkCreateFolders()
		self.taskID = self.folderHandler.taskID
	
	def checkStatus(self):
		''' Reads the status of the current work using the Matlab engine, this method only finishes when the task is completed or canceled (due to error or if the file kill.txt exists)
		'''
		pass
		
	def updateStatus(self,newStatus):
		''' Stores the actual status in a status file
		Attributes
		----------
		newStatus : string
			New status to be logged in the status.txt file
		'''
		
		self.folderHandler.saveData(newStatus,'status'+str(self.taskID),self.folderHandler.rootTempFolder)
		
	def formatOutputs(self,data):
		pass
			
	def removeNewFiles(self):
		self.folderHandler.removeNewFiles()
		
	def killTask(self):
		''' Kills a running task
		'''
		pass
		
	def prepareParameters(self,params,task = None):
		pass
	
	def runTask(self,name,args):
		''' Runs a task by its name and using the sent parameters
		Attributes
		----------
		name : string
			name of the task to execute, it must be the exact name of the folder and .m file (/name/name.m) inside the Tasks folder
		args : string or Object
			Path of the file to be used as input or the content of the file
		'''
		pass
				
	def log(self,data):
		''' Print data along with the time to be used in a log file or similar
		Attributes
		----------
		data : string
			name of the task to execute, it must be the exact name of the folder and .m file (/name/name.m) inside the Tasks folder
		'''
		if(self.verbose):
			datetimestr = datetime.now()
			print('[' + datetimestr.strftime("%X %x") + '] : ' + data)


class PythonTaskCaller(TaskCaller):
	def __init__(self,taskID, dynamic =False, verbose = False):
		super().__init__(taskID, dynamic, verbose)
		
	def updateStatus(self,newStatus):
		''' Stores the actual status in a status file
		Attributes
		----------
		newStatus : string
			New status to be logged in the status.txt file
		'''
		super().updateStatus(newStatus)
	
	def gatherResponse(self,data):
		self.log('Output Variables : ' + str(data))
		self.log('Completed')
		self.updateStatus('completed')
		self.log('Saving outputs')
		self.folderHandler.savePostStatus()
		self.folderHandler.saveIO(data,self.outIO)
		if(self.dynamic):
			outputs = self.formatOutputs(data)
			return outputs
		else:
			self.folderHandler._zipOutputs(keepFolderTree = True)
			return None
	
	def formatOutputs(self,data):
		outForm = self.folderHandler.readOutputFormat(self.taskName)
		runfolder = self.folderHandler.runFolder
		resultsfolder = self.folderHandler.resultsFolder
		if(outForm['format'] == "matlab"):
			path2file = self.folderHandler.locateFile(outForm['name'],runfolder)
			return self.folderHandler.populateOutData(self.folderHandler.serializeFile(path2file))
		elif(outForm['format'] == "bundle"):
			filepath = self.folderHandler._zipOutputs()
			filebytes = self.folderHandler.serializeFile(filepath)
			return self.folderHandler.populateOutData(filebytes)
			
		elif(outForm['format'] == "inline"):
			if(isinstance(data,dict)):
				outvalues = data
			else:
				outvalues = json.loads(data)
			return self.folderHandler.populateOutData(outvalues)
		elif(outForm['format'] == "json"):
			if(isinstance(data,dict)):
				outvalues = data
			else:
				outvalues = json.loads(data)
			return self.folderHandler.populateOutData(outvalues)
		else:
			print('Not Matlab, nor bundle nor inline')
			return None
			
	def removeNewFiles(self):
		super().removeNewFiles()
		
		
	def prepareParameters(self,params,task = None):
		self.log('Params format: ' + str(params['format']))
		#print('Params format: ' + str(params['format']))
		self.folderHandler.inputs = params
		if(params['format'] == 'inline'):
			return self.folderHandler.createInlineCommand()
		elif(params['format'] == 'matlab'):
			return self.folderHandler.createMatFileCommand(params,task)
		elif(params['format'] == 'json'):
			return json.dumps(params)
		else:
			return 'Error, format is not of inline type'
	
	def runTask(self,name,args):
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
		#print(pathToScript)
		#if('linux' in sys.platform):
		#	pathToScript = pathToScript.replace('\\','/')
		#else:
		#	pathToScript = pathToScript.replace('/','\\')
		try:
			module = SourceFileLoader(meth, pathToScript+".py").load_module()
		except Exception as e:
			print('Error importing: ' + str(e))
		self.taskName = name
		
		self.folderHandler.savePreStatus()
		self.log('Task : ' + str(name) + ' and params : ' + str(args))
		#print('Module : ' + str(lib) + ' and meth : ' + meth)
		#print('Params : ' + str(args[0:100]))
		#print('Params : ' + str(args[-100:]))
		# try:
		prevDir = os.getcwd()
		os.chdir(self.folderHandler.runFolder)
		self.asyncTask = getattr(module, meth)(args)
		os.chdir(prevDir)
		self.asyncTask = self.gatherResponse(self.asyncTask)
		
		return self.asyncTask
		# except Exception as e:
			# print('Error in method call: ' + str(e))
			# return None
				
	def log(self,data):
		''' Print data along with the time to be used in a log file or similar
		Attributes
		----------
		data : string
			name of the task to execute, it must be the exact name of the folder and .m file (/name/name.m) inside the Tasks folder
		'''
		super().log(data)


class MatlabTaskCaller(TaskCaller):
	"""
	Class to call a task to be run in a running matlab engine. If the session is dynamic (expects results to be returned after a while) the file runs and clears the "run" folder. If the session is not dynamic, there would be created both, run and results folders. 

	Attributes
	----------
	dynamic : Whether the script/task answer is expected or not. If false the outputs will be in a file
	verbose : Whether the class logs all the steps in the process or not
	outIO : Gathers the output of the engine when a task is running
	errIO : Gathers the errors of the engine when a task is running, now is redirected to outIO
	folderHandler : Handles the creation, inspection, updating and deleting of files (see remoteFolders.py)
	taskID: Integer that identifies the running task

	"""
	def __init__(self,taskID, dynamic =False, sessionID = None, verbose = False):
			# self.dynamic = dynamic
			# self.verbose = verbose;
			# self.outIO = io.StringIO()
			# self.errIO = io.StringIO()
			# self.folderHandler = remoteFolders(taskID)
			# if(dynamic):
				# self.log('Dynamic Task')
			# self.folderHandler.checkCreateFolders()
			# self.taskID = self.folderHandler.taskID
			super().__init__(taskID, dynamic, verbose)
			if(sessionID is not None):
					self.log('Session defined')
					self.sessionID = sessionID
					self.joinMLSession()
			else:
					self.log('Searching for sessions')
					availableSessions = self.searchSharedSession()
					if(len(availableSessions)>0):
							self.log('There are sessions')
							self.sessionID = availableSessions[0]
							self.joinMLSession()
					else:
							sessionLauncher.createMLSession()
							#print('No shared sessions')
							#raise Exception("No shared sessions, last session expired")

	def joinMLSession(self):
		''' Connects to the a Matlab session,
		'''
		try:
				self.engine = matlab.engine.connect_matlab()
		except Exception as e:
				self.log('Not available yet : ' + str(e))
				time.sleep(10)
				self.joinMLSession()
	
	@staticmethod
	def searchSharedSession():
		''' Looks for a valid running Matlab session in the computer, if present the engine is ready to be used in self.engine
		'''
		try:
			return matlab.engine.find_matlab()
		except:
			return None	

	def checkStatus(self):
		''' Reads the status of the current work using the Matlab engine, this method only finishes when the task is completed or canceled (due to error or if the file kill.txt exists)
		'''
		checkCounter = 10
		while (not self.asyncTask.done()):
			checkCounter = checkCounter + 1
			if(checkCounter>10):
				self.log('Checking and saving status...')
				checkCounter = 0
			self.updateStatus('running')
			if(os.path.exists((self.folderHandler.runFolder+'/kill.txt'))):
				self.log('Sending cancel signal to task...')
				self.killTask()
				self.updateStatus('canceled')
				return
			if(self.dynamic):
				time.sleep(0.1)
			else:
				time.sleep(10)
		variables = self.asyncTask.result()
		self.log('Output Variables : ' + str(variables))
		self.engine.close('all')
		self.log('Completed')
		self.updateStatus('completed')
		self.log('Saving outputs')
		if(self.dynamic):
			self.folderHandler.savePostStatus()
			self.folderHandler.saveIO(variables,self.outIO)
			outputs = self.formatOutputs(variables)
			return outputs
		else:
			self.folderHandler.savePostStatus()
			self.folderHandler.saveIO(variables,self.outIO)
			self.folderHandler._zipOutputs(keepFolderTree = True)
			return None

	def updateStatus(self,newStatus):
		''' Stores the actual status in a status file
		Attributes
		----------
		newStatus : string
			New status to be logged in the status.txt file
		'''
		super().updateStatus(newStatus)
		# self.folderHandler.saveData(newStatus,'status'+str(self.taskID),self.folderHandler.rootTempFolder)

	def formatOutputs(self,data):
		outForm = self.folderHandler.readOutputFormat(self.taskName)
		runfolder = self.folderHandler.runFolder
		resultsfolder = self.folderHandler.resultsFolder
		if(outForm['format'] == "matlab"):
			path2file = self.folderHandler.locateFile(outForm['name'],runfolder)
			return self.folderHandler.populateOutData(self.folderHandler.serializeFile(path2file))
		elif(outForm['format'] == "bundle"):
			filepath = self.folderHandler._zipOutputs()
			filebytes = self.folderHandler.serializeFile(filepath)
			return self.folderHandler.populateOutData(filebytes)
		elif(outForm['format'] == "json"):
			if(isinstance(data,dict)):
				outvalues = data
			else:
				outvalues = json.loads(data)
			return self.folderHandler.populateOutData(outvalues)
		else:
			print('Not Matlab nor bundle')
			return None

	def removeNewFiles(self):
		super().removeNewFiles()
		#self.folderHandler.removeNewFiles()

	def killTask(self):
		''' Kills a running task
		'''
		timeout = 10;
		while((not self.asyncTask.cancelled()) & (timeout>0)):
			timeout = timeout -1;
			time.sleep(1)
			self.log('Trying to cancel, attempts left : ' + str(timeout))
			try:
				self.asyncTask.cancel()
			except Exception as e:
				self.log('Task cannot be cancelled, due to error :')
				self.log(str(e))
		self.log('User cancelled the task')
		
	def prepareParameters(self,params,task = None):
		self.log('Params format: ' + str(params['format']))
		self.folderHandler.inputs = params
		if(params['format'] == 'inline'):
			return self.folderHandler.createInlineCommand()
		elif(params['format'] == 'matlab'):
			return self.folderHandler.createMatFileCommand(params,task)
		elif(params['format'] == 'json'):
			return json.dumps(params)
		else:
			return 'Error, format is not of inline type'
				
	def runTask(self,name,args):
		''' Runs a task by its name and using the sent parameters
		Attributes
		----------
		name : string
			name of the task to execute, it must be the exact name of the folder and .m file (/name/name.m) inside the Tasks folder
		args : string or Object
			Path of the file to be used as input or the content of the file
		'''
		self.taskName = name
		self.engine.clear(nargout=0)
		if(self.dynamic):
			self.folderHandler.copyTasks(name)
		self.folderHandler.savePreStatus()
		self.log('Using user path: ' + str(str(self.folderHandler.runFolder)))
		addpath = 'userpath("' + os.path.abspath(str(self.folderHandler.runFolder)) + '")'
		self.engine.eval(addpath,background = True,nargout=0)
		self.log('Task : ' + str(name) + ' and params : ' + str(args))
		if('exit' in name):
			self.closeMLSession()
		else:
			numberouts = int(self.engine.nargout(name))
			self.log('outs expected: ' + str(numberouts))
			try:
				#self.asyncTask = self.engine.feval(name,args, nargout=numberouts,stdout=self.outIO,stderr=self.errIO,background = True)
				if(isinstance(args,str)):
					if("'" in args):
						command = name + '("' + args + '")'
					else:
						command = name + "('" + args + "')"
				else:
					command = name + '(' + ','.join(str(x) for x in args) + ')'
				self.asyncTask = self.engine.eval(command, nargout=numberouts,stdout=self.outIO,stderr=self.errIO,background = True)
			except Exception as e:
				print('Error : ' + str(e))
				variables = 'Error'

	def closeMLSession(self):
		''' Closes a Matlab session using the self.engine or connecting to one
		'''
		if(self.engine is not None):
				self.joinMLSession()
		try:
				self.engine.eval('exit',nargout=0)
		except:
				print('Session Finished')

	def log(self,data):
		''' Print data along with the time to be used in a log file or similar
		Attributes
		----------
		data : string
			name of the task to execute, it must be the exact name of the folder and .m file (/name/name.m) inside the Tasks folder
		'''
		super().log(data)
		# if(self.verbose):
			# datetimestr = datetime.now()
			# print('[' + datetimestr.strftime("%X %x") + '] : ' + data)


def main(argv):
	ON_POSIX = 'posix' in sys.builtin_module_names
	sessionID = None
	verbose = True
	taskID = None
	path = None
	ismatlab = True
	try:
			opts, args = getopt.getopt(argv,"ht:a:s:v:i:p:r:m:",["task=","args=","session=","verbose=","taskID=","path=","runF="])
	except getopt.GetoptError:
			sys.exit(2)
	for opt, arg in opts:
			if opt == '-h':
					print('python callTaskAsync -t <taskName> -a <args> -s <sessionID> -v <verbose> -i <taskID>')
					sys.exit()
			elif opt in ("-t", "--task"):
					task = arg
			elif opt in ("-a", "--args"):
					params = arg
			elif opt in ("-s", "--session"):
					sessionID = arg
			elif opt in ("-v", "--verbose"):
					verbose = arg
			elif opt in ("-i", "--taskID"):
					taskID = arg
			elif opt in ("-m", "--isMatlab"):
					ismatlab = (arg == 'True')
	
	if(ismatlab):
		session = MatlabTaskCaller(taskID = taskID, sessionID = sessionID, verbose = verbose)
		session.runTask(task, params)
		session.checkStatus()
	else:
		session = PythonTaskCaller(taskID = taskID, verbose = verbose)
		session.runTask(task, params)

if __name__ == "__main__":
	main(sys.argv[1:])
