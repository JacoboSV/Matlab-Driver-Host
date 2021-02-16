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

class MatlabTaskCaller(object):

	def __init__(self,taskID, path = None, runpath = None, dynamic = False, sessionID = None, verbose = False):
			#print(dynamic)
			self.dynamic = dynamic			
			self.verbose = verbose;
			self.outIO = io.StringIO()
			self.errIO = io.StringIO()
			self.tasksFolder = './Tasks/'
			random.seed(datetime.now())	
			date = random.randint(1,1000)
			if(path is not None):
				self.path2Save = path
			else:
				self.path2Save = './Results/'+'ciemat'+str(date)
				if(not os.path.isdir(self.path2Save)):
					os.mkdir(self.path2Save)
			if(runpath is not None):
				self.runPath = runpath
				#self.runFolder = runpath
			else:
				self.runPath = './Run/'+'ciemat'+str(date)
				if(not os.path.isdir(self.runPath)):
					os.mkdir(self.runPath)
			if(self.dynamic):
				self.taskID = taskID
			else:
				self.taskID = str(date)
			self.preStatus = []
			self.postStatus = []
			self.savePreStatus()
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
			if(not os.path.exists(self.path2Save)):
					os.mkdir(self.path2Save)

	def _zipOutputs(self):
			zf = zipfile.ZipFile(self.path2Save+"/out.zip", "w")
			for root, dirs, files in os.walk(self.path2Save):
				for file in files:
					if(('out.zip' not in file) & ('log.txt' not in file)):
						zf.write(os.path.join(root, file))

	def copyTasks(self, task):
		self._makeSymLinks(self.tasksFolder+task,self.runPath)

	def _makeSymLinks(self,src,dst):
		for root, dirs, files in os.walk(src):
			for adir in dirs:
				newfolder = os.path.join(root,adir).replace(src,dst)
				os.mkdir(newfolder)
			for afile in files:
				newfile = os.path.join(root,afile).replace(src,dst)
				os.symlink(os.path.abspath(os.path.join(root,afile)),os.path.abspath(newfile))

	def joinMLSession(self):
			try:
					self.engine = matlab.engine.connect_matlab()
			except Exception as e:
					self.log('Not available yet : ' + str(e))
					time.sleep(10)
					self.joinMLSession()
	def searchSharedSession(self):
		try:
			return matlab.engine.find_matlab()
		except:
			return None	
			
	def checkStatus(self):
		while (not self.asyncTask.done()):
			self.log('Checking and saving status...')
			if(self.dynamic):
				time.sleep(0.5)
			else:
				time.sleep(10)
			self.updateStatus('running')
			if(os.path.exists((self.path2Save+'/kill.txt'))):
				self.log('Sending cancel signal to task...')
				self.killTask()
				#self._saveData('Cancelled','status',self.path2Save)
				self.updateStatus('canceled')										
				return
		variables = self.asyncTask.result()
		#self.engine.save('vars',nargout=0)
		self.log('Output Variables : ' + str(variables))
		self.engine.close('all')
		self.log('Completed')
		#self._saveData('Finished','status',self.path2Save)
		self.updateStatus('completed')		
		if(self.dynamic):
			return variables		
		else:
			self.saveIO(variables)
			self._zipOutputs()
			return None

	def updateStatus(self,newStatus):
		self._saveData(newStatus,'status'+str(self.taskID),'./')

	def killTask(self):
		while(not self.asyncTask.cancelled()):
			try:
				self.asyncTask.cancel()
			except Exception as e:
				print('Task cannot be cancelled, due to error :')
				print(str(e))
		self.log('User cancelled the task')
				
	def runTask(self,name,args):
			if(self.dynamic):
				self.copyTasks(name)
			self.engine.clear(nargout=0)			
			addpath = 'userpath("' + os.path.abspath(str(self.runPath)) + '")'			
			self.engine.eval(addpath,background = True,nargout=0)
			if('exit' in name):
				self.closeMLSession()
			else:
				self.log(name)
				#Obtain the number of outputs of a given script or funtion
				numberouts = int(self.engine.nargout(name))
				self.log('outs expected: ' + str(numberouts))
				#Call funtion by name and redirect stdout and stderr			  
				try:
					self.asyncTask = self.engine.feval(name,args, nargout=numberouts,stdout=self.outIO,stderr=self.errIO,background = True)
				except Exception as e:
					print('Error : ' + str(e))
					variables = 'Error'

	def saveIO(self,variables):
			self.savePostStatus()
			self.moveNewFiles()
			self.log('Saving outputs')
			self._saveData(str(variables),'out',self.path2Save)
			self._saveData(self.outIO,'matlabOut',self.path2Save)
			#self._saveData(self.errIO,'errors',self.path2Save)

	def _saveData(self,data,name,path2save):
			#self.log('Saving Info...')
			fileName = path2save + "/" + name + ".txt"
			try:
					file = open(fileName,'x')
			except:
					file = open(fileName,'w')
			if(not isinstance(data, str)):
				dataread  = data.getvalue()
				file.write(dataread)
			else:
				file.write(data)

	def closeMLSession(self):
			if(self.engine is not None):
					self.joinMLSession()
			try:
					self.engine.eval('exit',nargout=0)
			except:
					print('Session Finished')
	
	def savePreStatus(self):	
			#print(self.runPath)
			for dirpath,_,filenames in os.walk(self.runPath):
					for f in filenames:
						self.preStatus.append(os.path.abspath(os.path.join(dirpath, f)))
			#print(str(self.preStatus))

	def savePostStatus(self):	
			for dirpath,_,filenames in os.walk(self.runPath):
					for f in filenames:
						self.postStatus.append(os.path.abspath(os.path.join(dirpath, f)))

	def moveNewFiles(self):
			self.savePostStatus()
			added = list(set(self.postStatus)-set(self.preStatus))

			for newfile in added:
				dstfile = newfile.replace(os.path.abspath(self.runPath),os.path.abspath(self.path2Save))
				dstfolder = os.path.split(dstfile)[0]		
				if not os.path.exists(dstfolder):
					os.makedirs(dstfolder)
				shutil.copy(newfile,dstfile)

	def log(self,data):
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
