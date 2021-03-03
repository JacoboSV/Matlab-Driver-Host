from remoteMatlabFolders import remoteMatlabFolders
import json
import sys
import getopt
import os
import matlab.engine
import base64

class testFolders(object):

	def __init__(self):
		self.folderHandler = remoteMatlabFolders(dynamic = True)
		print('It is reading inputs?: ' + str(self.readsInputFormat('procesado')))
		print('It is populating with bytes the data field?: ' + str(self.populatesDatafield(bytes('example', encoding='utf-8'))))
		with open("ins.mat", 'rb') as f:
			data = base64.b64encode(f.read())
		datastring = data.decode('utf-8')
		datajson = {"format":"matlab","name":"ins.mat","data":datastring}		
		#print(json.dumps(datajson, indent=4, sort_keys=True)[1:50] + '(...)')
		dataout = base64.b64decode(datastring)
		
		print('It is populating with string the data field?: ' + str(self.populatesDatafield('"C15a",0.001,56988,6')))
		print('It is creating inline commands?: ' + str(self.createsInlineCommand('"C15a",0.001,56988,6',['"C15a"','0.001','56988','6'])))
		print('It is creating inline commands from raw data?: ' + str(self.createsInlineCommand(None,['"C15a"','0.001','56988','6'])))
		print('It is populating with bytes from matlab file the data field?: ' + str(self.populatesDatafield(data)))
		print('It is creating matlab input commands from .mat data?: ' + str(self.createMatFileCommand(datajson,'procesado')))
		
		dataout = base64.b64decode(data)

		out_file = open("out-file.mat", "wb")
		out_file.write(dataout)
		out_file.close()
		
	def readsInputFormat(self,task):
		inputformat = self.folderHandler.readInputFormat(task)
		isformatKey = 'format' in inputformat
		isnameKey = 'name' in inputformat
		isdataKey = 'data' in inputformat
		return (isformatKey & isnameKey & isdataKey)
		
	def isFileNeeded(self,data):
		engine = matlab.engine.connect_matlab()
		try:
			engine.load(data)
			return False
		except:
			return True

	def populatesDatafield(self,data):
		inputsJSON = self.folderHandler.populateInData(data)
		#print(inputsJSON)
		isDataOk = inputsJSON['data'] == data
		return isDataOk
	
	def createsInlineCommand(self,data,check):
		command = self.folderHandler.createInlineCommand()
		#print(command)
		return command == check
		
	def createMatFileCommand(self,data = None,task=None):
		command = self.folderHandler.createMatFileCommand(data,task)
		return command 
		

def main(argv):
	test = testFolders()

if __name__ == "__main__":
	main(sys.argv[1:])