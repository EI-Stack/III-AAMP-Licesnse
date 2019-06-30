
# -*- coding: utf-8 -*-

import boto
import boto.s3.connection
from boto.s3.key import Key

import pandas as pd
import numpy as np
import os
import json
import datetime

from flask import Flask
from flask import request
from flask import jsonify

app = Flask(__name__)

@app.route("/", methods=['GET','POST'])
def test_1():
    """
    for simple json.
    official page: should return 200 ok. Used for "Test connection" on the datasource config page.
    """
    str_msg = 'test simple json with /'

    return jsonify({'msg': str_msg}), 200


#@app.route('/blob/api/v1.0/get_content', methods=['POST'])
@app.route('/query', methods=['POST'])
def get_content():

    # retrieve post JSON object
    jsonobj = request.get_json(silent=True)
    print(jsonobj)
    a = int(jsonobj['aamp'])
    
    license_str = 'Vm0weGQxSXhiRmhTV0doVVYwZDRWMWxVU205V2JHeFZVbTFHVjFac2JETlhhMXBQVmxVeFYyTkliRmhoTVVwRVZrZHplRll4VG5GUmJIQk9VbXh2ZWxaclpEUldNVnBXVFZWV2FHVnFRVGs9'
    
    
    return license_str
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
