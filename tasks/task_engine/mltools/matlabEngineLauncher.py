import sys
import matlab.engine
import time
import sys

def main(argv):
		future = matlab.engine.connect_matlab(background=True)
		#eng = future.result()
		# eng.eval('matlab.engine.shareEngine("sharedSession")',nargout=0)
		#eng.matlab.engine.shareEngine(nargout=0)
		
		timeout = time.time() + 24*60*60   # 5 minutes from now
		while True:
			test = 0
			if test == 5 or time.time() > timeout:
					break
			test = test - 1
			time.sleep(10)
			print(time.time())

if __name__ == "__main__":
   main(sys.argv[1:])

