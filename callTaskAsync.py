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
from remoteMatlabFolders import remoteMatlabFolders

class MatlabTaskCaller(object):

	def __init__(self,taskID, path = None, runpath = None, dynamic = False, sessionID = None, verbose = False):
			self.dynamic = dynamic			
			self.verbose = verbose;
			self.outIO = io.StringIO()
			self.errIO = io.StringIO()
			
			self.folderHandler = remoteMatlabFolders(taskID)
			self.taskID = self.folderHandler.taskID
			self.preStatus = []
			self.postStatus = []
			self.folderHandler.savePreStatus()
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
							print('No shared sessions')
							raise Exception("No shared sessions, last session expired")

	def joinMLSession(self):
		''' Connects to the a Matlab session,
		'''
		try:
				self.engine = matlab.engine.connect_matlab()
		except Exception as e:
				self.log('Not available yet : ' + str(e))
				time.sleep(10)
				self.joinMLSession()
	def searchSharedSession(self):
		''' Looks for a valid running Matlab session in the computer, if present the engine is ready to be used in self.engine
		'''
		try:
			return matlab.engine.find_matlab()
		except:
			return None	
			
	def checkStatus(self):
		''' Reads the status of the current work using the Matlab engine, this method only finishes when the task is completed or canceled (due to error or if the file kill.txt exists)
		'''
		while (not self.asyncTask.done()):
			self.log('Checking and saving status...')
			self.updateStatus('running')
			if(os.path.exists((self.folderHandler.runFolder+'/kill.txt'))):
				self.log('Sending cancel signal to task...')
				self.killTask()
				self.updateStatus('canceled')
				return
			if(self.dynamic):
				time.sleep(0.5)
			else:
				time.sleep(10)
		variables = self.asyncTask.result()
		self.log('Output Variables : ' + str(variables))
		self.engine.close('all')
		self.log('Completed')
		self.updateStatus('completed')
		if(self.dynamic):
			return variables
		else:
			self.log('Saving outputs')
			self.folderHandler.saveIO(variables,self.outIO)
			self.folderHandler._zipOutputs()
			return None

	def updateStatus(self,newStatus):
		''' Stores the actual status in a status file
		Attributes
		----------
		newStatus : string
			New status to be logged in the status.txt file
		'''
		self.folderHandler._saveData(newStatus,'status'+str(self.taskID),'./')

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
				
	def runTask(self,name,args):
		''' Runs a task by its name and using the sent parameters
		Attributes
		----------
		name : string
			name of the task to execute, it must be the exact name of the folder and .m file (/name/name.m) inside the Tasks folder
		args : string or Object
			Path of the file to be used as input or the content of the file
		'''
		if(self.dynamic):
			self.folderHandler.copyTasks(name)
		self.engine.clear(nargout=0)			
		addpath = 'userpath("' + os.path.abspath(str(self.folderHandler.runFolder)) + '")'			
		self.engine.eval(addpath,background = True,nargout=0)
		if('exit' in name):
			self.closeMLSession()
		else:
			self.log(name)
			numberouts = int(self.engine.nargout(name))
			self.log('outs expected: ' + str(numberouts))
			try:
				self.asyncTask = self.engine.feval(name,args, nargout=numberouts,stdout=self.outIO,stderr=self.errIO,background = True)
			except Exception as e:
				self.log('Error : ' + str(e))
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
		if(self.verbose):
			datetimestr = datetime.now()
			print('[' + datetimestr.strftime("%X %x") + '] : ' + data)


def main(argv):
	ON_POSIX = 'posix' in sys.builtin_module_names
	sessionID = None
	verbose = True
	taskID = None
	path = None
	try:
			opts, args = getopt.getopt(argv,"ht:a:s:v:i:p:r:",["task=","args=","session=","verbose=","taskID=","path=","runF="])
	except getopt.GetoptError:
			sys.exit(2)
	for opt, arg in opts:
			if opt == '-h':
					print('python callTaskAsync -t <taskName> -a <args> -s <sessionID> -v <verbose> -i <taskID> -p <path> -r <runFolder>')
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
			elif opt in ("-p", "--path"):
					savepath = arg
			elif opt in ("-r", "--runF"):
					runpath = arg
	
	session = MatlabTaskCaller(taskID = taskID, path = savepath, runpath = runpath, sessionID = sessionID, verbose = verbose)
	#session = MatlabTaskCaller(taskID = taskID, savepath, runpath,sessionID,verbose)
	session.log('Task : ' + str(task) + ' and params : ' + str(params))
	session.runTask(task, params)
	session.checkStatus()

if __name__ == "__main__":
	main(sys.argv[1:])
