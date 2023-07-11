function output = {taskName}({parameters},outputWanted)
	error = "";
	output = 'None';
	errorCode = "";
	
	if ~exist('outputWanted','var')
		outputWanted =  'None';
	end
	%if the variable errorCode is defined in this code it will appear if an exception is catched
	{Check params}
	try
		values = run({parametersInFunction}, outputWanted);
		output = values;
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

function [{outputsCode}] = run({parameters},outputWanted)
	% Main user code goes here
	% Do not use "_" when defining variables
	%______________ Code __________________
	#{userCode}
	%________________________________
end