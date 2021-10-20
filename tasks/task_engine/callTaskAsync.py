import sys
import getopt
from remoteFolders import remoteFolders
from dataFormats import ioFormatter
from tasks import MatlabTaskCaller, PythonTaskCaller


def main(argv):
	ON_POSIX = 'posix' in sys.builtin_module_names
	sessionID = None
	verbose = True
	taskID = None
	path = None
	ismatlab = True
	isdynamic = False
	try:
			opts, args = getopt.getopt(argv,"ht:a:s:v:i:p:r:m:d:",["task=","args=","session=","verbose=","taskID=","path=","runF=","isMatlab=","isDynamic="])
	except getopt.GetoptError:
			sys.exit(2)
	for opt, arg in opts:
			if opt == '-h':
					print('python callTaskAsync -t <taskName> -a <args> -s <sessionID> -v <verbose> -i <taskID>')
					sys.exit()
			elif opt in ("-t", "--task"):
					task = arg
			elif opt in ("-a", "--args"):
					params = arg
			elif opt in ("-s", "--session"):
					sessionID = arg
			elif opt in ("-v", "--verbose"):
					verbose = arg
			elif opt in ("-i", "--taskID"):
					taskID = arg
			elif opt in ("-m", "--isMatlab"):
					ismatlab = (arg == 'True')
			elif opt in ("-d", "--isDynamic"):
					isdynamic = (arg == 'True')
	
	folderHandler = remoteFolders(taskID)
	formatter = ioFormatter() 
	
	if(ismatlab):
		session = MatlabTaskCaller(taskID,folderHandler, formatter, sessionID = sessionID, verbose = verbose, dynamic = isdynamic)
		#params = session.prepareParameters(params,task)
		session.runTask(task, params)
		session.checkStatus()
	else:
		session = PythonTaskCaller(taskID,folderHandler, formatter, verbose = verbose, dynamic = isdynamic)
		#params = session.prepareParameters(params,task)
		session.runTask(task, params)

if __name__ == "__main__":
	main(sys.argv[1:])
