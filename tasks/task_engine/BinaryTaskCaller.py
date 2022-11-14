import os
import subprocess
from .TaskCaller import TaskCaller
import traceback
from subprocess import PIPE

class BinaryTaskCaller(TaskCaller):
	

	def runTask(self, name, args, expectedOuts = None):
		''' Runs a task by its name and using the sent parameters
		Attributes
		----------
		name : string
			name of the task to execute, it must be the exact name of the folder and binary file (/name/name.c) inside the Tasks folder
		args : string or Object
			Path of the file to be used as input or the content of the file
		'''
		if(self.dynamic):
			self.folderHandler.copyTasks(os.path.dirname(name))
		pathToScript = os.path.join(self.folderHandler.runFolder, os.path.basename(name))
		self.folderHandler.savePreStatus()
		try:
			print("name: ", name)
			print("pathToScript: ", pathToScript)
			#result = subprocess.run([pathToScript] + [args['data']], capture_output=True)	
			result = subprocess.run([pathToScript] + [args['data']], stdout=PIPE, stderr=PIPE)		
			print("result", result)
			data = {
				"output": (result.stdout.decode('UTF-8')),
				"error": result.stderr.decode('UTF-8')
			}

			return self.checkStatus(data)
		except:
			print(traceback.format_exc())
			return None