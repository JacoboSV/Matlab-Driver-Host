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
import json
import ast
import base64

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
	taskID: Integer that identifies the running task

	"""
	def __init__(self, taskID = None,dynamic = False):
		self.dynamic = dynamic
		self.preStatus = []
		self.postStatus = []
		self.rootRunFolder = './Run/'
		self.rootResultsFolder = './Results/'
		self.rootTasksFolder = './Tasks/'
		self.rootTempFolder = './'
		self.prefix = 'ciemat'
		if(taskID is None):
			self.taskID = self._obtainNextPath2Save()
		else:
			self.taskID = taskID
		self.runFolder = self.rootRunFolder+self.prefix+str(self.taskID)
		self.resultsFolder = self.rootResultsFolder+self.prefix+str(self.taskID)
		#if(dynamic):
		#	self.inputformat = self.readInputFormat()
		#self.checkCreateFolders()
	
	def readInputFormat(self,task):
		with open(os.path.join(self.rootTasksFolder,task)+'/inputformat.txt') as json_file:
			self.inputformat = json.load(json_file)
			return self.inputformat
			
	def readOutputFormat(self,task):
		with open(os.path.join(self.rootTasksFolder,task)+'/outputformat.txt') as json_file:
			self.outputformat = json.load(json_file)
			return self.outputformat
			
	#def createInlineCommand(self,task):
	
	# def readMatFile(self,path):
		# in_file = open(path, "rb") # opening for [r]eading as [b]inary
		# data = in_file.read()
		# in_file.close()
		# return data
	
	def populateOutData(self,data):
		self.outputs = self.outputformat
		self.outputs['data'] = data
		return self.outputs
	
	def populateInData(self,data):
		self.inputs = self.inputformat
		self.inputs['data'] = data
		return self.inputs
	
	def createInlineCommand(self,data = None):
		if(data is None):
			data = self.inputs['data']
			dataIn = data.split(',')
			#for i in range(len(dataIn)):
				#dataIn[i] = self._evalTypes(dataIn[i])
			return dataIn

	def createMatFileCommand(self,params=None,task=None):
		#print(params)
		data = params['data']
		name = params['name']
		if(name):
			filename = self.locateParamsFile(name)
		else:
			filename = None
		if(filename is None):
			if(not isinstance(data, bytes)):
				data = self.inputs['data']
			#print(str(data))
			#print(str(task))
			filename = os.path.join(self.rootTasksFolder,task)+'/input_file.mat'
			out_file = open(filename, "wb") # open for [w]riting as [b]inary
			out_file.write(base64.b64decode(data))
			out_file.close()
			return filename
	
	@staticmethod
	def _evalTypes(val):
		try:
			val = ast.literal_eval(val)
		except ValueError:
			pass
		return val

	def locateFile(self,what,where):
		for files in os.listdir(where):
			#print(files)
			if(what in str(files)):
				return os.path.abspath(os.path.join(where,files))
		return None

	def locateParamsFile(self,params):
		''' Locates the input file in the local folder and returns the path
		Attributes
		----------
		params : string
			Complete name or prefix to identify an input file
		'''
		for files in os.listdir(self.rootTempFolder):
			if(params in str(files)):
				return files
		return None

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
				self._createFolder(newfolder)
				#if(os.path.isdir(newfolder)):
				#	os.mkdir(newfolder)
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
	
	def savePreStatus(self,location = None):
		''' Makes a copy of the folder tree structure in the <runFolder> to check if something changes
		'''
		if(location is None):
			location = self.runFolder
		for dirpath,_,filenames in os.walk(location):
				for f in filenames:
					self.preStatus.append(os.path.abspath(os.path.join(dirpath, f)))

	def savePostStatus(self, location = None):
		''' Makes a copy of the folder tree structure in the <runFolder> to check if something changes
		'''
		if(location is None):
			location = self.runFolder
		for dirpath,_,filenames in os.walk(location):
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
		added = list(set(self.postStatus)-set(self.preStatus))

		for newfile in added:
			dstfile = newfile.replace(os.path.abspath(self.runFolder),os.path.abspath(self.resultsFolder))
			dstfolder = os.path.split(dstfile)[0]
			if not os.path.exists(dstfolder):
				os.makedirs(dstfolder)
			shutil.copy(newfile,dstfile)
			
	def removeNewFiles(self):
		''' Compares the status before and after the execution to check if new files are created, all the new files are copied to the results folder.
		'''
		added = list(set(self.postStatus)-set(self.preStatus))
		for newfile in added:
			dstfile = newfile.replace(os.path.abspath(self.runFolder),os.path.abspath(self.resultsFolder))
			os.remove(newfile)
		os.remove(self.zippedFile)
			
	def _zipOutputs(self,where=None):
		''' Create a zip with all the files and folders inside the results folder
		'''
		if(where is None):
			filepath = self.resultsFolder+"/out.zip"
			resultfolder = self.resultsFolder
		else:
			filepath = where+"/out.zip"
			resultfolder = where
		zf = zipfile.ZipFile(filepath, "w")
		for root, dirs, files in os.walk(resultfolder):
			for file in files:
				if(('out.zip' not in file) & ('log.txt' not in file)):
					zf.write(os.path.join(root, file))
		self.zippedFile = filepath
		return filepath
	
	def serializeFile(self,filepath):
		with open(filepath, 'rb') as f:
			data = base64.b64encode(f.read())
		datastring = data.decode('utf-8')
		#in_file = open(filepath, "rb") # opening for [r]eading as [b]inary
		#data = in_file.read()
		#in_file.close()
		return datastring
					
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

# def main(argv):
	# ON_POSIX = 'posix' in sys.builtin_module_names
	# task = None
	# params = None
	# kill = None
	# try:
		# opts, args = getopt.getopt(argv,"ht:p:k:",["task=","params=","kill="])
	# except getopt.GetoptError:
		# sys.exit(2)
	# for opt, arg in opts:
		# if opt == '-h':
			# print('python remoteMatlabFolders -t <taskName> -p <parameters> -k <taskID to kill>')
			# sys.exit()
		# elif opt in ("-t", "--task"):
			# task = arg
		# elif opt in ("-p", "--params"):
			# params = arg
		# elif opt in ("-k", "--kill"):
			# kill = arg
					
	# session = remoteMatlabFolders()
	# session.copyTasks(task)
	# session.copyInputs(params)

# if __name__ == "__main__":
	# main(sys.argv[1:])
	