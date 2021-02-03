import sys
import getopt
import os
import matlab.engine
import io
import time
from subprocess import PIPE, Popen, STDOUT
from datetime import datetime

class MatlabSessionLauncher(object):

	def __init__(self,sessionID = None, kill = None):
		self.runFolder = './Run/'
		self.resultsFolder = './Results/'
		self.tasksFolder = './Tasks/'
		if(sessionID is not None):
			#print('Session defined')
			self.sessionID = sessionID
			self._obtainNextPath2Save()
		else:
			if(kill is not None):
				self.killTaskWithID(kill)
			else:
				#print('Searching for sessions')
				availableSessions = self.searchSharedSession()
				if(len(availableSessions)>0):
					#print('There are sessions')
					self.sessionID = availableSessions[0]
					self._obtainNextPath2Save()
				else:
					#print('No shared sessions, creating one')
					self.createMLSession();
					self.sessionID = None
					self._obtainNextPath2Save()
		
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
		P = Popen(command.format(name,args,self.sessionID,self.taskID,self.runFolder,self.resultsFolder), shell=True)

	def closeMLSession(self):
		if(self.engine is not None):
			self.joinMLSession()
		try:
			self.engine.eval('exit',nargout=0)
		except:
			print('Session Finished')
					
	def killTaskWithID(self,kill):
		fileName = self.runFolder + kill + "/kill.txt"
		try:
			file = open(fileName,'x')
		except:
			file = open(fileName,'w')
		datetimestr = datetime.now()
		file.write('Task cancelled at ' + datetimestr.strftime("%X %x"))
	
	def locateParamsFile(self,params):
		#print(params)
		for files in os.listdir('./'):
			#print(files)
			if(params in str(files)):
				#print(files)
				return files
		return None
	
	def _obtainNextPath2Save(self):
		taskID = 0
		path2Save = self.runFolder+'ciemat'+str(taskID)
		while(os.path.isdir(path2Save)):
			taskID = taskID +1
			path2Save = self.runFolder+'ciemat'+str(taskID)
		self.taskID = taskID
	
	def _createFolders(self):
		self.runFolder = './Run/'+'ciemat'+str(self.taskID)
		self.resultsFolder = './Results/'+'ciemat'+str(self.taskID)
		if(not os.path.isdir(self.runFolder)):
			os.mkdir(self.runFolder)
		if(not os.path.isdir(self.resultsFolder)):
			os.mkdir(self.resultsFolder)
	
	def _makeSymLinks(self,src,dst):
		#src = self.tasksFolder+task
		#dst = self.runFolder
		for root, dirs, files in os.walk(src):
			for file in files:
				newfile = os.path.join(root,file).replace(src,dst)
				os.symlink(os.path.join(root,file),newfile)
				print(newfile)
				print(os.path.join(root,file))
			for dir in dirs:
				os.mkdir(dst+dir)
	
	def copyTasks(self, task):
		self._makeSymLinks(self.tasksFolder+task,self.runFolder)
		
	def copyInputs(self,params):
		os.symlink(params,self.runFolder+'/'+params)
	
	def prepareTask2Run(self,task,params):
		self._createFolders()
		self.copyTasks(task)
		self.copyInputs(params)
			
				

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
	params = str(session.locateParamsFile(params))
	#session._obtainNextPath2Save()
	if(task is not None):
		session.prepareTask2Run(task,params)
		session.runTask(task, params)
		print(session.taskID)

if __name__ == "__main__":
	main(sys.argv[1:])

