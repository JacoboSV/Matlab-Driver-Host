import os as _os
import json
import traceback


def methodName1(param1):
	_error = "Code do nothing"
	_output = None
	_output = {"output": _output, "error": _error}
	errorCode = ""
	try:
		# Main user code here 
		# If errorCode is defined in this code it will appear if an exception is catched
		
		
		
		_output = "This is a template"
		# _output will carry the result of this function
	except Exception as e:
		_output = "Err"
		print(traceback.print_exc())
		_error = "Exception captured. Error: " + str(e) + ", User error code: " + errorCode 
	
	return {"output": _output, "error": _error}
