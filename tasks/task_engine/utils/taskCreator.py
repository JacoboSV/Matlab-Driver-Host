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
        paramsCheckCode = self._properties_to_code(properties)
        templateFile = open(templatePath + '/template/template.py')
        self.taskFilePath = runpath + "/"
        if not os.path.exists(self.taskFilePath):
            os.makedirs(self.taskFilePath)
        newFile = open(self.taskFilePath +'/'+ name + '.py','w')
        for line in templateFile:
            if('#{userCode}' in line):
                for cline in code.splitlines():
                    newFile.write(line.replace('#{userCode}', '\t'+cline))
            elif('{parameters}' in line):
                newFile.write(line.replace('{parameters}', paramsSTR))
            elif('{parametersInFunction}' in line):
                params_in_call = paramsSTR.replace(' = None','')
                newFile.write(line.replace('{parametersInFunction}', params_in_call))
            elif('{Check params}' in line):
                newFile.write('\n'.join(paramsCheckCode)+'\n')
            elif('#{outputlist}' in line):
                newFile.write(line.replace('#{outputlist}', self._properties_to_outputs(properties)))
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
                propsList.append(prop.get('name') + ' = None')
        paramsSTR = ','.join(propsList)
        return paramsSTR

    def _properties_to_code(self, properties):
        checkcodelines = []
        #print("Properties  ----------------->>  ", properties)
        for prop in properties:
            if('required' in prop.get('attributes') and 'input' in prop.get('attributes')):
                paramType = self._translate_to_pythonTypes(prop.get('type').lower())
                checkcodelines.append('\tif(not isinstance({0},{1})):'.format(prop.get('name'),paramType))
                checkcodelines.append('\t\t_error = "Parameter {0} is of incorrect type"'.format(prop.get('name')))
            elif('input' in prop.get('attributes')):
                paramType = self._translate_to_pythonTypes(prop.get('type').lower())
                checkcodelines.append('\tif({0} is not None and not isinstance({0},{1})):'.format(prop.get('name'),paramType))
                checkcodelines.append('\t\t_error = "Parameter {0} is of incorrect type"'.format(prop.get('name')))
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
            'number': 'float',
            'float': 'float',
            'array': 'list',
            'list': 'list',
            'matrix': 'list',
            'boolean': 'bool',
            'string' : 'str',
            'file'	 : 'str',
            'integer': 'int',
            'ANY' : 'str',
            'OPTION' : 'str',
            'np.array' : 'np.array',
			'pd.series' : 'pd.Series',
			'pd.dataframe': 'pd.DataFrame',
            }
        variableType = type.split('[')[0]
        if(variableType in typeDict):
            return typeDict.get(type.split('[')[0])
        else:
            return 'str'
