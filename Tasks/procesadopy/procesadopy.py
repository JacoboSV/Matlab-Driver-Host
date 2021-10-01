import os as _os
import pandas as _pandas
import uuid as _uuid
import numpy as _numpy
import matplotlib.pyplot as _matplotlib_pyplot
import scipy.io
import json

# --- Function definitions for node C15a/65988
# def _Data_DischargeLoader (_input=None, Campaign=None, Discharge=None, DataDir="data/Campaigns/", _display=False):
	# '''
		# Loads data of a given campaign and discharge and fills in a DataFrame
		# - _input" can be a dict of two types:
			# { 'filename' , 'skiprows'} indicating a single csv file with a DataFrame with all signals indexed with the same time
			# { 'campaign', 'discharge' } for a set of files, each with a signal with perhaps different times
		# - _input can be None, in which case Campaign and Discharge parametres are used as substitue of the second dict type
			# '''
	# _frame = None
	# _filename = None
	
	# if _input is not None:
		
		# if 'filename' in _input:
			# _filename = _input['filename']
			# if 'skiprows' in _input:
				# _skiprows = _input['skiprows']
			# else:
				# _skiprows = 0
			# _frame = pd.read_csv(DataDir+str(_filename),skiprows=_skiprows)
		
		# else: # try dict with campaing and discharge  
			# if 'campaign' in _input:
				# Campaign = _input['campaign']
			# if 'discharge' in _input:
				# Discharge = _input['discharge']

	# if _frame is None:
		# Campaign  = str(Campaign)
		# Discharge = str(Discharge)
	
	# _dir = DataDir+Campaign+"/"
	# _files=[]
	# with _os.scandir(_dir) as _iterator:
		# for _entry in _iterator:
			# if _entry.is_file() and Discharge+'_' in _entry.name:
				# _name = _entry.name.split('.')[0]
				# _signal = _name.split('_')[-1]
				# _files.append( { "signal" : _signal, "file" : _entry.name}) 
	
	# _files = sorted(_files, key=lambda k: k['signal']) 

	# _list = []
	# for _entry in _files:
		# _file   = _entry['file']
		# _signal = _entry['signal']
		# _data = _pandas.read_csv(_dir+_file, sep=" ", header=None, skipinitialspace=True)
		# _data.columns = ['time_'+_signal, 'signal_'+_signal]
		# _list.append(_data)

	# _frame = _pandas.concat(_list, axis=1)

	# if (_display):
		# if _filename is not None:
			# print ("<h2>Data from file "+_filename+"</h2>")
		# else: 
			# print ("<h2>Data for discharge "+Discharge+" in campaign "+Campaign+"</h2>")
		# print (_frame)

	# return _frame

# --- Function definitions for node Crop and resample

# def _Data_DischargePreprocessing (_input, SamplingPeriod=0.001, _display=False):
	# '''
		# Converts a DataFrame with columns 'time_xxx', 'signal_xxx' ... into a DataFrame
		# with the same time frame and cols 'signal_xxx' ...
		# The time fram spans from the common minimum to the commom maximum and is sampled at a given period 
	# '''
	
	# _list = []
	# _tmin = -1
	# _tmax = float("inf")

	# for _col in _input:
		# if _col.startswith('time_'):
			# _signal = _col[5:]
			# _data = _input[[_col, 'signal_'+_signal]].dropna()
			# _tmin = max(_tmin,_data[_col].min())
			# _tmax = min(_tmax,_data[_col].max())
			# _data.set_index(_col,inplace=True)
			# _list.append(_data)

	# _time = _numpy.arange(_tmin,_tmax,SamplingPeriod)

	# for _index, _data in enumerate(_list):
		# _data = _data.reindex(_data.index.union(_time))
		# _data.interpolate(method='values',inplace=True)
		# _list[_index] = _data.reindex(_time)

	# _frame = _pandas.concat(_list, axis=1)

	# if (_display):
	   # print ("<h2>Discharge data preprocessed from input</h2>")
	   # print ("<h3>Samplig period = "+str(SamplingPeriod)+"</h3>")
	   # print (_frame)

	# return _frame

# def _Model_MaxFromFile(**_kwargs):
	# for _key, _value in _kwargs.items():
		# if _key=="numdescarga":
			# _discharge = _value
		# elif _key== "numsignal":
			# _featureStyle = _value
		# elif _key== "namesignal":
			# _signal = _value
		# elif _key== "d_r":
			# _dir = _value
	
	# _data = _pandas.read_csv(_dir+_discharge, sep=" ", header=None, skipinitialspace=True)
	
	# _list.append(_data)
	
