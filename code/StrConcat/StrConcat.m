function output = StrConcat(str1,str2,outputWanted)
	error = "";
	output = 'None';
	errorCode = "";
	
	if ~exist('outputWanted','var')
		outputWanted =  'None';
	end
	%if the variable errorCode is defined in this code it will appear if an exception is catched
	if(~ isa(str1,"char"))
		error = "Parameter str1 is of incorrect type;"
end
	if(~ isa(str2,"char"))
		error = "Parameter str2 is of incorrect type;"
end
	try
		values = run(str1,str2, outputWanted);
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



function valuesFromUserCode = run(str1,str2,outputWanted)
	% Main user code goes here
	% Do not use "_" when defining variables
	%______________ Code __________________
		disp(str1)
		disp(str2)
		strout = strcat(str1,str2)
	%________________________________
	
	valuesFromUserCode =  struct('strout',strout);

end