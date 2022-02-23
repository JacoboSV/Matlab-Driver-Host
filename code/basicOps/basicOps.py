import os as _os
import pandas as _pandas
import uuid as _uuid
import numpy as _numpy
import matplotlib.pyplot as _matplotlib_pyplot
import scipy.io
import json
import math
import traceback

def _tester(input1, input2, input3, input4):
	#===========================================================================
	# print("input1",input1)
	# print("input2",input2)
	# print("input3",input3)
	# print("input4",input4)
	#===========================================================================
	a = input1
	b = input2
	c = input3
	d = input4
	_output = (a,b,c,d)
	
	_error = "None"
	return {"output": _output, "error": _error}

def _operation(Operation, Operand1, Operand2):
	_error = None
	#print("Operation: ",Operation)
	#print("Operand1: ",Operand1)
	#print("Operand2: ",Operand2)
	if(isinstance(Operand1, str) or isinstance(Operand2, str)):
		Operand1 = float(Operand1)
		Operand2 = float(Operand2)
		
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

	if("divided by" in Operation):
		if (Operand2==0):
			_output = "Err"
			_error = "Operand 2 can't be 0"
			return {"output": [_output], "error": _error}
	
	try: 
		_output = OPERATIONS[Operation](Operand1, Operand2)
	except Exception as e:
		_output = "Err"
		print("Operation not valid: expected 'plus', 'minus', 'times', 'divided by', <,>,= or != got : ", str(Operation))
		print("Operation not valid: expected numeric inputs, got : operand 1: " + str(Operand1) + ", Operand2: " + str(Operand1) + "")
		_error = "Exception captured. Error: " + str(e) 
		traceback.print_exc()
	return {"output": [_output], "error": _error}

def _function(Operation, Operand):
	_error = None
	FUNCTIONS = {
		'exp':  lambda a : math.exp(a),
		'sqrt': lambda a : math.sqrt(a),
		'log':  lambda a : math.log(a)
	}
	
	if(isinstance(Operand, str)):
		Operand = float(Operand)

	if("sqrt" in Operation and Operand<0):
		_output = "Err"
		_error = "Operand must be zero or bigger"
		return {"output": [_output], "error": _error}
	elif("log" in Operation and Operand<=0):
		_output = "Err"
		_error = "Operand must by bigger than 0"
		return {"output": [_output], "error": _error}
	try: 
		_output = FUNCTIONS[Operation](Operand)
	except Exception as e:
		_output = "Err"
		print("Operation not valid: expected 'exp', 'log' or 'sqrt', got : ", str(Operation))
		print("Operation not valid: expected numeric input, got : Operand 1: ", str(Operand))
		_error = "Exception captured. Error: " + str(e) 
	
	return {"output": [_output], "error": _error}

def _polishCalculation(Operation1, Operand1, Operand2, Operation2=None, Operand3=None, Operation3=None, Operand4=None, Operation4=None, Operand5=None, Operation5=None, Operand6=None, Operation6=None, Operand7=None, Operation7=None, Operand8=None):
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

	operands = [Operand1,Operand2,Operand3,Operand4,Operand5,Operand6,Operand7,Operand8]
	operations = [Operation1,Operation2,Operation3,Operation4,Operation5,Operation6,Operation7]
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
	return {"output": [_output], "error": _error}
	
