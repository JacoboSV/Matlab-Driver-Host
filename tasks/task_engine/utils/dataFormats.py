import ast
import base64
import json
import os
import time
import numpy as np
import base64

class IOFormatter(object):
	"""
	Class to manage 

	Attributes
	----------

	"""
	def __init__(self):
		self.inputformat = ''
		self.outputformat = ''
		self.inputs = ''
		self.outputs = ''
		self.INPUT_HANDLER = {
			'matlab' : self._get_Matlab_Input,
			'file'   : self._get_File_Input,
			'inline' : self._get_Inline_Input,
			'json'   : self._get_Json_Input
		}
		self.OUTPUT_HANDLER = {
			'matlab' : self._get_File_Output,
			'file'   : self._get_File_Output,
			'inline' : self._get_Inline_Output,
			'json'   : self._get_Json_Output,
			'bundle' : self._get_Bundle_Output
		}
		self.CASTERS = {
			'bool' : bool,
			'string'   : str,
			'float' : float,
			'number' : float,
			'double'   : float,
			'integer' : int,
			'array' : list,
			'nparray' : np.array,
			'matrix' : list,
			'npmatrix' : np.array,
			'file' : self._b64_to_file,
			'option': self.castStr,
			'any': self.castStr
			}
		self.LOCATORS = {
			'bool' : str,
			'string'   : str,
			'float' : str,
			'number' : str,
			'double'   : str,
			'integer' : str,
			'array' : str,
			'nparray' : str,
			'matrix' : str,
			'npmatrix' : str,
			'file' : self.locateFile,
			'option': str,
			'any': str
			}
		
		self.IOSTR = {
			"format" : "",
			"name"   : "",
			"data"   : None,
			"info"   : {
				"startTime"      : "",
				"stopTime"       : "",
				"duration"       : 0,
				"stdout"         : "",
				"generatedFiles" : {
					"names" : [],
					"sizes" : []
				}
			}
		}

	def castStr(self,strChain):
		return str(strChain).strip('"').strip("'")

	def getName(self):
		return self.IOSTR["name"]
		
	def getStartTime(self):
		return self.IOSTR["info"]["startTime"]

	def getStopTime(self):
		return self.IOSTR["info"]["stopTime"]

	def setStartTime(self, time):
		self.IOSTR["info"]["startTime"] = time

	def setStopTime(self, time):
		self.IOSTR["info"]["stopTime"] = time
		
	def getFormat(self):
		return self.IOSTR["format"]

	def getData(self):
		return self.IOSTR["data"]

	def setDuration(self, duration):
		self.IOSTR["info"]["duration"] = duration

	def setStdout(self, stdout):
		self.IOSTR["info"]["stdout"] = stdout

	def setGeneratedFiles(self,names,sizes):
		self.IOSTR["info"]["generatedFiles"]["names"] = names
		self.IOSTR["info"]["generatedFiles"]["sizes"] = sizes

	def addGeneratedFile(self,name,size):
		self.IOSTR["info"]["generatedFiles"]["names"].append(name)
		self.IOSTR["info"]["generatedFiles"]["sizes"].append(size)

	def setName(self,name):
		self.IOSTR["name"] = name

	def setFormat(self,format):
		self.IOSTR["format"] = format

	def setData(self,data):
		self.IOSTR["data"] = data

	def initializeIOSTR(self,ioput):
		self.inputs = ioput
		self.setName(ioput["name"])
		self.setFormat(ioput["format"])
		self.setData(ioput["data"])
		
	def readInputFormat(self,path):
		with open(path) as json_file:
			self.inputformat = json.load(json_file)
			return self.inputformat
			
	def readOutputFormat(self,path,task):
		outputFile = os.path.join(path, 'outputformat.txt')
		with open(outputFile) as json_file:
			outputFormats = json.load(json_file)
			#When task is a Python task it is written: <library>.<method>. The file outputFile, contain the formats 
			#for all the available methods in an array structure. This code read the method, and returns the right format
			if('.' in task):
				module_method = task.split('.')
				#lib = module_method[0]
				meth = module_method[1]
				self.outputformat = outputFormats['formats'][meth]
				return outputFormats['formats'][meth]
			else:
				self.outputformat = outputFormats['formats'][task]
				return self.outputformat
	
	def formatInputs(self, params, task, path):
		self.task = task
		#self.initializeIOSTR(params)
		#return self.INPUT_HANDLER[self.getFormat()](path)
		args = {}
		for variable in params['variables']:
			paramType =  variable['type'].lower().split('[')[0]
			paramName = variable['name']
			if('location' in variable and 'server' in paramLoc):
				paramLoc = variable['location']
				if('file' in paramType):
					values = self.LOCATORS[paramType](variable['data'])
				else:
					values = self.LOCATORS[paramType](paramName)
			else:
				if('file' in variable['type']):
					values = self.CASTERS[paramType](paramName+'.'+variable['subtype'],variable['data'])
				else:
					values = self.CASTERS[paramType](variable['data'])
			args[paramName] = values
		return args
		
	def formatOutputs(self, runPath, resultsPath, data, files=None, duration=0, startTime="", stopTime=""):
		expectedOutput = self.readOutputFormat(runPath, self.task)
		self.initializeIOSTR(expectedOutput)
		if(files):
			self.setGeneratedFiles(files["names"],files["sizes"])
		self.setDuration(duration)
		self.setStartTime(startTime)	
		self.setStopTime(stopTime)
		return self.OUTPUT_HANDLER[self.getFormat()](runPath, resultsPath, data)
	
	def populateOutData(self, data):
		self.IOSTR['data'] = data
		return self.IOSTR
	
	def _get_Inline_Input(self, path=None):
		data = self.getData()
		dataIn = data.split(',')
		return dataIn
	
	def _get_File_Input(self, path=None):
		return str(self.IOSTR)
	
	def _get_Json_Input(self, path=None):
		return json.dumps(self.getData())

	def _get_Matlab_Input(self,path):
		name = self.getName()
		if(name):
			filename = self.locateFile(name)
		else:
			filename = None
		if(filename is None):
			filename = path + '/input_file.mat'
			self._b64_to_file(filename,self.getData())
		return os.path.abspath(filename)

	def _get_File_Output(self,runfolder, resultfolder = None,data = None):
		path2file = self.locateFile(self.getName(),runfolder)
		return self.populateOutData(self.serializeFile(path2file))

	def _get_Inline_Output(self,runfolder = None, resultfolder = None,data = None):
		if(isinstance(data,dict)):
			outvalues = data
		else:
			outvalues = str(data)
		return self.populateOutData(outvalues)

	def _get_Json_Output(self, runfolder=None, resultfolder=None, data=None):
		if(isinstance(data, dict)):
			outvalues = data
		else:
			outvalues = json.loads(data)
		return self.populateOutData(outvalues)

	def _get_Bundle_Output(self,runfolder,resultfolder,data = None):
		path2file = self.locateFile(self.IOSTR['name'],resultfolder)
		filebytes = self.serializeFile(path2file)
		return self.populateOutData(filebytes)

	@staticmethod
	def _evalTypes(val):
		try:
			val = ast.literal_eval(val)
		except ValueError:
			pass
		return val

	def _b64_to_file(self,name,data):
		tempFolder = './var/temp/'
		path = tempFolder+name
		fh = open(path, 'wb')
		fh.write(base64.b64decode(data))
		fh.close()
		return os.path.abspath(path)

	def serializeFile(self,filepath):
		with open(filepath, 'rb') as f:
			data = base64.b64encode(f.read())
		datastring = data.decode('utf-8')
		return datastring

	def locateFile(self,what,where = None):
		#print("File location: ", what)
		if(where):
			for files in os.listdir(where):
				if(what in str(files)):
					return os.path.abspath(os.path.join(where,files))
		else:
			if(os.path.isfile(what)):
				return os.path.abspath(what)
			else:
				return None
		return None
