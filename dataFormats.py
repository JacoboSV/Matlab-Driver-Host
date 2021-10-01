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

class ioFormatter(object):
	"""
	Class to manage 

	Attributes
	----------

	"""
	def __init__(self):
		#self.folderHandler = folderHandler
		self.inputformat = ''
		self.outputformat = ''
		self.inputs = ''
		self.outputs = ''
		self.inTypes = {
			'matlab' : self._get_Matlab_Input,
			'file' : self._get_File_Input,
			'inline' : self._get_Inline_Input,
			'json' : self._get_Json_Input
		}
		self.outTypes = {
			'matlab' : self._get_File_Output,
			'file' : self._get_File_Output,
			'inline' : self._get_Inline_Output,
			'json' : self._get_Json_Output,
			'bundle' : self._get_Bundle_Output
		}
	
	def readInputFormat(self,path):
		with open(path) as json_file:
			self.inputformat = json.load(json_file)
			return self.inputformat
			
	def readOutputFormat(self,path,task):
		inputFile = os.path.join(path,'outputformat.txt')
		with open(inputFile) as json_file:
			outputFormats = json.load(json_file)
			if('.' in task):
				module_method = task.split('.')
				lib = module_method[0]
				meth = module_method[1]
				self.outputformat = outputFormats['formats'][meth]
				return outputFormats['formats'][meth]
			else:
				self.outputformat = outputFormats
				return self.outputformat
	
	def formatInputs(self,params,task,path):
		self.inputs = params
		self.task = task
		format = params['format']
		return self.inTypes[format](path)
		
	def formatOutputs(self,runPath,resultsPath,data):
		self.outputs = self.readOutputFormat(runPath,self.task)
		format = self.outputs['format']
		return self.outTypes[format](runPath,resultsPath,data)
	
	def populateOutData(self,data):
		self.outputs = self.outputformat
		self.outputs['data'] = data
		return self.outputs
	
	def populateInData(self,data):
		self.inputs = self.inputformat
		self.inputs['data'] = data
		return self.inputs
	
	def _get_Inline_Input(self,path = None):
		data = self.inputs['data']
		if(data is None):
			data = self.inputs['data']
		dataIn = data.split(',')
		return dataIn
	
	def _get_File_Input(self,path = None):
		return str(self.inputs)
	
	def _get_Json_Input(self,path = None):
		data = self.inputs['data']
		return json.dumps(data)

	def _get_Matlab_Input(self,path):
		data = self.inputs['data']
		name = self.inputs['name']
		if(name):
			filename = self.locateFile(name)
		else:
			filename = None
		if(filename is None):
			if(not data):
				data = self.inputs['data']
			filename = path + '/input_file.mat'
			self._b64_to_file(filename,data)
		return os.path.abspath(filename)
	
	def _get_File_Output(self,runfolder,resultfolder = None,data = None):
		path2file = self.locateFile(self.outputs['name'],runfolder)
		return self.populateOutData(self.serializeFile(path2file))
		
	def _get_Inline_Output(self,runfolder = None,resultfolder = None,data = None):
		if(isinstance(data,dict)):
			outvalues = data
		else:
			outvalues = str(data)
		return self.populateOutData(outvalues)
		
	def _get_Json_Output(self,runfolder = None,resultfolder = None,data = None):
		if(isinstance(data,dict)):
			outvalues = data
		else:
			outvalues = json.loads(data)
		return self.populateOutData(outvalues)
		
	def _get_Bundle_Output(self,runfolder,resultfolder,data = None):
		#filepath = self.folderHandler._zipOutputs()
		path2file = self.locateFile(self.outputs['name'],resultfolder)
		filebytes = self.serializeFile(path2file)
		return self.populateOutData(filebytes)
	
	@staticmethod
	def _evalTypes(val):
		try:
			val = ast.literal_eval(val)
		except ValueError:
			pass
		return val
	
	def _b64_to_file(self,filename,data):
		out_file = open(filename, "wb") 
		out_file.write(base64.b64decode(data))
		out_file.close()
	
	def serializeFile(self,filepath):
		with open(filepath, 'rb') as f:
			data = base64.b64encode(f.read())
		datastring = data.decode('utf-8')
		return datastring

	def locateFile(self,what,where = None):
		if(where):
			for files in os.listdir(where):
				if(what in str(files)):
					return os.path.abspath(os.path.join(where,files))
		else:
			if(os.path.isdir(what)):
				return os.path.abspath(os.path.join(what,files))
			else:
				return None
		return None
