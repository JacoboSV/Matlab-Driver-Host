import os
import json
import traceback

class TaskCreator(object):

    def __init__(self):
        pass

    def createTask(self, name, properties, code, templatePath, runpath):
        '''Creates a file to run the node code from a template. 
        ----------
        properties : List
            COntain the names of the outputs that the graph expect
        code : string
            Information about the error
        '''
        paramsSTR = self._properties_to_params(properties)
        outsSTR = self._properties_to_outputs(properties)
        paramsCheckCode = self._properties_to_code(properties)
        templateFile = open(templatePath + '/template/template.m')
        self.taskFilePath = runpath + "/"
        if not os.path.exists(self.taskFilePath):
            os.makedirs(self.taskFilePath)
        newFile = open(self.taskFilePath +'/'+ name + '.m','w')
        for line in templateFile:
            if('#{userCode}' in line):
                for cline in code.splitlines():
                    newFile.write(line.replace('#{userCode}', '\t'+cline))
            elif('{parameters}' in line):
                line = line.replace('{parameters}', paramsSTR)
                if('{taskName}' in line):
                    line = line.replace('{taskName}', name)
                if('{outputsCode}' in line):
                    line = line.replace('{outputsCode}', outsSTR)
                newFile.write(line)
            # elif('{outputsCode}' in line):
            #     newFile.write(line.replace('{outputsCode}', outsSTR))
            elif('{parametersInFunction}' in line):
                params_in_call = paramsSTR.replace(' = None','')
                newFile.write(line.replace('{parametersInFunction}', params_in_call))
            elif('{Check params}' in line):
                newFile.write('\n'.join(paramsCheckCode)+'\n')
            else:
                newFile.write(line)
        newFile.close()
        templateFile.close()
        return {'error': False, 'errorCode': ''}

    def _properties_to_params(self, properties):
        propsList = []
        for prop in properties:
            if('required' in prop.get('attributes') and 'input' in prop.get('attributes')):
                propsList.append(prop.get('name'))
            elif('input' in prop.get('attributes')):
                propsList.append(prop.get('name'))
        paramsSTR = ','.join(propsList)
        return paramsSTR

    def _properties_to_code(self, properties):
        checkcodelines = []
        #print("Properties  ----------------->>  ", properties)
        # for prop in properties:
        #     if('required' in prop.get('attributes') and 'input' in prop.get('attributes')):
        #         paramType = self._translate_to_pythonTypes(prop.get('type'))
        #         checkcodelines.append('\tif(~ isa({0},{1}))'.format(prop.get('name'),paramType))
        #         checkcodelines.append('\t\terror = "Parameter {0} is of incorrect type;"'.format(prop.get('name')))
        #         checkcodelines.append('end')
        #     elif('input' in prop.get('attributes')):
        #         paramType = self._translate_to_pythonTypes(prop.get('type'))
        #         checkcodelines.append('\tif(exist("{0}","var") & ~ isa({0},{1}))'.format(prop.get('name'),paramType))
        #         checkcodelines.append('\t\terror = "Parameter {0} is of incorrect type;"'.format(prop.get('name')))
        #         checkcodelines.append('end')
        return checkcodelines

    def _properties_to_outputs(self,properties):
        propsList = []
        for prop in properties:
            if('output' in prop.get('attributes')):
            #if('required' in prop.get('attributes') and 'output' in prop.get('attributes')):
                propsList.append(prop.get('name'))
        outsSTR = ','.join(propsList)
        return outsSTR


    def _translate_to_pythonTypes(self, type):
        #TO DO: File must be checked also as a existing File or a existing File identifier
        typeDict = {
            'number': '"float"',
            'array': '"double"',
            'list': '"double"',
            'matrix': '"double"',
            'boolean': '"logical"',
            'string' : '"char"',
            'file'	 : '"char"',
            'integer': '"integer"',
            'OPTION' : '"char"' 
        }
        variableType = type.split('[')[0]
        if(variableType in typeDict):
            return typeDict.get(type.split('[')[0])
        else:
            return 'char'




