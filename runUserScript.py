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

	def __init__(self,sessionID = None, kill = None):
		if(kill is None):
			self.folderHandler = remoteMatlabFolders()
			self.taskID = self.folderHandler.taskID
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
		
	def createMLSession(self):
		P = Popen('nohup python3.6 matlabEngineLauncher.py > MLSession.log 2>&1 &', shell=True)

	def searchSharedSession(self):
		try:
			return matlab.engine.find_matlab()
		except:
			return None

	def runTask(self,name,args):
		command = 'nohup python3.6 callTaskAsync.py \
		-t {0} -a {1} -s {2} -i {3} -r {4} -p {5} \
		> {5}/log.txt 2>&1 &' 
		#print(command.format(name,args,self.sessionID,self.taskID,self.resultsFolder,self.resultsFolder))
		#print(command.format(name,args,self.sessionID,self.taskID,self.folderHandler.runFolder,self.folderHandler.resultsFolder))
		P = Popen(command.format(name,args,self.sessionID,self.taskID,self.folderHandler.runFolder,self.folderHandler.resultsFolder), shell=True)

	def closeMLSession(self):
		if(self.engine is not None):
			self.joinMLSession()
		try:
			self.engine.eval('exit',nargout=0)
		except:
			print('Session Finished')
					
	def killTaskWithID(self,kill):
		fileName = self.folderHandler.rootRunFolder + self.folderHandler.prefix + kill + "/kill.txt"
		try:
			file = open(fileName,'x')
		except:
			file = open(fileName,'w')
		datetimestr = datetime.now()
		file.write('Task cancelled at ' + datetimestr.strftime("%X %x"))
	
	def locateParamsFile(self,params):
		for files in os.listdir('./'):
			if(params in str(files)):
				return files
		return None
	
	def prepareTask2Run(self,task,params,dynamic = False):
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
