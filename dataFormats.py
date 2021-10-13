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
		self.INPUT_HANDLER = {
			'matlab' : self._get_Matlab_Input,
			'file' : self._get_File_Input,
			'inline' : self._get_Inline_Input,
			'json' : self._get_Json_Input
		}
		self.OUTPUT_HANDLER = {
			'matlab' : self._get_File_Output,
			'file' : self._get_File_Output,
			'inline' : self._get_Inline_Output,
			'json' : self._get_Json_Output,
			'bundle' : self._get_Bundle_Output
		}
	
		self.IOSTR = {
			"format" : "",
			"name" : "",
			"data" : None,
			"info" : {
				"startTime" : "",
				"stopTime" : "",
				"duration" : 0,
				"stdout" : "",
				"generatedFiles" : {
					"names" : [],
					"sizes" : []
				}
			}
		}
		
	

	def getName(self):
		return self.IOSTR["name"]
		
	def getStartTime(self):
		return self.IOSTR["name"]["startTime"]
	def getStopTime(self):
		return self.IOSTR["info"]["stopTime"]
	def setStartTime(self,time):
		self.IOSTR["name"]["startTime"] = time
	def setStopTime(self):
		self.IOSTR["name"]["stopTime"] = time
		
	def getFormat(self):
		return self.IOSTR["format"]
	def getData(self):
		return self.IOSTR["data"]
	def setDuration(self,duration):
		self.IOSTR["info"]["duration"] = duration
	def setStdout(self,stdout):
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
		self.setName(ioput["name"])
		self.setFormat(ioput["format"])
		self.setData(ioput["data"])
		
	def readInputFormat(self,path):
		with open(path) as json_file:
			self.inputformat = json.load(json_file)
			return self.inputformat
			
	def readOutputFormat(self,path,task):
		outputFile = os.path.join(path,'outputformat.txt')
		with open(outputFile) as json_file:
			outputFormats = json.load(json_file)
			#When task is a Python task it is written: <library>.<method>. The file outputFile, contain the formats for all the available methods in an array structure. This code read the method, and returns the right format
			if('.' in task):
				module_method = task.split('.')
				#lib = module_method[0]
				meth = module_method[1]
				self.outputformat = outputFormats['formats'][meth]
				return outputFormats['formats'][meth]
			else:
				self.outputformat = outputFormats
				return self.outputformat
	
	def formatInputs(self,params,task,path):
		self.task = task
		self.initializeIOSTR(params)
		self.inputs = params
		self.setFormat(params['format'])
		#format = params['format']
		return self.INPUT_HANDLER[self.getFormat()](path)
		
	def formatOutputs(self,runPath,resultsPath,data,files = None,duration = 0, startTime = "", stopTime = ""):
		expectedOutput = self.readOutputFormat(runPath,self.task)
		#self.outputs = expectedOutput 
		self.initializeIOSTR(expectedOutput)
		if(files):
			self.setGeneratedFiles(files["names"],files["sizes"])
		self.setDuration(duration)
		self.setStartTime(startTime)
		self.setStopTime(stopTime)
		#format = self.outputs['format']
		#print("expectedOutput[format]", expectedOutput['format'])
		#print("self.getFormat()", self.getFormat())
		return self.OUTPUT_HANDLER[self.getFormat()](runPath,resultsPath,data)
	
	def populateOutData(self,data):
		#self.outputs = self.outputformat
		#self.outputs = self.IOSTR
		self.IOSTR['data'] = data
		return self.IOSTR
	
	# def populateInData(self,data):
		# self.inputs = self.inputformat
		# self.inputs['data'] = data
		# return self.inputs
	
	def _get_Inline_Input(self,path = None):
		data = self.getData()
		#if(data is None):
		#	data = self.inputs['data']
		dataIn = data.split(',')
		return dataIn
	
	def _get_File_Input(self,path = None):
		#return str(self.inputs)
		return str(self.IOSTR)
	
	def _get_Json_Input(self,path = None):
		#data = self.inputs['data']
		return json.dumps(self.getData())

	def _get_Matlab_Input(self,path):
		#data = self.inputs['data']
		name = self.getName()
		if(name):
			filename = self.locateFile(name)
		else:
			filename = None
		if(filename is None):
			#if(not data):
			#	data = self.inputs['data']
			filename = path + '/input_file.mat'
			self._b64_to_file(filename,self.getData())
		return os.path.abspath(filename)
	
	def _get_File_Output(self,runfolder,resultfolder = None,data = None):
		path2file = self.locateFile(self.getName(),runfolder)
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
		#print("runfolder: ", runfolder)
		#print("resultfolder: ", resultfolder)
		#print("data: ", data)
		
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
