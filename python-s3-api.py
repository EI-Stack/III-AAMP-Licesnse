

import boto
import boto.s3.connection
import pandas as pd
import numpy
import os
import json
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
    jsonobj = json.dumps(jsonobj['targets'][0]['target'])
    jsonobj = jsonobj.replace("\"", "")
    jsonobj = jsonobj.replace("'", "\"")
    jsonobj = json.loads(jsonobj)

    # load value of key for access blob container (bucket)
    ACCESS_KEY = jsonobj['access_key']
    SECRET_KEY = jsonobj['secret_key']
    HOST = jsonobj['host']
    PORT = jsonobj['port']
    BUCKET_NAME = jsonobj['bucket']
    FILE_NAME = jsonobj['filename']

    # establish connection between blob storage and this client app
    s3_connection = boto.connect_s3(
                   aws_access_key_id = ACCESS_KEY,
                   aws_secret_access_key = SECRET_KEY,
                   host = HOST,
                   port = PORT,
                   is_secure=False,               # uncomment if you are not using ssl
                   calling_format = boto.s3.connection.OrdinaryCallingFormat(),
                 )

    # goto bucket and get file accroding to the file name
    # TODO: cache exception if file not exist
    bucket = s3_connection.get_bucket(BUCKET_NAME, validate=False)
    key = bucket.get_key(FILE_NAME)
    key.get_contents_to_filename(FILE_NAME)

    # read bin file and translate it to JSON formate
    bin_data = numpy.fromfile(FILE_NAME, dtype='>d')
    df_file = pd.DataFrame(data = bin_data)

    # delete file which stored in local
    os.remove(FILE_NAME)

    # load 'data' and 'index' in bin file, and append it into a list
    # follow data format from Grafana: https://github.com/grafana/simple-json-datasource/blob/master/README.md
    jsonobj = json.loads(df_file.to_json(orient='split'))
    datapoints_array = []
    for i in range(0, jsonobj['index'][-1]):
        datapoints_array.append([jsonobj['data'][i][0], jsonobj['index'][i]])

    #TODO: group data by mean (or preprocess before data upload to S3
    # construct json array for responding
    dict_data = {}
    dict_data["target"] = FILE_NAME
    dict_data["datapoints"] = datapoints_array
    jsonarr = json.dumps([dict_data])

    return str(jsonarr)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
