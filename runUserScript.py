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
				self.outIO = io.StringIO()
				self.errIO = io.StringIO()
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
		
		def _obtainNextPath2Save(self):
			taskID = 0
			path2Save = './TasksResults/Outputs/'+str(taskID)
			while(os.path.isdir(path2Save)):
				path2Save = './TasksResults/Outputs/'+str(taskID)
				taskID = taskID +1
			self.path2Save = path2Save
			os.mkdir(path2Save)
			
		def createMLSession(self):
				P = Popen('nohup python3 matlabEngineLauncher.py > MLSession.log 2>&1 &', shell=True)

		def searchSharedSession(self):
				try:
						return matlab.engine.find_matlab()
				except:
						return None

		def runTask(self,name,args):
				command = 'nohup python3 callTaskAsync.py -t {0} -p {1} -s {2} -d {3} > {3}/MLSession.log 2>&1 &'
				P = Popen(command.format(name,args,self.sessionID,self.path2Save), shell=True)

		def closeMLSession(self):
				if(self.engine is not None):
						self.joinMLSession()
				try:
						self.engine.eval('exit',nargout=0)
				except:
						print('Session Finished')
						
		def killTaskWithID(self,kill):
				fileName = "./TasksResults/Outputs/" + kill + "/kill.txt"
				try:
						file = open(fileName,'x')
				except:
						file = open(fileName,'w')
				datetimestr = datetime.now()
				file.write('Task cancelled at ' + datetimestr.strftime("%X %x"))


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
		#session._obtainNextPath2Save()
		if(task is not None):
			session.runTask(task, params)
			print(session.path2Save)

if __name__ == "__main__":
   main(sys.argv[1:])
