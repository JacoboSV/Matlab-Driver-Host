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

class MatlabTaskCaller(object):

	def __init__(self,dir,sessionID = None, verbose = False):
			self.verbose = verbose;
			self.outIO = io.StringIO()
			self.errIO = io.StringIO()
			self.path2Save = dir
			if(sessionID is not None):
					if self.verbose : print('Session defined')
					self.sessionID = sessionID
					self.joinMLSession()
			else:
					if self.verbose : print('Searching for sessions')
					availableSessions = self.searchSharedSession()
					if(len(availableSessions)>0):
							if self.verbose : print('There are sessions')
							self.sessionID = availableSessions[0]
							self.joinMLSession()
					else:
							print('No shared sessions')
							raise Exception("No shared sessions, last session expired")
			if(not os.path.exists(self.path2Save)):
					os.mkdir(self.path2Save)

	def _zipOutputs(self):
			filePaths = self._retrieve_file_paths(self.path2save)
			for fileName in filePaths:
					# writing files to a zipfile
					zip_file = zipfile.ZipFile(self.path2save+'/out'+'.zip', 'w')
					with zip_file:
							# writing each file one by one
							for file in filePaths:
									zip_file.write(file)

	def _retrieve_file_paths(self,dirName):
			filePaths = []
			# Read all directory, subdirectories and file lists
			for root, directories, files in os.walk(dirName):
					for filename in files:
							# Create the full filepath by using os module.
							filePath = os.path.join(root, filename)
							filePaths.append(filePath)
			return filePaths

	def joinMLSession(self):
			try:
					self.engine = matlab.engine.connect_matlab()
			except Exception as e:
					if self.verbose : print('Not available yet : ' + str(e))
					time.sleep(10)
					self.joinMLSession()
					
	def checkStatus(self):
		while (not self.asyncTask.done()):
			if self.verbose : print('Checking and saving status...')
			time.sleep(10)
			self._saveData('Running','status',self.path2Save)
			if(os.path.exists((self.path2Save+'/kill.txt'))):
				if self.verbose : print('Sending cancel signal to task...')
				self.killTask()
				self._saveData('Cancelled','status',self.path2Save)
				return
		variables = self.asyncTask.result()
		if self.verbose : print('Completed')
		self._saveData('Finished','status',self.path2Save)
		session.saveIO()

	def killTask(self):
		while(not self.asyncTask.cancelled()):
			try:
				self.asyncTask.cancel()
			except Exception as e:
				print('Task cannot be cancelled, due to error :')
				print(str(e))
		if self.verbose : print('User cancelled the task')
				
	def runTask(self,name,args):
			if('exit' in name):
				self.closeMLSession()
			else:
				if self.verbose : print(name)
				#Obtain the number of outputs of a given script or funtion
				numberouts = int(self.engine.nargout(name))
				if self.verbose : print('outs expected: ' + str(numberouts))
				#Call funtion by name and redirect stdout and stderr			  
				try:
					self.asyncTask = self.engine.feval(name,args, nargout=numberouts,stdout=self.outIO,stderr=self.errIO,background = True)
				except Exception as e:
					print('Error : ' + str(e))
					variables = 'Error'

	def saveIO(self):
			if self.verbose : print('Saving outputs')
			self._saveData(self.outIO,'out',self.path2Save)
			self._saveData(self.errIO,'log',self.path2Save)

	def _saveData(self,data,name,path2save):
			#if self.verbose : print('Saving Info...')
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


def main(argv):
	ON_POSIX = 'posix' in sys.builtin_module_names
	sessionID = None
	verbose = True
	try:
			opts, args = getopt.getopt(argv,"ht:p:s:v:d:",["task=","params=","session=","verbose="])
	except getopt.GetoptError:
			sys.exit(2)
	for opt, arg in opts:
			if opt == '-h':
					print('python callTaskAsync -t <taskName> -p <parameters> -s <sessionID> -v <verbose>')
					sys.exit()
			elif opt in ("-t", "--task"):
					task = arg
			elif opt in ("-p", "--params"):
					params = arg
			elif opt in ("-s", "--session"):
					sessionID = arg
			elif opt in ("-v", "--verbose"):
					verbose = arg
			elif opt in ("-d", "--dir"):
					dir = arg
	
	session = MatlabTaskCaller(dir,sessionID,verbose)
	if verbose : print(session.sessionID)
	#time.sleep(10)
	#time.sleep(10)
	session.runTask(task, params)
	session.checkStatus()

#future = matlab.engine.connect_matlab(background=True)
#eng = future.result()
#t,m = eng.maximumFile('ins.txt',nargout=2)
#eng.quit()
if __name__ == "__main__":
   main(sys.argv[1:])

