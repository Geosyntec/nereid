from flask import Flask
import json
import socket

import numpy
import pandas
import scipy
from scipy import linalg
from scipy.spatial import Delaunay

app = Flask(__name__)

def test_numpy():
    arr = numpy.array([1.5, 2, 8])

    return arr

def test_pandas():
    df = pandas.Series(test_numpy(), name='pd_data')
    return df

def test_scipy_linalg():
    A = numpy.array([[1,2],[3,4]])
    res = linalg.inv(A)

    return A, res

def test_scipy_spatial():
    points = numpy.array([[0, 0], [0, 1.1], [1, 0], [1, 1]])
    tri = Delaunay(points)

    return points, tri


def get_Host_name_IP(): 
    try: 
        host_name = socket.gethostname() 
        host_ip = socket.gethostbyname(host_name) 

        return {
            "hostname": host_name,
            "ip_address": host_ip
        }

    except: 
        print("Unable to get Hostname and IP") 



@app.route('/')
def hello_world():

    tdf = test_pandas()
    tarr = test_numpy()

    a, res = test_scipy_linalg()
    pts, tri = test_scipy_spatial()

    info = {
        "app_name": 'nereid',
        "app_version": '0.0.2', 
        "test_"+tdf.name: tdf.to_list(),
        "test_"+'numpy_arr': tarr.tolist(),
        "test_"+'linalg_inv': res.tolist(),
        "test_"+'delaunay': tri.simplices.ravel().tolist(),
    }

    info.update(get_Host_name_IP())
    
    _json = json.dumps(
        info,
        sort_keys=True,
        indent=4,
    )

    rsp = "<pre>{}</pre>"
    
    return rsp.format(_json)

if __name__ == '__main__':
    app.run()