import os
import matlab.engine
import time
from .matlab.runUserScript import sessionLauncher
from .TaskCaller import TaskCaller


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
	def __init__(self,taskID, folderHandler, formatter, dynamic =False, sessionID = None, verbose = True):
		super().__init__(taskID, folderHandler, formatter, dynamic, verbose)
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
						while(self.searchSharedSession() is None):
							time.sleep(10)
							self.sessionID = self.searchSharedSession()[0]
						self.joinMLSession()
		
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

	def checkStatus(self, data=None):
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
		self.log('Task finished')
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
			#print("expectedOuts",self.expectedOuts)
			#for counter, key in enumerate(self.expectedOuts):
			#	outputsNames[key] = self.asyncTask.get('output')[counter]
			#self.saveOutputsLocally(outputsNames)
			return outputs
		else:
			self.folderHandler.savePostStatus()
			self.folderHandler.saveIO(variables,self.outIO)
			self.folderHandler._zipOutputs(keepFolderTree = True)
			return None

	def killTask(self):
		''' Kills a running task
		'''
		timeout = 10
		while((not self.asyncTask.cancelled()) & (timeout>0)):
			timeout = timeout -1
			time.sleep(1)
			self.log('Trying to cancel, attempts left : ' + str(timeout))
			try:
				self.asyncTask.cancel()
			except Exception as e:
				self.log('Task cannot be cancelled, due to error :')
				self.log(str(e))
		self.log('User cancelled the task')
				
	def runTask(self,name,args,expectedOuts = None):
		''' Runs a task by its name and using the sent parameters
		Attributes
		----------
		name : string
			name of the task to execute, it must be the exact name of the folder and .m file (/name/name.m) inside the Tasks folder
		args : string or Object
			Path of the file to be used as input or the content of the file
		'''
		self.taskName = name
		self.expectedOuts = expectedOuts
		# TO DO: poner esto como opcional en función del quien sea el usuario anterior y demas. Si es una tarea diferente no la mando me espero, si es la misma del mismo usuario. 
		# Podría lanzarse un engine por usuario? Pensarlo.
		# Una solucion: Las tareas seran unicas (de unica ejecucion) o de ejecucion mantenida (QUe pueden usar el mismo workspace). Si es de tipo único se borra antes y despues.
		# Si es ejecuion mantenida no borra nada
		# Segundo control, mirar si las tareas son del mismo usuario o de otro: Mirar como informar al servidor del usurio 
		#self.engine.clear(nargout=0)
		if(self.dynamic):
			self.folderHandler.copyTasks(name)
		self.folderHandler.savePreStatus()
		userpath = os.path.abspath(str(self.folderHandler.runFolder))
		self.log('Using user path: ' + str(str(self.folderHandler.runFolder)))
		addpath = 'userpath("' + userpath  + '")'
		self.engine.eval(addpath,background = True,nargout=0)
		self.engine.eval('cd ' + userpath,background = True,nargout=0)
		self.log('Task : ' + str(name) + ' and params : ' + str(args))
		if('exit' in name):
			self.closeMLSession()
		else:
			numberouts = int(self.engine.nargout(name))
			self.log('outs expected: ' + str(numberouts))
			try:
				if(isinstance(args,str)):
					if("'" in args):
						command = name + '("' + args + '")'
					else:
						command = name + "('" + args + "')"
				else:
					command = name + '(' + ','.join(str(args[x]) for x in args) + ')'
				self.log('Command to use: '+ command)
				self.asyncTask = self.engine.eval(command, nargout=numberouts,background = True)
			except Exception as e:
				print('Error : ' + str(e))
				variables = 'Error'

	def saveOutputsLocally(self,outputsNames):
		''' 
		Attributes
		----------
		name : list
			List of names of the variables generated while running the task, it must contain the exact names used in the task
		'''
		filename = 'LocalOutputs'
		command = 'save({0},{1})'.format(filename,','.join(outputsNames))
		command = 'save(' + filename + ',' +','.join(outputsNames)+')'
		self.engine.eval(command)

	def closeMLSession(self):
		''' Closes a Matlab session using the self.engine or connecting to one
		'''
		if(self.engine is not None):
				self.joinMLSession()
		try:
				self.engine.eval('exit',nargout=0)
		except:
				print('Session Finished')