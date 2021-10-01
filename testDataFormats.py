from dataFormats import ioFormatter
from remoteFolders import remoteFolders
import json
import sys
import getopt
import os
import matlab.engine
import base64

class testDataFormats(object):

	def __init__(self):
		self.folderHandler = remoteFolders()
		self.folderHandler.checkCreateFolders()
		self.folderHandler.copyTasks('procesado')
		self.formatter = ioFormatter()
		runFolder = os.path.abspath(self.folderHandler.runFolder)
		
		with open("./Temp/ins.mat", 'rb') as f:
			data = base64.b64encode(f.read())
		datastring = data.decode('utf-8')
		datajson = {"format":"matlab","name":"ins.mat","data":datastring}		
		dataout = base64.b64decode(datastring)
		
		print('Reading inputs: \t\t\t' + str(self.readsInputFormat(runFolder+'/inputformat.txt')))
		print('Reading outputs: \t\t\t' + str(self.readsOutputFormat(runFolder+'/inputformat.txt','procesado')))
		
		print('Fill input with bytes: \t\t\t' + str(self.populatesDatafield(bytes('example', encoding='utf-8'),True)))
		print('Fill input  with string: \t\t' + str(self.populatesDatafield('"C15a",0.001,56988,6',True)))
		print('Fill output with bytes: \t\t' + str(self.populatesDatafield(bytes('example', encoding='utf-8'),False)))
		print('Fill output with string: \t\t' + str(self.populatesDatafield('"C15a",0.001,56988,6',False)))
		print('Fill input using data field bytes: \t' + str(self.populatesDatafield(data,True)))
		
		print('Creating matlab ins: \t\t\t' + str(self.getsInputs(datajson,runFolder,'procesado',runFolder+'\input_file.mat')))
		datajson = {"format":"json","name":"","data":{'newins':'totest'}}
		
		print('Creating json ins: \t\t\t' + str(self.getsInputs(datajson,runFolder,'procesado',json.dumps({'newins':'totest'}))))
		datajson = {"format":"inline","name":"","data":'"C15a",0.001,56988,6'}
		print('Creating inline ins: \t\t\t' + str(self.getsInputs(datajson,runFolder,'procesado',['"C15a"','0.001','56988','6'])))
		
		
	def readsInputFormat(self,task):
		inputformat = self.formatter.readInputFormat(task)
		isformatKey = 'format' in inputformat
		isnameKey = 'name' in inputformat
		isdataKey = 'data' in inputformat
		return (isformatKey & isnameKey & isdataKey)
		
	def readsOutputFormat(self,path,task):
		outputformat = self.formatter.readOutputFormat(path,task)
		isformatKey = 'format' in outputformat
		isnameKey = 'name' in outputformat
		isdataKey = 'data' in outputformat
		return (isformatKey & isnameKey & isdataKey)
		

	def populatesDatafield(self,data,inorout):
		if(inorout):
			inputsJSON = self.formatter.populateInData(data)
		else:
			inputsJSON = self.formatter.populateOutData(data)
		#print(inputsJSON)
		isDataOk = inputsJSON['data'] == data
		return isDataOk
	
	def getsInputs(self,data,task,path,check):
		command = self.formatter.formatInputs(data,path,task)
		return command == check
		
	def createMatFileCommand(self,data = None,task=None):
		command = self.formatter.createMatFileCommand(data,task)
		return command 
		

def main(argv):
	test = testDataFormats()

if __name__ == "__main__":
	main(sys.argv[1:])