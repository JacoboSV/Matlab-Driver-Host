function output = testingArray(inner,outputWanted)
	error = "";
	output = 'None';
	errorCode = "";
	
	if ~exist('outputWanted','var')
		outputWanted =  'None';
	end
	%if the variable errorCode is defined in this code it will appear if an exception is catched
	if(~ isa(inner,"char"))
		error = "Parameter inner is of incorrect type;"
end
	try
		values = run(inner, outputWanted);
		output = checkTypes(values)
	catch e
		output = "Err";
		error = "Exception captured. , User error code: " + e.message ;
	end 
	outStruct = struct('output', output, 'error', error);
	output = jsonencode(outStruct);
end

function rawInputs = checkTypes(rawInputs)
	names = fieldnames(rawInputs)
	for i = 1:numel(names)
		input = rawInputs.(names{i})
		if(isa(input,"char"))
			rawInputs.(names{i}) = strcat('"', input, '"')
		elseif(isa(input,"string"))
			rawInputs.(names{i}) = strcat("'", input, "'")
		else
			rawInputs.(names{i}) = input
		end
	end
end

function valuesFromUserCode = run(inner,outputWanted)
	% Main user code goes here
	% Do not use "_" when defining variables
	%______________ Example __________________
		disp(inner)
		outarray = [1,2,3,3,4,5]
	%________________________________
	
	valuesFromUserCode =  struct('outarray',outarray);

end