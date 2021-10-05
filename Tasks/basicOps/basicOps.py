import os as _os
import pandas as _pandas
import uuid as _uuid
import numpy as _numpy
import matplotlib.pyplot as _matplotlib_pyplot
import scipy.io
import json
import math
import traceback


def _operation(operation, operand1, operand2):
	_error = None
	#print("operation: ",operation)
	#print("operand1: ",operand1)
	#print("operand2: ",operand2)
	if(isinstance(operand1, str) or isinstance(operand2, str)):
		operand1 = float(operand1)
		operand2 = float(operand2)
		
	OPERATIONS = {
		"plus": lambda a,b : a+b,
		"minus": lambda a,b : a-b,
		"times": lambda a,b : a*b,
		"divided by": lambda a,b : a/b,
		'>' : lambda a, b : a >  b,
		'>=': lambda a, b : a >= b,
		'<' : lambda a, b : a <  b,
		'<=': lambda a, b : a <= b,
		'==': lambda a, b : a == b,
		'!=': lambda a, b : a != b
	}

	if("divided by" in operation):
		if (operand2==0):
			_output = "Err"
			_error = "Operand 2 can't be 0"
			return {"output": _output, "error": _error}
	
	try: 
		_output = OPERATIONS[operation](operand1, operand2)
	except Exception as e:
		_output = "Err"
		print("Operation not valid: expected 'plus', 'minus', 'times', 'divided by', <,>,= or != got : ", str(operation))
		print("Operation not valid: expected numeric inputs, got : operand 1: " + str(operand1) + ", operand2: " + str(operand1) + "")
		_error = "Exception captured. Error: " + str(e) 
		traceback.print_exc()
	return {"output": _output, "error": _error}

def _function(_operation, operand):
	_error = None
	FUNCTIONS = {
		'exp':  lambda a : math.exp(a),
		'sqrt': lambda a : math.sqrt(a),
		'log':  lambda a : math.log(a)
	}
	
	if(isinstance(operand, str)):
		operand = float(operand)

	if("sqrt" in _operation and operand<0):
		_output = "Err"
		_error = "Operand must be zero or bigger"
		return {"output": _output, "error": _error}
	elif("log" in _operation and operand<=0):
		_output = "Err"
		_error = "Operand must by bigger than 0"
		return {"output": _output, "error": _error}
	try: 
		_output = FUNCTIONS[_operation](operand)
	except Exception as e:
		_output = "Err"
		print("Operation not valid: expected 'exp', 'log' or 'sqrt', got : ", str(_operation))
		print("Operation not valid: expected numeric input, got : operand 1: ", str(operand))
		_error = "Exception captured. Error: " + str(e) 
	
	return {"output": _output, "error": _error}


# Compute output of node C15a/65988
#_output_1 = _Data_DischargeLoader(Campaign="C15a", Discharge=65988)

# Compute output of node Crop and resample
#_output_2 = _Data_DischargePreprocessing(_output_1, SamplingPeriod=0.001)

# Compute output of node Radiated power
#_output_3 = _Model_SignalSelection(_output_2, Signal="signal_06", LowerLimit=1000)