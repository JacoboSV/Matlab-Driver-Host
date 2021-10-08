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

class remoteFolders(object):
	"""
	Class to manage the folder creation and file management when running a script remotely

	Attributes
	----------
	preStatus : File tree before running the task
	postStatus : File tree after running the task
	rootRunFolder : './Run/'
	rootResultsFolder : './Results/'
	rootTasksFolder : './Tasks/'
	prefix : String to be at the beginning of the ./Run/ folder
	taskID: Integer that identifies the running task

	"""
	def __init__(self, taskID = None):
		self.preStatus = []
		self.postStatus = []
		self.rootRunFolder = './Run/'
		self.rootResultsFolder = './Results/'
		self.rootTasksFolder = './Tasks/'
		self.rootTempFolder = './Temp/'
		self.prefix = 'ciemat'
		if(taskID is None):
			self.taskID = self._obtainNextPath2Save()
		else:
			self.taskID = taskID
		self.runFolder = self.rootRunFolder+self.prefix+str(self.taskID)
		self.resultsFolder = self.rootResultsFolder+self.prefix+str(self.taskID)
	
	def setRunFolder(self,newRunFolder):
		self.runFolder = newRunFolder
		
	def setResultsFolder(self,newResultsFolder):
		self.resultsFolder = newResultsFolder
	
	def get_input_format_path(self,task):
		return self.runFolder+'/inputformat.txt'
		
	def get_output_format_path(self,task):
		return self.runFolder+'/outputformat.txt'

	def locateParamsFile(self,params):
		''' Locates the input file in the local folder and returns the path
		Attributes
		----------
		params : string
			Complete name or prefix to identify an input file
		'''
		temporalFolder = os.path.abspath(self.rootTempFolder)
		#print(temporalFolder)
		for files in os.listdir(temporalFolder):
			if(params in str(files)):
				return os.path.abspath(os.path.join(temporalFolder,files))
		#If not there, try in the main folder
		for files in os.listdir('./'):
			if(params in str(files)):
				return os.path.abspath(os.path.join('./',files))
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
		os.symlink(params,os.path.abspath(self.runFolder+'/'+os.path.basename(params)))
	
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
		added = self.getNewFilesPath()

		for newfile in added:
			dstfile = newfile.replace(os.path.abspath(self.runFolder),os.path.abspath(self.resultsFolder))
			dstfolder = os.path.split(dstfile)[0]
			if not os.path.exists(dstfolder):
				os.makedirs(dstfolder)
			if(newfile != dstfile):
				shutil.copy(newfile,dstfile)
	
	def cleanTempFiles(self):
		os.remove('status'+str(self.taskID)+'.txt')
	
	def getNewFilesPath(self):
		added = list(set(self.postStatus)-set(self.preStatus))
		return added
	
	def getNewFilesPathSize(self):
		added = self.getNewFilesPath()
		sizes =[]
		outFile = os.path.abspath(os.path.join(self.resultsFolder, './out.txt'))
		stdoutFile = os.path.abspath(os.path.join(self.resultsFolder, './Script stdout.txt'))
		added.append(outFile)
		added.append(stdoutFile)
		for fil in added:
			sizes.append(os.path.getsize(fil))
			#print("File: " + str(fil) + ", with size: " + str(os.path.getsize(fil)))
		return {"names": added, "sizes": sizes}

			
	def removeNewFiles(self):
		''' Compares the status before and after the execution to check if new files are created, all the new files are copied to the results folder.
		'''
		added = self.getNewFilesPath()
		for newfile in added:
			dstfile = newfile.replace(os.path.abspath(self.runFolder),os.path.abspath(self.resultsFolder))
			os.remove(newfile)
		os.remove(self.zippedFile)
		os.remove('status'+str(self.taskID)+'.txt')
	
	def _zipNewFiles(self,where):
		added = self.getNewFilesPath()
		filepath = where+"/out.zip"
		zf = zipfile.ZipFile(filepath, "w")
		for newfile in added:
			zf.write(newfile,os.path.basename(newfile))
		self.zippedFile = filepath
		return filepath
	
	def _zipOutputs(self,where=None, keepFolderTree = False):
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
					if(keepFolderTree):
						zf.write(os.path.join(root, file),file)
					else:
						zf.write(os.path.join(root, file),os.path.basename(file))
		self.zippedFile = filepath
		return filepath
	
	def serializeFile(self,filepath):
		with open(filepath, 'rb') as f:
			data = base64.b64encode(f.read())
		datastring = data.decode('utf-8')
		return datastring
					
	def saveIO(self,variables, outStream):
		''' Saves all the new data, outputs and variables after the execution of the script/task
		Attributes
		----------
		variables : object
			The object that is returned by the task
		outStream : io.StringIO
			Object containing all the outputs of the stdout pipe
		'''
		self.moveNewFiles()
		self.saveData(str(variables),'out',self.resultsFolder)
		self.saveData(outStream,'Script stdout',self.resultsFolder)

	def saveData(self,data,name,path2save):
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
