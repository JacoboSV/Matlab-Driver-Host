import os
import json
import traceback
import pandas as pd
import numpy as np

def userMethod({parameters}, outputWanted = 'Result'):
	_error = ""
	_output = None
	_output = {"output": _output, "error": _error}
	errorCode = ""
	#if the variable errorCode is defined in this code it will appear if an exception is catched
	{Check params}
	try:
		_outputNotChecked = run({parametersInFunction}, outputWanted)
		#_output = checkTypes(_outputNotChecked)
		_output = _outputNotChecked
		
	except Exception as e:
		_output = "Err"
		print(traceback.print_exc())
		_error = "Exception captured. Error: " + str(e) + ", User error code: " + errorCode 
	
	return {"output": _output, "error": _error}


def run({parameters}, outputWanted = None):
	outputs = None
	# Main user code goes here
	# Do not use "_" when defining variables
	#______________ Example __________________
	outputs = []
#{userCode}
	#________________________________
	return [#{outputlist}]


