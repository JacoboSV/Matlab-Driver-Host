import os as _os
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
		_output = checkTypes(_outputNotChecked)
		
	except Exception as e:
		_output = "Err"
		print(traceback.print_exc())
		_error = "Exception captured. Error: " + str(e) + ", User error code: " + errorCode 
	
	return {"output": [_output], "error": _error}


def checkTypes(_rawInputs):
	signals = []
	for _input in _rawInputs: 
		if isinstance(arr, np.ndarray):
			signals.append(_input.tolist())
		elif isinstance(_input, pd.Series):
			signals.append(_input)
		elif isinstance(_input, str):
			signals.append('"' + _input + '"')
		elif isinstance(_input, dict):
			signals.append( pd.DataFrame(_input['signal'][0]))
		elif isinstance(_input, str):
			jsondata = json.loads(_input)
			signals.append( pd.DataFrame(jsondata['signal'][0]))
	return signals

def run({parameters}, outputWanted = None):
	outputs = None
	# Main user code goes here
	# Do not use "_" when defining variables
	#______________ Example __________________
	outputs = {}
#{userCode}
	#________________________________
	if(outputWanted is None or outputWanted not in outputs):
		return outputs
	else:
		return outputs[outputWanted]