# @app.task
# def createTask(name, properties, code):
# 	try:	
# 		paramsSTR = _properties_to_params(properties)
# 		outsSTR = _properties_to_outputs(properties)
# 		paramsCheckCode = _properties_to_code(properties)
# 		templateFile = open('code/template/template.m')
# 		if not os.path.exists('code/'+name):
# 			os.makedirs('code/'+name)
# 		newFile = open('code/'+name +'/'+ name + '.m','w')
# 		for line in templateFile:
# 			if('#{userCode}' in line):
# 				for cline in code.splitlines():
# 					newFile.write(line.replace('#{userCode}', '\t'+cline))
# 			elif('{parameters}' in line):
# 				line = line.replace('{parameters}', paramsSTR)
# 				if('{taskName}' in line):
# 					newFile.write(line.replace('{taskName}', name))
# 				else:
# 					newFile.write(line)
# 			elif('#{outputsCode}' in line):
# 				newFile.write(line.replace('#{outputsCode}', outsSTR))
# 			elif('{parametersInFunction}' in line):
# 				params_in_call = paramsSTR.replace(' = None','')
# 				newFile.write(line.replace('{parametersInFunction}', params_in_call))
# 			elif('{Check params}' in line):
# 				newFile.write('\n'.join(paramsCheckCode)+'\n')
# 			else:
# 				newFile.write(line)
# 		newFile.close()
# 		templateFile.close()
# 		return {'error': False, 'errorCode': ''}
# 	except Exception as e:
# 		print('Exception when creating new task')
# 		print(traceback.format_exc())
# 		return {'error': True, 'errorCode': str(e)}

# def _properties_to_outputs(properties):
# 	propsList = []
# 	for prop in properties:
# 		if('required' in prop.get('attributes') and 'output' in prop.get('attributes')):
# 			propsList.append("'" + prop.get('name') + "'," + prop.get('name'))
# 	outsSTR = 'struct('+ ','.join(propsList)+')'
# 	return outsSTR

# def _properties_to_params(properties):
# 	propsList = []
# 	for prop in properties:
# 		if('required' in prop.get('attributes') and 'input' in prop.get('attributes')):
# 			propsList.append(prop.get('name'))
# 		elif('input' in prop.get('attributes')):
# 			propsList.append(prop.get('name'))
# 	paramsSTR = ','.join(propsList)
# 	return paramsSTR

# def _properties_to_code(properties):
# 	checkcodelines = []
# 	#===========================================================================
# 	# checkTypeDict= {
# 	# 	'python': 'not isinstance',
# 	# 	'matlab': '~ isa',
# 	# 	}
# 	#===========================================================================
# 	for prop in properties:
# 		if('required' in prop.get('attributes') and 'input' in prop.get('attributes')):
# 			paramType = _translate_to_pythonTypes(prop.get('type'))
# 			checkcodelines.append('\tif(~ isa({0},{1}))'.format(prop.get('name'),paramType))
# 			checkcodelines.append('\t\terror = "Parameter {0} is of incorrect type;"'.format(prop.get('name')))
# 			checkcodelines.append('end')
# 		elif('input' in prop.get('attributes')):
# 			paramType = _translate_to_pythonTypes(prop.get('type'))
# 			checkcodelines.append('\tif(exist("{0}","var") & ~ isa({0},{1}))'.format(prop.get('name'),paramType))
# 			checkcodelines.append('\t\terror = "Parameter {0} is of incorrect type;"'.format(prop.get('name')))
# 			checkcodelines.append('end')
# 	return checkcodelines


# def _translate_to_pythonTypes(type):
# 	#TO DO: File must be checked also as a existing File or a existing File identifier
# 	typeDict = {
# 		'number': '"float"',
# 		'array': '"double"',
# 		'list': '"double"',
# 		'matrix': '"double"',
# 		'boolean': '"logical"',
# 		'string' : '"char"',
# 		'file'	 : '"char"',
# 		'integer': '"integer"',
# 		'OPTION' : '"char"' 
# 		}
# 	return typeDict.get(type.split('[')[0])