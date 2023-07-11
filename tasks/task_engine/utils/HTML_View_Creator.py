import json
import random
import pandas as pd
import re
import base64 as b64
from PIL import Image
from .imageFormatter import ImageFormatter
import os
import sys


class OutputHTMLCreator(object):
	def __init__(self):
		jsonData = {}
		error = False
		self.templatePath = "tasks/task_engine/utils/template_userSkeleton.html"
		self.convertImages2b64 = True
		self.reduceImages = True
		self.imageType = "logo"
		self.jsonkey_forfiles = "generatedFiles"
		self.fileCount = 0

	def isImage(self,file):
		types = ['apng','avif','gif','jpg','jpeg','jfif','pjpeg','pjp','png','svg','webp']
		fileext = file.split('.').pop()
		return fileext in types

	def isTextFile(self,file):
		types = ['txt','json','log','nfo','md','ocr']
		fileext = file.split('.').pop()
		return fileext in types

	def getTextFromFile(self,file):
		text_file = open(file, "r")
		data = text_file.read()[0:500]
		text_file.close()
		return data	

	def getHTMLasString(self):
		text_file = open(self.path_outHTML, "r")
		data = text_file.read()
		text_file.close()
		return data

	def rePathFiles(self,files):
		filesPaths = files['names']
		filesPaths = ['../ResultsFiles/' + os.path.basename(filep) for filep in filesPaths]
		return filesPaths

	def getHTML_filesFigs(self, filepaths):
		html_FF = ''
		repathfiles = self.rePathFiles(filepaths)
		# print("-_-----_____repathfiles {0}".format(repathfiles), file=sys.stderr)
		fivetabs = '\t\t\t\t\t'
		for count, filep in enumerate(repathfiles):
			html_FF += fivetabs + '<span class="mySlides w3-center"> \n'
			if(self.isImage(filep)):
				html_FF += fivetabs + '\t<img class="w3-animate-opacity" src="' + filep + '" style="box-shadow: 3px 3px 3px rgba(0, 65, 87, 0.5);width:100%"> \n'
				html_FF += fivetabs + '\t<p>' + os.path.basename(filep) + '</p> \n'
			elif(self.isTextFile(filep)):
				html_FF += fivetabs + '\t<div class="w3-animate-opacity w3-left-align" style="box-shadow: 3px 3px 3px rgba(0, 65, 87, 0.5);width:100%"> \n'
				html_FF += fivetabs + '\t' + self.getTextFromFile(filepaths['names'][count]).replace('\n','<br>').replace('\t','&emsp; ') + ' \n'
				html_FF += fivetabs + '\t</div> \n'
				html_FF += fivetabs + '\t<p>' + os.path.basename(filep) + '</p> \n'
			else:
				html_FF += fivetabs + '\t<div class="w3-animate-opacity" style="box-shadow: 3px 3px 3px rgba(0, 65, 87, 0.5);width:100%"> \n'
				html_FF += fivetabs + '\t' +  filep + ' \n'
				html_FF += fivetabs + '\t</div> \n'
				html_FF += fivetabs + '\t<p>' + os.path.basename(filep) + '</p> \n'
			html_FF += fivetabs + '</span>'

		return html_FF 
		# 

	def orderIO(self,namedInputs,namedOutputs):
		io_namevalue = {name:namedInputs[name] for name in namedInputs}
		for name in namedOutputs:
			io_namevalue[name] = namedOutputs[name]
		return io_namevalue

	def create(self,rawData, path_outHTML = 'var/temp/filledTemplate.html', bdnodeInfo = {}, namedInputs = {}):
		error = False
		if(isinstance(rawData,dict)):
			outputJSON = rawData
		else:
			try: 
				outputJSON = json.load(rawData)
			except:
				print("The data can't be processed as JSON, please check the output data to find more information.")
				error = True
		self.path_outHTML = path_outHTML
		htmlfile = open(self.templatePath,'r', encoding="utf8")
		newFile = open(path_outHTML,'w', encoding="utf8")
		filesAndFigs = outputJSON['info']['generatedFiles']
		for line in htmlfile:
			if(not error):
				if('///**NODE RUN INFO**///' in line):
					newFile.write('all_info = ' + json.dumps(outputJSON))
				elif('///**NODE OUTPUT DATA**///' in line):
					namedOutputs = outputJSON['data']['output']
					io_namevalue = self.orderIO(namedInputs,namedOutputs)
					# print("-_-----_____io_namevalue {0}".format(io_namevalue.keys()), file=sys.stderr)
					plottableData = {}
					for keyOut in io_namevalue:
						try:
							if(isinstance(io_namevalue[keyOut],str)):
								plottableData[keyOut] = io_namevalue[keyOut]
							else:
								plottableData[keyOut] = pd.DataFrame(io_namevalue[keyOut]).to_dict(orient='list')
						except:
							plottableData[keyOut] = io_namevalue[keyOut]
					newFile.write('outputData = {0}'.format(plottableData))
				elif('///**NODE INFO**///' in line):
					newFile.write('bdnode_info = ' + json.dumps(bdnodeInfo))
				elif('///**FIGS AND FILES**///' in line):
					newFile.write(self.getHTML_filesFigs(filesAndFigs) + '\n')
				else:
					newFile.write(line)
			else:
				if('///**HtmlData**///' in line):
					newFile.write('<h1> Error found when procesing the output data as JSON, please check the data and paths </h1>')
		newFile.close()
		htmlfile.close()

