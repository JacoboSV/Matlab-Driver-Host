import os
import shutil
import zipfile
import base64
import traceback
import datetime

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
	def __init__(self, userDataPath = './', language = 'python'):
		self.preStatus = []
		self.postStatus = []
		self.userDataPath = userDataPath
		self.prefix = 'lab_'
		self.paths = {
			'run'    : './var/run/',
			'results': './var/results/',
			'code'  : './code/',
			'temp'   : './var/temp/',
			'userDataPath'   : userDataPath,
		}
		[self._createFolder(self.paths[p]) for p in self.paths]
		self.taskID = self._obtainNextPath2Save()
		self.runFolder = self.paths['run'] + self.prefix + str(self.taskID)
		self.resultsFolder = self.paths['results'] + self.prefix + str(self.taskID)
		self.user = self.userDataPath.split('_')[0].split('/')[-1]
		if(language == 'python'):
			self.addUserLibsAsPackage()
	
	def setRunFolder(self, newRunFolder):
		self.runFolder = newRunFolder
		
	def setResultsFolder(self, newResultsFolder):
		self.resultsFolder = newResultsFolder

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
		path2Save = self.paths['run'] + self.prefix + str(taskID)
		while(os.path.isdir(path2Save)):
			taskID = taskID + 1
			path2Save = self.paths['run'] + self.prefix + str(taskID)
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
	
	
	def _createFolder(self, path):
		''' Check and creates a folder if not there
		Attributes
		----------
		path : string
			Path with the folder name included
		'''
		if(not os.path.isdir(path)):
			os.makedirs(path)
	
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
	
	def checkCreateFolders(self):
		''' Create the main folders needed to run the scripts and store outputs
		'''
		self._createFolder(self.runFolder)
		self._createFolder(self.resultsFolder)
	
	def moveNewFiles(self):
		''' Compares the status before and after the execution to check if new files are created, all the new files are copied to the results folder.
		'''
		added = self.getNewFilesPath()
		for newfile in added:
			dstfile = newfile.replace(os.path.abspath(self.runFolder), os.path.abspath(self.resultsFolder))
			dstfile2 = newfile.replace(os.path.abspath(self.runFolder), os.path.abspath(self.userDataPath)+ '/ResultsFiles/')
			dstfolder = os.path.split(dstfile)[0]
			dstfolder2 = os.path.split(dstfile2)[0]
			if not os.path.exists(dstfolder):
				os.makedirs(dstfolder)
			if not os.path.exists(dstfolder2):
				os.makedirs(dstfolder2)
			if(newfile != dstfile):
				shutil.copy(newfile,dstfile)
			if(newfile != dstfile2):
				shutil.copy(newfile,dstfile2)
	
	def cleanTempFiles(self):
		'''Remove the status file created during a Node run
		'''
		os.remove('status' + str(self.taskID) + '.txt')
	
	def getNewFilesPath(self):
		added = list(set(self.postStatus) - set(self.preStatus))
		return added
	
	def getNewFilesPathSize(self):
		'''Gets sizes and paths of the new files created during the Node run and includes them inside a dict
		'''
		added = self.getNewFilesPath()
		sizes =[]
		outFile = os.path.abspath(os.path.join(self.resultsFolder, './out.txt'))
		stdoutFile = os.path.abspath(os.path.join(self.resultsFolder, './stdout.txt'))
		added.append(outFile)
		added.append(stdoutFile)
		for fil in added:
			sizes.append(os.path.getsize(fil))
		return {"names": added, "sizes": sizes}


	def addUserLibsAsPackage(self):
		'''Locates libraries in the user path inside the code folder, read all the files inside this path and creates __init__.py files to
		create a loadable package. Finally, the path is added, during run time, to the python path, allowing users to
		 load and call their own functions   
		'''
		self.userLibPath = os.path.abspath(self.paths['code']) + '/userLibraries/{0}/'.format(self.user)
		for folder,_,files in os.walk(self.userLibPath):
			__all__ = [ str(os.path.basename(f)[:-3]) for f in files if '.py' in f]
			if(__all__):
				newfile = open(folder + '/' + '__init__.py','w')
				line = '__all__ = {0}'.format(__all__)
				newfile.write(line)
		import sys
		sys.path.insert(0,self.userLibPath)


	def removeNewFiles(self):
		''' Compares the status before and after the execution to check if new files are created, all the new files are deleted from the results folder.
		'''
		added = self.getNewFilesPath()
		for newfile in added:
			dstfile = newfile.replace(os.path.abspath(self.runFolder),os.path.abspath(self.resultsFolder))
			os.remove(newfile)
		os.remove(self.zippedFile)
		os.remove('status'+str(self.taskID)+'.txt')
	
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
					
	def saveIO(self, variables, outStream):
		''' Saves all the new data, outputs and variables after the execution of the script/task
		Attributes
		----------
		variables : object
			The object that is returned by the task
		outStream : io.StringIO
			Object containing all the outputs of the stdout pipe
		'''
		self.moveNewFiles()
		self.saveData(str(variables), 'out', self.resultsFolder)
		self.saveData(outStream, 'stdout', self.resultsFolder)
		self.saveData(outStream, 'stdout', self.userDataPath+'/node_logs')
		self.saveData(outStream, 'stdout', self.userDataPath+'/ResultsFiles')

	def saveData(self, data, name, path2save):
		''' Saves in files the information in data as <path2save>/name.txt
		----------
		data : string or io.StringIO
			The data to be saved
		name : string
			Name of the file to be saved
		path2save : string
			Path where the file must be stored, can be relative or absolute
		'''
		#self.log('Saving Info...')
		# testing = True
		# if(testing):
		# 	import sys
		# 	print("----------WARNING----------- Testing is activated", file=sys.stderr)
		# 	path2save= path2save.replace('/code','.')
		# 	fileName = os.path.abspath(path2save) + "/" + name + ".txt"
		# else:
		fileName = path2save + "/" + name + ".txt"
		# print('Saving using fileName: {0}'.format(fileName))
		if(not os.path.exists(path2save + "/")):
			# print('Saving using path2save: {0}'.format(path2save))
			os.makedirs(path2save + "/")
		file = open(fileName, 'w')
		if(not isinstance(data, str)):
			dataread  = data.getvalue()
			file.write(dataread)
		else:
			file.write(data)