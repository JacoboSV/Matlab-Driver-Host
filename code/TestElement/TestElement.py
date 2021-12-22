import os as _os
import json
import traceback


def userMethod(inputOne,extraInput = None, outputWanted = 'Result'):
	_error = "Code do nothing"
	_output = None
	_output = {"output": _output, "error": _error}
	errorCode = ""
	#if the variable errorCode is defined in this code it will appear if an exception is catched
	if(not isinstance(inputOne,str)):
		_error = "Parameter inputOne is of incorrect type"
	if(extraInput is not None and not isinstance(extraInput,float)):
		_error = "Parameter extraInput is of incorrect type"
	try:
		_output = run(inputOne,extraInput, outputWanted)
	except Exception as e:
		_output = "Err"
		print(traceback.print_exc())
		_error = "Exception captured. Error: " + str(e) + ", User error code: " + errorCode 
	
	return {"output": _output, "error": _error}


def checkTypes(_rawInputs):
	signals = []
	for _input in _rawInputs: 
		if isinstance(_input, _pandas.Series):
			signals.append(_input)
		elif isinstance(_input, dict):
			signals.append( _pandas.DataFrame(_input['signal'][0]))
		elif isinstance(_input, str):
			jsondata = json.loads(_input)
			signals.append(_pandas.DataFrame(jsondata['signal'][0]))
	return signals

def run(inputOne,extraInput = None, outputWanted = None):
	outputs = None
	# Main user code goes here
	# Do not use "_" when defining variables
	#______________ Example __________________
	outputs = {}
	import numpy as np
	print('Hello World!')
	outputs = 'Hello World! these are my params: ' + str(inputOne) + ', ' + str(extraInput)
	#________________________________
	if(outputWanted is None or outputWanted not in outputs):
		return outputs
	else:
		return outputs[outputWanted]
