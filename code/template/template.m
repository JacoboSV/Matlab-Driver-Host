function output = userMethod({parameters},outputWanted):
	error = "";
	output = 'None';
	errorCode = "";
	
	if ~exist('outputWanted','var')
		outputWanted =  'None';
	end
	%if the variable errorCode is defined in this code it will appear if an exception is catched
	{Check params}
	try:
		output = run({parametersInFunction}, outputWanted);
	catch e
		output = "Err";
		error = "Exception captured. , User error code: " + e.message ;
	end 
	outStruct = struct('output', output, 'error', error);
	output = jsonencode(outStruct);
	return output
end

function values = run({parameters},outputWanted):
	outputs = 'None';
	% Main user code goes here
	% Do not use "_" when defining variables
	%______________ Example __________________
	outputs = {};
	#{userCode}
	%________________________________
	
	if(strcmp(outputWanted,'None'))
		values =  outputs;
	else
		values = outputs[outputWanted];
	end
end