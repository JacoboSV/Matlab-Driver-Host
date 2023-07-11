import ast
import base64
import json
import os
import time
import numpy as np
import pandas as pd
import base64
from .HTML_View_Creator import OutputHTMLCreator
from datetime import datetime
import traceback

class IOFormatter(object):
	"""
	Class to manage 

	Attributes
	----------

	"""
	def __init__(self, nodeInfo, bdnodeInfo, userDataPath = "", IO_types={}, language = 'python'):
		self.inputformat = ''
		self.outputformat = ''
		self.nodeInfo = nodeInfo
		self.bdnodeInfo = bdnodeInfo
		self.inputs = ''
		self.language = language
		self.outputs = ''
		self.userDataPath = userDataPath
		self.IO_types = IO_types
		self.htmlCreator = OutputHTMLCreator()
		self.OUTPUT_HANDLER = {
			'json'   : self._get_Json_Output,
		}
		self.OUT_CASTERS = {
			'np.ndarray': np.ndarray.tolist,
			'pd.dataframe': pd.DataFrame.to_dict,
			'pd.series': pd.Series.tolist,
			'string': self.castStr,
			#signals = '"' + _input + '"'
		}

		self.IN_CASTERS = {
			'python' : {
				'bool' : bool,
				'string'   : str,
				'float' : float,
				'number' : float,
				'double'   : float,
				'integer' : int,
				'array' : self.castArray,
				'np.array' : np.array,
				'matrix' : self.castArray,
				'pd.series' : pd.Series,
				'pd.dataframe': pd.DataFrame,
				'b64file' : self._b64_to_file,
				'file' : self.locateFile,
				'option': self.castStr,
				'any': self.castStr
				},
			'matlab' : {
				'bool' : bool,
				# 'dict' : json.dumps,
				'string'   : self.str_matlab,
				'float' : float,
				'number' : float,
				'double'   : float,
				'integer' : int,
				'array' : self.castArray_matlab,
				'np.array' : self.castArray_matlab,
				'matrix' : self.castArray_matlab,
				'pd.series' : self.castArray_matlab,
				'pd.dataframe': self.castArray_matlab,
				'b64file' : self._b64_to_file,
				'file' : self.locateFile,
				'option': self.castStr,
				'any': self.castStr
				}
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

	def str_matlab(self,strChain):	
		quoted = []
		# varNames = [str(args[x]) for x in args] 
		# self.log("varNames: " + str(varNames))
		if("'" in strChain):
			quoted.append('"' + str(args[varname]) + '"')
		elif("\"" in strChain):
			quoted.append("'" + str(args[varname]) + "'")
		else:
			quoted.append('"' +"'" + str(args[varname]) + "'" + '"')
		return str(strChain)

	# def castDict_matlab(self,strChain):	
	# 	arrayout = 'matlab.int32({0})'.format(arrayData)

	def castStr(self,strChain):
		return str(strChain).strip('"').strip("'")

	def castArray(self,arrayData):
		return list(eval(arrayData))

	def castArray_matlab(self,arrayData):
		arrayout = ''
		firstdata = arrayData[0]
		while(True):
			if(isinstance(firstdata,list)):
				firstdata = firstdata[0]
			else:
				if(isinstance(firstdata,int)):
					arrayout = 'matlab.int32({0})'.format(arrayData)
				elif(isinstance(firstdata,float)):
					arrayout = 'matlab.double({0})'.format(arrayData)
				elif(isinstance(firstdata,bool)):
					arrayout = 'matlab.logical({0})'.format(arrayData)
				else:
					arrayout = 'matlab.single({0})'.format(arrayData)
				break
		return arrayout

	def getName(self):
		return self.IOSTR["name"]
		
	def getStartTime(self):
		return self.IOSTR["info"]["startTime"]

	def getStopTime(self):
		return self.IOSTR["info"]["stopTime"]

	def setStartTime(self, time):
		self.IOSTR["info"]["startTime"] = datetime.fromtimestamp(time).strftime("%d %b %Y %H:%M:%S")

	def setStopTime(self, time):
		self.IOSTR["info"]["stopTime"] = datetime.fromtimestamp(time).strftime("%d %b %Y %H:%M:%S")
		
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

	def setName(self,name):
		self.IOSTR["name"] = name

	def setFormat(self,format):
		self.IOSTR["format"] = format

	def setData(self,data):
		self.IOSTR["data"] = data
	
	def formatInputs(self, params, task):
		'''Adapts the data serialized in the input json to match the input specified in the Node
		----------
		params : dict
			Input parameters extracted from the json info inside the graph
		task: String
			Name of the Node to be run, to be used in files and logs
		'''
		print("params: ", params)
		self.task = task
		args = {}
		for variable in params['variables']:
			paramType =  variable['type'].lower().split('[')[0]
			paramName = variable['name']
			if('location' in variable and 'server' in variable['location']):
				paramLoc = variable['location']
				if('file' in paramType):
					values = self.LOCATORS[paramType](variable['data'])
				else:
					values = self.LOCATORS[paramType](paramName)
			else:
				if('b64file' in variable['type']):
					values = self.IN_CASTERS[self.language][paramType](paramName+'.'+variable['subtype'],variable['data'])
				else:
					# print("paramType: {0}".format(paramType))
					
					print("variable['data']: ", variable['data'])
					try:
						values = self.IN_CASTERS[self.language][paramType](variable['data'])
					except:
						values = variable['data']
					#print("values: ", values)
			args[paramName] = values
		self.args = args
		return args
		
	def formatOutputs(self, data, files=None, duration=0, startTime="", stopTime=""):
		'''Adapts the data to be serialized and included in a json, uses Node information from graph
		----------
		data : dict
			Raw output dict, contain all the data that can be serializable or not
		files: list
			Names of the files that have been created during the Node run
		duration: Int
			Diference between start and stop time (ms)
		startTime: String
			ISO string that contains start date and time
		stopTime: String
			ISO string that contains stop date and time
		'''
		self.setName(self.nodeInfo.get("name"))
		self.setFormat('json')
		if(files):
			self.setGeneratedFiles(files["names"],files["sizes"])
		self.setDuration(duration)
		self.setStartTime(startTime)	
		self.setStopTime(stopTime)
		formattedOutput = self._get_Json_Output(data)
		formattedOutput['nodeInfo'] = self.nodeInfo
		# with open('testing.txt', 'w') as f:
		# 	f.write("formattedOutput: {0}".format(formattedOutput))
		# 	f.write("self.nodeInfo: {0}".format(self.nodeInfo))
		try:
			self.htmlCreator.create(formattedOutput, bdnodeInfo = self.bdnodeInfo, namedInputs = self.args)
			htmlText = self.htmlCreator.getHTMLasString()
		except:
			print(str(traceback.format_exc()))
			htmlText = "Error : ", str(traceback.format_exc())
		scappedHtmlText = htmlText
		formattedOutput["info"]["html"] = scappedHtmlText
		return formattedOutput
	
	def populateOutData(self, data):
		'''Fills the data field of the IOSTR dict object to be sent to the executor		
		'''
		self.IOSTR['data'] = data
		return self.IOSTR

	def _get_Json_Output(self, datain=None):
		'''Check and modifies the output data to be serialized.
		----------
		data : dict
			Raw output dict, contain all the data that can be serializable or not
		'''
		for data in datain['output']:
			datain['output'][data] = self.checkTypes(datain['output'][data])
		return self.populateOutData(datain)

	def checkTypes(self,_input):
		'''Changes the type of well knows not json serializable types
		----------
		data : Any
			Raw output value, can be serializable or not
		'''
		if isinstance(_input, np.ndarray):
			signals = _input.tolist()
		elif isinstance(_input, pd.DataFrame):
			signals = _input.to_dict()
		elif isinstance(_input, pd.Series):
			signals = _input.tolist()
		elif isinstance(_input, str):
			signals = '"' + _input + '"'
		elif isinstance(_input, dict):
			signals = _input
		else:
			signals = _input
		return signals

	def _b64_to_file(self,name,data):
		tempFolder = './var/temp/'
		path = tempFolder+name
		fh = open(path, 'wb')
		fh.write(base64.b64decode(data))
		fh.close()
		return os.path.abspath(path)

	def locateFile(self,what,where = None):
		'''Locates the files in the user path and returns an accesible path 
		----------
		what : String
			File name
		where: String
			Relative path inside user path
		'''
		pathsjoined = os.path.abspath(self.userDataPath  + what)
		what = os.path.basename(pathsjoined)
		where = os.path.dirname(pathsjoined)
		if(where):
			for files in os.listdir(where):
				if(what in str(files)):
					return os.path.abspath(os.path.join(where,files))
		else:
			if(os.path.isfile(pathsjoined)):
				return pathsjoined
			else:
				return None
		return None
