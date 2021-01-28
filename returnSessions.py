import sys
import getopt
import os
import matlab.engine
import io

def anySharedSession():
        try:
                return matlab.engine.find_matlab()
        except:
                return None

def main(argv):
        session = ''
        sessionIDs = anySharedSession()
        if(len(sessionIDs)>0):

                print(sessionIDs)


        else:
                print('No session available')

if __name__ == "__main__":
   main(sys.argv[1:])