def _Model_SeriesFeature(_matFile, Feature='max'):
	mat = scipy.io.loadmat(_matFile)
	_discharge = str(_pandas.Series(mat['numdescarga'][0])[0])
	_dir = str(_pandas.Series(mat['d_r'][0])[0])
	_signal = str(_pandas.Series(mat['numsignal'][0])[0])
	_prefix = 'DES_'
	_textFile = '.txt'
	_path2file = _dir + _prefix + _discharge + '_0' + _signal + '_r' + _textFile
	if('signal' not in mat.keys()):
		_data = _pandas.read_csv(_path2file, sep=" ", header=None, skipinitialspace=True)
	else:
		_data = _pandas.DataFrame(mat['signal'])
	_data.columns = ['time_'+_signal, 'signal_'+_signal]
	if Feature=='min':
		_index = _data['signal_'+_signal].idxmin()
	elif Feature=='max':
		_index = _data['signal_'+_signal].idxmax()
		
	if _index is None:
		_output = _pandas.DataFrame()
	else:
		_featurePoint = [_data['time_'+_signal][_index], _data['signal_'+_signal][_index]]
		_output = {'signal': [_data.values.tolist()], 'features': _featurePoint}
	return _output

# --- Function definitions for node Radiated power

# def _Model_SignalSelection(_input=None, Signal=None, UpperLimit=None, UpperValue=None, LowerLimit=None, LowerValue=None, _display=False):
	# '''
	# Selects a signal from the discharge DataFrame and optionally saturates it
	# '''
	# if _input is None:
		# return _pandas.Series()

	# if Signal is None:
		# return _pandas.Series()
	
	# #_key = "signal "+"{0:0=2d}".format(Signal)
	# _series = _input[Signal]
	
	# if UpperLimit is not None:
		# if UpperValue is None:
			# UpperValue = UpperLimit
		# _series[_series > UpperLimit] = UpperValue

	# if LowerLimit is not None:
		# if LowerValue is None:
			# LowerValue = LowerLimit
		# _series[_series < LowerLimit] = LowerValue

	# if (_display):
		# print ("<h2>Series after saturation for "+ Signal+"</h2>")
		# print (_series)

	# return _series

	

# # --- Function definitions for node Maximum

# def _Model_SeriesFeature(_input=None, Feature='max', _display=False):
	
	# if _input is None:
		# _output =  { "index" : None, "value": None }

	# if Feature=='min':
		# _index = _input.idxmin()
	# elif Feature=='max':
		# _index = _input.idxmax()
	# else:
		# _index = None

	# if _index is None:
		# _output = { "index" : None, "value": None }
	# else:
		# _output = { "index" : _index, "value": _input[_index] }
	
	# if (_display):
		# print ("<h2>Series "+Feature+":</h2>")
		# print ("<h3>Value: ",_output['value'],"</h3>")
		# print ("<h3>Index: ",_output['index'],"</h3>")

	# return _output


	

# # --- Function definitions for node Plot signal and max

def _Visualization_SeriesFeaturePlot(*_inputs, **_kwargs):
	'''
		Creates a plot of a series and (optionally) a feature
	'''
	_matplotlib_pyplot.rcParams['figure.figsize'] = [20, 10]
	_matplotlib_pyplot.rcParams['figure.dpi'] = 300
			
	_title = None
	_featureStyle = "ro"
	_markerSize = 10
	_display=None
	
	for _key, _value in _kwargs.items():
		if _key=="Title":
			_title = _value
		elif _key== "FeatureStyle":
			_featureStyle = _value
		elif _key== "MarkerSize":
			_markerSize = _value
		elif _key== "_display":
			_display = _value
			
		# prepare a plot with subplots in a column
	_matplotlib_pyplot.clf()
	
	if _title is None:
		_matplotlib_pyplot.title('Plot of series and feature')
	else:
		_matplotlib_pyplot.title(_title)
	
	for _input in _inputs: 
		if isinstance(_input, _pandas.Series):
			_matplotlib_pyplot.plot(_input,'b')
		elif isinstance(_input, dict):
			_matplotlib_pyplot.plot(_pandas.DataFrame(_input['signal'][0]),'b')
		elif isinstance(_input, str):
			jsondata = json.loads(_input)
			signal = _pandas.DataFrame(jsondata['signal'][0])
			_matplotlib_pyplot.plot(signal[0],signal[1],'b')
			_matplotlib_pyplot.plot(jsondata['features'][0],jsondata['features'][1],'ro')
			_matplotlib_pyplot.plot(jsondata['features'][0],jsondata['features'][0],'bo')
			
	_outputFile = "./_plot"+str(_uuid.uuid4())+".jpg"
	_matplotlib_pyplot.savefig(_outputFile);
	_matplotlib_pyplot.close()

	#_output = "<img src='"+_outputFile+"' alt='Plot' width='100%' height='50%'>"
	if (_display):
		print (_output)
	
	return {}



# Compute output of node C15a/65988
#_output_1 = _Data_DischargeLoader(Campaign="C15a", Discharge=65988)

# Compute output of node Crop and resample
#_output_2 = _Data_DischargePreprocessing(_output_1, SamplingPeriod=0.001)

# Compute output of node Radiated power
#_output_3 = _Model_SignalSelection(_output_2, Signal="signal_06", LowerLimit=1000)