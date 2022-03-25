function output = plotTestMatlab(inner,outputWanted)
	error = "";
	output = 'None';
	errorCode = "";
	
	if ~exist('outputWanted','var')
		outputWanted =  'None';
	end
	%if the variable errorCode is defined in this code it will appear if an exception is catched
	if(~ isa(inner,"list"))
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
		fig = figure(1)
		plot(inner)
		saveas(fig,'./line.png')
		outer = fullfile(pwd,"line.png")
	%________________________________
	
	valuesFromUserCode =  struct('outer',outer);

end