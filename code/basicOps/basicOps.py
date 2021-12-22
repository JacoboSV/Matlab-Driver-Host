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
		'!=': lambda a, b : a != b,
		"maximum": lambda a, b : _numpy.maximum(a, b),
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

def _polishCalculation(operation1, operand1, operand2, operation2=None, operand3=None, operation3=None, operand4=None, operation4=None, operand5=None, operation5=None, operand6=None, operation6=None, operand7=None, operation7=None, operand8=None):
	OPERATIONS = {
		'plus':         lambda a, b : a + b,
		'minus':        lambda a, b : a - b,
		'times':        lambda a, b : a * b,
		'divided by':   lambda a, b : a / b,
		'pow':          lambda a, b : math.pow(a,b),
		'atan2':        lambda a, b : math.atan2(a,b),
		'sqrt':         lambda a : math.sqrt(a),
		'exp':          lambda a : math.exp(a),
		'log':          lambda a : math.log(a),
		'sin':          lambda a : math.sin(a),
		'cos':          lambda a : math.cos(a),
		'tan':          lambda a : math.tan(a),
		'asin':          lambda a : math.asin(a),
		'acos':          lambda a : math.acos(a),
		'atan':         lambda a : math.atan(a),
		}
	_error = None

	operands = [operand1,operand2,operand3,operand4,operand5,operand6,operand7,operand8]
	operations = [operation1,operation2,operation3,operation4,operation5,operation6,operation7]
	#operations = [op for op in operations if op]
	
	counter = len(operations)-1
	for i in range(0,len(operations)):
		if(operations[counter] is not None):
			break
		counter = counter-1
	operations = operations[0:counter+1]
	
	counter = len(operands)-1
	for i in range(0,len(operands)):
		#print("operands[counter]: ",operands[counter])
		if(operands[counter] is not None):
			try: 
				float(operands[counter])
				break
			except:
				operations.append(operands[counter])
				counter = counter - 1 
		else:
			counter = counter - 1 
			
	
	operands = operands[0:counter+1]
	operands = [float(op) for op in operands]
	
	#print(operands)
	#print(operations)
	
	_output = operands.pop()
	next = operands.pop()

	try:
		for i, op in enumerate(operations):
			#print(_output)
			if(op is None or op == 'None'):
				operands.insert(0,_output)
				_output = operands.pop()
			else:
				_output = OPERATIONS[op](next,_output)
				try:
					popped = operands.pop()
					next = popped
				except:
					pass
		
	except Exception as e:
		_output = "Err"
		operationList = ""
		operationList = ",".join([operationList + str(k) for k,v in OPERATIONS.items()])
		print("Operation not valid, expected : ", operationList)
		print("Operation not valid: expected numeric input")
		print(traceback.print_exc())
		_error = "Exception captured. Error: " + str(e) 
	return {"output": _output, "error": _error}
	
