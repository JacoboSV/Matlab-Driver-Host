import numpy as np
import os

def get_localUserFile(path):
    base_path = _userDataPath
    filepath = os.path.abspath(base_path + '/' + path)
    #filedata = open(base_path + '/' + path, 'r')
    #data = filedata.read()
    data = np.loadtxt(filepath, delimiter=' ')
    return data
