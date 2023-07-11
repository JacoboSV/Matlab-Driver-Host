import os
import matlab.engine
import time
import json
import traceback

from .mltools.runUserScript import sessionLauncher
from .TaskCaller import TaskCaller
from .utils.taskCreator_Matlab import TaskCreator

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
	def __init__(self,taskID, nodeInfo, bdnodeInfo, sessionID = None, verbose = True):
		self.language = 'matlab'
		super().__init__(taskID, nodeInfo, bdnodeInfo)
		self.sessionManager(sessionID)
		
	def joinMLSession(self, session = None):
		''' Connects to the a Matlab session,
		'''
		try:
			self.log('Trying to connect to: {0}'.format(session))
			self.engine = matlab.engine.connect_matlab(session)
		except Exception as e:
			self.log('Not available yet : ' + str(e))
			time.sleep(1)
			self.joinMLSession()
	
	@staticmethod
	def searchSharedSession():
		''' Looks for a valid running Matlab session in the computer, if present the engine is ready to be used in self.engine
		'''
		try:
			return matlab.engine.find_matlab()
		except:
			return None	

	def checkStatus(self, data=None, isError = False):
		''' Reads the status of the current work using the Matlab engine, this method only finishes when the task is completed or canceled (due to error or if the file kill.txt exists)
		'''
		if(not isError):
			checkCounter = 10
			while (not self.asyncTask.done()):
				checkCounter = checkCounter + 1
				if(checkCounter>10):
					self.log('Checking and saving status...')
					checkCounter = 0
				self.updateStatus('running')
				if(os.path.exists((self.getRunFolder()+'/kill.txt'))):
					self.log('Sending cancel signal to task...')
					self.killTask()
					self.updateStatus('Canceled')
					return
				time.sleep(0.1)
				self.updateStatus('Completed')
				variables = self.asyncTask.result()
				
		else:
			self.updateStatus('Completed with errors')
			variables = data
		
		# print("variables :", variables)
		if(not isinstance(variables, dict)):
			variables = json.loads(variables)
			self.log(str(variables))
		outputsNames = {}
		self.log("Expected Outputs to recover from Node: {0}".format(self.expectedOuts))
		for counter, key in enumerate(self.expectedOuts):
			try:
				outslength = len(variables.get('output'))
			except:
				outslength = -1
			if(outslength == len(self.expectedOuts)):
				outputsNames[key] = variables.get('output')[counter]
			else:
				outputsNames[key] = variables.get('output')
		# print("outputsNames: ", outputsNames)
		
		variables['output'] = outputsNames
		self.saveOutputsLocally(variables)

		self.engine.close('all')
		self.log('Saving outputs')
		# if(self.dynamic):
		self.savePostStatus()
		self.saveIO(variables)
		outputs = self.formatOutputs(variables)
		# self.engine.quit()
		return outputs
		# else:
		# 	self.folderHandler.savePostStatus()
		# 	self.folderHandler.saveIO(variables,self.outIO)
		# 	self.folderHandler._zipOutputs(keepFolderTree = True)
		# 	return None

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
				

	def sessionManager(self,sessionID):
		if(sessionID is not None):
				self.log('Session selected by user')
				self.sessionID = sessionID
				self.joinMLSession()
		else:
				self.log('Searching for sessions')
				availableSessions = self.searchSharedSession()
				if(len(availableSessions) > 0):
						self.sessionID = availableSessions[0]
						self.joinMLSession(self.sessionID)
				else:
						self.log('No sessions')
						sessionLauncher.createMLSession()
						while(self.searchSharedSession() is None):
							time.sleep(1)
							self.sessionID = self.searchSharedSession()[0]
						self.joinMLSession() 

	def runTask(self,args):
		''' Runs a task by its name and using the sent parameters
		Attributes
		----------
		name : string
			name of the task to execute, it must be the exact name of the folder and .m file (/name/name.m) inside the Tasks folder
		args : string or Object
			Path of the file to be used as input or the content of the file
		'''
		self.updateStatus('Started')
		# self.expectedOuts = expectedOuts
		# TO DO: poner esto como opcional en funci�n del quien sea el usuario anterior y demas. Si es una tarea diferente no la mando me espero, si es la misma del mismo usuario. 
		# Podr�a lanzarse un engine por usuario? Pensarlo.
		# Una solucion: Las tareas seran unicas (de unica ejecucion) o de ejecucion mantenida (QUe pueden usar el mismo workspace). Si es de tipo �nico se borra antes y despues.
		# Si es ejecuion mantenida no borra nada
		# Segundo control, mirar si las tareas son del mismo usuario o de otro: Mirar como informar al servidor del usurio 
		#self.engine.clear(nargout=0)
		
		self.updateStatus('Preparing Data')
		self.savePreStatus()

		userpath = os.path.abspath(self.getRunFolder())
		addpath_command = 'userpath("' + userpath  + '")'
		userLibspath_command = 'addpath ' + os.path.abspath(self.getUserLibPath())
		userFilespath_command = 'global user__Data__Path; user__Data__Path = "' + os.path.abspath(self.userDataPath) + '";'
		# self.log('userLibspath_command: {0}'.format(userLibspath_command))
		# self.log('userFilespath_command: {0}'.format(userFilespath_command))
		# self.log('Using user path: {0}'.format(userpath))
		self.engine.eval(addpath_command, background = True, nargout=0)
		self.engine.eval('cd ' + userpath, background = True, nargout=0)
		self.engine.eval(userLibspath_command, background = True, nargout=0)
		self.engine.eval(userFilespath_command, background = True, nargout=0)
		
		for arg in args:
			if(isinstance(args[arg],str)):
				# print("--- Type: str")
				try:
					self.engine.workspace[arg] = eval(args[arg])
				except:
					self.engine.workspace[arg] = args[arg]
			elif(isinstance(args[arg],dict)):
				# print("--- Type: dict")
				args[arg] = json.dumps(args[arg])
				# print("------- Transformed type: {0}".format(type(args[arg])))
				# print("------- Transformed value: {0}".format(args[arg]))
				
				defvar_command = arg + ' = jsondecode(\'' + args[arg] + '\')'
				# print("------- defvar_command: {0}".format(defvar_command))
				self.engine.eval(defvar_command, background = True, nargout=0)
			else:
				# print("--- Type: Other")
				self.engine.workspace[arg] = args[arg]
			# self.engine.eval('disp(' + arg + ')', nargout = 0)
		
		self.log('Task : {0} and params {1}'.format(self.taskName, args))
		if('exit' in self.taskName):
			self.closeMLSession()
		else:
			numberouts = int(self.engine.nargout(self.taskName))
			self.log('Outs expected: {0}'.format(numberouts))
			# args = self.addQuotesToStrings(args)
			try:
				self.log("Args: {0}".format(args))
				command = self.taskName + '(' + ','.join(str(x) for x in args) + ')'
				self.log('Command to use: '+ command)
				
				self.asyncTask = self.engine.eval(command, nargout=numberouts,background = True)
				return self.checkStatus()
			except Exception as e:
				errormsg = 'Error: ' + traceback.format_exc()
				return self.checkStatus(self.errorAnswer(self.expectedOuts, errormsg))

	def checkVarInWorkspace(self,variableName):
		checkvars = 'exist("' + variableName + '")'
		self.log('Checking if ' + str(variableName) + ' exist')
		isdefined = self.engine.eval(checkvars, nargout=1,background = True)
		while (not isdefined.done()):
			time.sleep(0.2)
			self.log('waiting...')
		isVarDef = bool(isdefined.result())
		self.log(' --- ' + variableName + ' exist? ' + str(isVarDef))
		return isVarDef

	def addQuotesToStrings(self,args):
		self.log("args: " + str(args))		
		quoted = []
		# varNames = [str(args[x]) for x in args] 
		# self.log("varNames: " + str(varNames))
		for varname in args:
			if(isinstance(varname,str)):
				isdefined = self.checkVarInWorkspace(varname)
				if(isdefined):
					quoted.append(varname)
				else:
					if("'" in args[varname]):
						quoted.append('"' + str(args[varname]) + '"')
					elif("\"" in args[varname]):
						quoted.append("'" + str(args[varname]) + "'")
					elif(isinstance(args[varname],str)):
						quoted.append("'" + str(args[varname]) + "'")
					else:
						quoted.append(args[varname])
			else:
				quoted.append(args[varname])
		return quoted


	def saveOutputsLocally(self,outputsNames):
		''' 
		Attributes
		----------
		name : list
			List of names of the variables generated while running the task, it must contain the exact names used in the task
		'''
		filename = self.getRunFolder() + '/LocalOutputs.json'
		with open(filename, 'w') as f:
			json.dump(outputsNames,f)

	def closeMLSession(self):
		''' Closes a Matlab session using the self.engine or connecting to one
		'''
		if(self.engine is not None):
				self.joinMLSession()
		try:
				self.engine.eval('exit',nargout=0)
		except:
				self.log('Session Finished')

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
