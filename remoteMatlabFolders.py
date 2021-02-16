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
		''' Looks for a valid name to a new run folder
		Attributes
		----------
		src : string
			Path with the source folder
		dst : string
			Path to the destination folder
		'''
		taskID = 0
		path2Save = self.rootRunFolder+self.prefix+str(taskID)
		while(os.path.isdir(path2Save)):
			taskID = taskID +1
			path2Save = self.rootRunFolder+'ciemat'+str(taskID)
		return taskID
	
	# def _createFolders(self):
		
		# self.runFolder = './Run/'+'ciemat'+str(self.taskID)
		# self.resultsFolder = './Results/'+'ciemat'+str(self.taskID)
		# if(not os.path.isdir(self.runFolder)):
			# os.mkdir(self.runFolder)
		# if(not os.path.isdir(self.resultsFolder)):
			# os.mkdir(self.resultsFolder)
	
	def _makeSymLinks(self,src,dst):
		''' Makes symbolic links to all the original files in the source folder
		Attributes
		----------
		src : string
			Path with the source folder
		dst : string
			Path to the destination folder
		'''
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
		''' Creates symbolic link to the input files in the folder in <rootTasksFolder>
		Attributes
		----------
		params : string
			Path to the input file
		'''
		os.symlink(os.path.abspath(params),os.path.abspath(self.runFolder+'/'+params))
	
	def savePreStatus(self):
		''' Makes a copy of the folder tree structure in the <runFolder> to check if something changes
		'''
		for dirpath,_,filenames in os.walk(self.runFolder):
				for f in filenames:
					self.preStatus.append(os.path.abspath(os.path.join(dirpath, f)))

	def savePostStatus(self):
		''' Makes a copy of the folder tree structure in the <runFolder> to check if something changes
		'''
		for dirpath,_,filenames in os.walk(self.runFolder):
				for f in filenames:
					self.postStatus.append(os.path.abspath(os.path.join(dirpath, f)))
	
	def copyTasks(self, task):
		''' Creates symbolic links to the task files in the folder in <rootTasksFolder>
		----------
		task : string
			Name of the task or script to be executed
		'''
		self._makeSymLinks(self.rootTasksFolder+task,self.runFolder)
	
	def checkCreateFolders(self):
		''' Create the main folders needed to run the scripts and store outputs
		'''
		self._createFolder(self.rootRunFolder)
		self._createFolder(self.rootResultsFolder)
		self._createFolder(self.rootTasksFolder)
		self._createFolder(self.runFolder)
		self._createFolder(self.resultsFolder)
	
	def moveNewFiles(self):
		''' Compares the status before and after the execution to check if new files are created, all the new files are copied to the results folder.
		'''
		self.savePostStatus()
		added = list(set(self.postStatus)-set(self.preStatus))

		for newfile in added:
			dstfile = newfile.replace(os.path.abspath(self.runFolder),os.path.abspath(self.resultsFolder))
			dstfolder = os.path.split(dstfile)[0]
			if not os.path.exists(dstfolder):
				os.makedirs(dstfolder)
			shutil.copy(newfile,dstfile)
			
	def _zipOutputs(self):
		''' Create a zip with all the files and folders inside the results folder
		'''
		zf = zipfile.ZipFile(self.resultsFolder+"/out.zip", "w")
		for root, dirs, files in os.walk(self.resultsFolder):
			for file in files:
				if(('out.zip' not in file) & ('log.txt' not in file)):
					zf.write(os.path.join(root, file))
					
	def saveIO(self,variables, outStream):
		''' Saves all the new data, outputs and variables after the execution of the script/task
		Attributes
		----------
		variables : object
			The object that is returned by matlab engine
		outStream : io.StringIO
			Object containing all the outputs of the stdout pipe
		'''
		self.savePostStatus()
		self.moveNewFiles()
		self._saveData(str(variables),'out',self.resultsFolder)
		self._saveData(outStream,'matlabOut',self.resultsFolder)
		#self._saveData(self.errIO,'errors',self.path2Save)

	def _saveData(self,data,name,path2save):
		''' Saves in files the information in data as <path2save>/name.txt
		----------
		data : string or io.StringIO
			The data to be saved
		name : string
			Name of the file to be saved
		path2save : string
			Pâth where the file must be stored, can be relative or absolute
		'''
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
	