import sys
import getopt
import os
import matlab.engine
import io
import time
from subprocess import PIPE, Popen, STDOUT
from datetime import datetime
import shutil
import zipfile

class remoteMatlabFolders(object):
	"""
	Class to manage the folder creation and file management when running matlab script in the engine

	Attributes
	----------
	dynamic : Whether the script/task answer is expected or not. If false the outputs will be in a file
	preStatus : File tree before running the task
	postStatus : File tree after running the task
	rootRunFolder : './Run/'
	rootResultsFolder : './Results/'
	rootTasksFolder : './Tasks/'
	prefix : String to be at the beginning of the ./Run/ folder
	

	"""
	def __init__(self, taskID = None,dynamic = False):
		self.dynamic = dynamic
		self.preStatus = []
		self.postStatus = []
		self.rootRunFolder = './Run/'
		self.rootResultsFolder = './Results/'
		self.rootTasksFolder = './Tasks/'
		self.prefix = 'ciemat'
		if(taskID is None):
			self.taskID = self._obtainNextPath2Save()
		else:
			self.taskID = taskID
		self.runFolder = self.rootRunFolder+self.prefix+str(self.taskID)
		self.resultsFolder = self.rootResultsFolder+self.prefix+str(self.taskID)
		self.checkCreateFolders()
		self.savePreStatus()
	
	
	def _obtainNextPath2Save(self):
		taskID = 0
		path2Save = self.rootRunFolder+self.prefix+str(taskID)
		while(os.path.isdir(path2Save)):
			taskID = taskID +1
			path2Save = self.rootRunFolder+'ciemat'+str(taskID)
		return taskID
	
	def _createFolders(self):
		self.runFolder = './Run/'+'ciemat'+str(self.taskID)
		self.resultsFolder = './Results/'+'ciemat'+str(self.taskID)
		if(not os.path.isdir(self.runFolder)):
			os.mkdir(self.runFolder)
		if(not os.path.isdir(self.resultsFolder)):
			os.mkdir(self.resultsFolder)
	
	def _makeSymLinks(self,src,dst):
		for root, dirs, files in os.walk(src):
			for adir in dirs:
				newfolder = os.path.join(root,adir).replace(src,dst)
				os.mkdir(newfolder)
			for afile in files:
				newfile = os.path.join(root,afile).replace(src,dst)
				os.symlink(os.path.abspath(os.path.join(root,afile)),os.path.abspath(newfile))
	
	def _createFolder(self,path):
		''' Check and creates a folder if not there
		Attributes
		----------
		path : string
			Path with the folder name included
		'''
		if(not os.path.isdir(path)):
			os.mkdir(path)
	
	def copyInputs(self,params):
		os.symlink(os.path.abspath(params),os.path.abspath(self.runFolder+'/'+params))
	
	def savePreStatus(self):	
			for dirpath,_,filenames in os.walk(self.runFolder):
					for f in filenames:
						self.preStatus.append(os.path.abspath(os.path.join(dirpath, f)))

	def savePostStatus(self):	
			for dirpath,_,filenames in os.walk(self.runFolder):
					for f in filenames:
						self.postStatus.append(os.path.abspath(os.path.join(dirpath, f)))
	
	def copyTasks(self, task):
		self._makeSymLinks(self.rootTasksFolder+task,self.runFolder)
	
	def checkCreateFolders(self):
		''' Creates the three folders that are needed to run matlab tasks
		'''
		self._createFolder(self.rootRunFolder)
		self._createFolder(self.rootResultsFolder)
		self._createFolder(self.rootTasksFolder)
		self._createFolder(self.runFolder)
		self._createFolder(self.resultsFolder)
	
	def moveNewFiles(self):
		self.savePostStatus()
		added = list(set(self.postStatus)-set(self.preStatus))

		for newfile in added:
			dstfile = newfile.replace(os.path.abspath(self.runFolder),os.path.abspath(self.resultsFolder))
			dstfolder = os.path.split(dstfile)[0]
			if not os.path.exists(dstfolder):
				os.makedirs(dstfolder)
			shutil.copy(newfile,dstfile)
			
	def _zipOutputs(self):
		zf = zipfile.ZipFile(self.resultsFolder+"/out.zip", "w")
		for root, dirs, files in os.walk(self.resultsFolder):
			for file in files:
				if(('out.zip' not in file) & ('log.txt' not in file)):
					zf.write(os.path.join(root, file))
					
	def saveIO(self,variables, outStream):
		self.savePostStatus()
		self.moveNewFiles()
		self._saveData(str(variables),'out',self.resultsFolder)
		self._saveData(outStream,'matlabOut',self.resultsFolder)
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
			print('python remoteMatlabFolders -t <taskName> -p <parameters> -k <taskID to kill>')
			sys.exit()
		elif opt in ("-t", "--task"):
			task = arg
		elif opt in ("-p", "--params"):
			params = arg
		elif opt in ("-k", "--kill"):
			kill = arg
					
	session = remoteMatlabFolders()
	session.copyTasks(task)
	session.copyInputs(params)

if __name__ == "__main__":
	main(sys.argv[1:])
	