import sys
import getopt
import os
import matlab.engine
import io
import time
from subprocess import PIPE, Popen, STDOUT
from datetime import datetime
from remoteMatlabFolders import remoteMatlabFolders

class MatlabSessionLauncher(object):
	"""
	Class to call MatlabTaskCaller (see callTaskAsync.py) in a diferent process or to kill a running one. This class prepares the system to be used when the task is called. If there is no matlab session active, this class will run matlabEngineLauncher.py to create one. 

	Attributes
	----------
	folderHandler : Handles the creation, inspection, updating and deleting of files (see remoteMatlabFolders.py)
	taskID: Integer that identifies the running task
	sessionID: Code that identifies the Matlab session that is running in the computer
	
	Methods
	----------
	createMLSession: Is a static method that can be used to start a Matlab session
	runTask : Calls MatlabTaskCaller (see callTaskAsync.py) in a diferent process with the name and arguments of the task. There will be no return of values. 
	searchSharedSession: Is a static method to look for a started Matlab session
	closeMLSession: Connect to a known Matlab session to call the "exit" method of matlab
	killTaskWithID: Kills a task or script running in the background using its ID
	"""

	def __init__(self,sessionID = None, kill = None):
		if(kill is None):
			self.folderHandler = remoteMatlabFolders()
			self.taskID = self.folderHandler.taskID
			self.folderHandler.checkCreateFolders()
		else:
			self.folderHandler = remoteMatlabFolders(taskID = kill)
			self.taskID = self.folderHandler.taskID
		if(sessionID is not None):
			self.sessionID = sessionID
		else:
			if(kill is not None):
				self.killTaskWithID(kill)
			else:
				availableSessions = self.searchSharedSession()
				if(len(availableSessions)>0):
					self.sessionID = availableSessions[0]
				else:
					self.createMLSession();
					self.sessionID = None
	
	@staticmethod
	def createMLSession():
		''' Calls to matlabEngineLauncher.py to start a new Matlab session in the background
		'''
		P = Popen('nohup python3.6 matlabEngineLauncher.py > MLSession.log 2>&1 &', shell=True)

	@staticmethod
	def searchSharedSession():
		''' Looks for a valid running Matlab session in the computer, if present the engine is ready to be used in self.engine
		'''
		try:
			return matlab.engine.find_matlab()
		except:
			return None

	def runTask(self,name,args):
		''' Calls to callTaskAsync.py to run a task or script in the background
		Attributes
		----------
		name : string
			name of the task to execute, it must be the exact name of the folder and .m file (/name/name.m) inside the Tasks folder
		args : string or Object
			Path of the file to be used as input or the content of the file
		'''
		command = 'nohup python3.6 callTaskAsync.py \
		-t {0} -a {1} -s {2} -i {3} > {4}/log.txt 2>&1 &' 
		#print(command.format(name,args,self.sessionID,self.taskID,self.folderHandler.resultsFolder))
		P = Popen(command.format(name,args,self.sessionID,self.taskID,self.folderHandler.resultsFolder), shell=True)

	def closeMLSession(self):
		''' Closes a Matlab session using the self.engine or connecting to one
		'''
		if(self.engine is not None):
			self.joinMLSession()
		try:
			self.engine.eval('exit',nargout=0)
		except:
			print('Session Finished')
					
	def killTaskWithID(self,kill):
		''' Kills a task or script running in the background using its ID (an integer number)
		Attributes
		----------
		kill : string or number
			ID of the task to kill
		'''
		fileName = self.folderHandler.rootRunFolder + self.folderHandler.prefix + str(kill) + "/kill.txt"
		try:
			file = open(fileName,'x')
		except:
			file = open(fileName,'w')
		datetimestr = datetime.now()
		file.write('Task cancelled at ' + datetimestr.strftime("%X %x"))
	
	def locateParamsFile(self,params):
		''' Locates the input file in the local folder and returns the path
		Attributes
		----------
		params : string
			Complete name or prefix to identify an input file
		'''
		for files in os.listdir('./'):
			if(params in str(files)):
				return files
		return None
	
	def prepareTask2Run(self,task,params,dynamic = False):
		''' Prepares a task or script to be executed, locates param file and prepares the folders
		Attributes
		----------
		params : string
			Complete name or prefix to identify an input file
		'''
		if(dynamic):
			params = self.locateParamsFile(params)			
		self.folderHandler.copyTasks(task)
		self.folderHandler.copyInputs(params)

def main(argv):
	ON_POSIX = 'posix' in sys.builtin_module_names
	task = None
	params = None
	kill = None
	try:
		opts, args = getopt.getopt(argv,"ht:p:k:",["task=","params=","kill="])
	except getopt.GetoptError:
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print('python connectToMatlabSession -t <taskName> -p <parameters> -k <taskID to kill>')
			sys.exit()
		elif opt in ("-t", "--task"):
			task = arg
		elif opt in ("-p", "--params"):
			params = arg
		elif opt in ("-k", "--kill"):
			kill = arg
					
	session = MatlabSessionLauncher(kill = kill)
	if(task is not None):
		session.prepareTask2Run(task,params)
		session.runTask(task, params)
		print(session.taskID)

if __name__ == "__main__":
	main(sys.argv[1:])
