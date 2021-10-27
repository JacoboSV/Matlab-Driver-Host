import os
import subprocess
from .TaskCaller import TaskCaller


class BinaryTaskCaller(TaskCaller):
	

	def runTask(self, name, args):
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
			result = subprocess.run([pathToScript] + args, capture_output=True)
			data = {
				"output": (result.stdout.decode('UTF-8')),
				"error": result.stderr.decode('UTF-8')
			}
			return self.checkStatus(data)
		except:
			return None