

import boto
import boto.s3.connection
from boto.s3.key import Key

import pandas as pd
import numpy as np
import os
import json
import datetime

import binascii
import struct

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
    #jsonobj = jsonobj.replace("'", "\"")
    #jsonobj = json.loads(jsonobj)

    EQU_NAME = jsonobj.split('@')[0]
    FEATURE = jsonobj.split('@')[1]
    TYPE = jsonobj.split('@')[2]

    print(EQU_NAME)
    print(FEATURE)
    print(TYPE)

    jsonobj = request.get_json(silent=True)
    jsonobj = json.dumps(jsonobj['range']['from'])
    jsonobj = jsonobj.split('T')[0]
    jsonobj = jsonobj.replace("\"", "")
    DATE = jsonobj.replace("-", "/")
    print(DATE)

    # load value of key for access blob container (bucket)
    ACCESS_KEY = 'cc0b4b06affd4f599dff7607f1556811'
    SECRET_KEY = 'U7fxYmr8idml083N8zo7JRddXiNbyCmNN'
    HOST = '192.168.123.226'
    PORT = 8080
    BUCKET_NAME = 'FOMOS-Y5'
    FILE_NAME = 'Raw Data-1-1Y510110100-06-29-06_8192.bin'
    ID_MACHINE = 'smartbox11 Signal Data'
    ID_TAG = '1Y510110100'
    #S3_PATH = jsonobj['date']
    S3_PATH = '2018/11/18'
    SAMPLE_RATE = 8192
    DISPLAY_POINT = 65536


    # establish connection between blob storage and this client app
    s3_connection = boto.connect_s3(
                   aws_access_key_id = ACCESS_KEY,
                   aws_secret_access_key = SECRET_KEY,
                   host = HOST,
                   port = PORT,
                   is_secure=False,               # uncomment if you are not using ssl
                   calling_format = boto.s3.connection.OrdinaryCallingFormat(),
                 )
    bucket = s3_connection.get_bucket(BUCKET_NAME, validate=False)

    # goto bucket and get file accroding to the file name
    PATH_DEST = ID_MACHINE + '/' + ID_TAG + '/' + S3_PATH + '/'
    s3_bin_data = os.path.join(PATH_DEST, FILE_NAME)
    print(s3_bin_data)
    key = bucket.get_key(s3_bin_data)

    try:
        key.get_contents_to_filename(FILE_NAME)
    except:
        return 'File not found'

    # get metadata (timestamp)
    #bucket = s3_connection.get_bucket(BUCKET_NAME, validate=False)
    #key = Key(bucket)
    #remote_key = bucket.get_key(s3_bin_data)
    #key_timestamp = remote_key.metadata
    #key_timestamp = key_timestamp['ts']
    #print('timestamp = ' + key_timestamp['ts'])
    
    # read bin file and translate it to JSON formate
    #df_file_mean, file_length = convert_bin(FILE_NAME, 'mean', DISPLAY_POINT)
    #df_file_max, file_length = convert_bin(FILE_NAME, 'max', DISPLAY_POINT)
    #df_file_min, file_length = convert_bin(FILE_NAME, 'min', DISPLAY_POINT)
    df_file, file_length = convert_bin(FILE_NAME, DISPLAY_POINT)

    # calculate start-time and end-time
    #TIME_START = datetime.datetime.fromtimestampint(int(key_timestamp)).strftime('%Y-%m-%d %H:%M:%S')

    date_list = s3_bin_data.split("/")
    date = date_list[2] + '-' + date_list[3] + '-' + date_list[4]
    time_list = s3_bin_data.split("/")[5].split("-")
    time = time_list[3] + ':' + time_list[3] + ':' + time_list[5].split("_")[0]
    key_timestamp = date + ' ' + time

    #TIME_START = int(datetime.datetime.strptime(key_timestamp, '%Y-%m-%d %H:%M:%S').strftime('%s')) * 1000
    TIME_START = int(datetime.datetime.strptime(DATE, '%Y/%m/%d').strftime('%s')) * 1000
    TIME_DELTA = float(float(file_length / SAMPLE_RATE) / DISPLAY_POINT) * 1000
    #TIME_DELTA = 0.1220703125
    print ('TIME_START', TIME_START)

    # deTIME_DELTAfile which stored in local
    os.remove(FILE_NAME)

    # load 'data' and 'index' in bin file, and append it into a list
    # follow data format from Grafana: https://github.com/grafana/simple-json-datasource/blob/master/README.md
    jsonobj_mean = json.loads(df_file.to_json(orient='split'))
    #jsonobj_max = json.loads(df_file_max.to_json(orient='split'))
    #jsonobj_min = json.loads(df_file_min.to_json(orient='split'))

    datapoints_array_mean = []
    #datapoints_array_max = []
    #datapoints_array_min = []
    for i in range(0, DISPLAY_POINT):
        datapoints_array_mean.append([jsonobj_mean['data'][i][0], TIME_START])
        #datapoints_array_mean.append([jsonobj_mean['data'][i][0], i])
        #datapoints_array_max.append([jsonobj_max['data'][i][0], TIME_START])
        #datapoints_array_min.append([jsonobj_min['data'][i][0], TIME_START])

        TIME_START = float(TIME_START) + TIME_DELTA


    # construct json array for API response
    dict_data_mean = {}
    dict_data_mean["target"] = 'original'
    dict_data_mean["datapoints"] = datapoints_array_mean
    #dict_data_max = {}
    #dict_data_max["target"] = 'max'
    #dict_data_max["datapoints"] = datapoints_array_max
    #dict_data_min = {}
    #dict_data_min["target"] = 'min'
    #dict_data_min["datapoints"] = datapoints_array_min

    #jsonarr = json.dumps([dict_data_mean, dict_data_max, dict_data_min])
    jsonarr = json.dumps([dict_data_mean])

    return str(jsonarr)
    #return str(df_file.index.values)


#def convert_bin (filename, pd_type, DISPLAY_POINT):
def convert_bin (filename, DISPLAYPOINT):
    bytes_read = open(filename, "rb").read()
    size = [hexint(bytes_read[(i*4):((i+1)*4)]) for i in range(2)]
    signal = [struct.unpack('f',bytes_read[(i*4):((i+1)*4)]) for i in range(2,2+size[0]*size[1])]
    data = np.array(signal).reshape(size)
    return_df = pd.DataFrame(data = data)
    return_df = return_df.T
    file_length = len(return_df)

    length = file_length / DISPLAYPOINT

    #if pd_type == 'mean':
    #    return_df = return_df.groupby(np.arange(len(return_df))/length).mean()
    #elif pd_type == 'max':
    #    return_df = return_df.groupby(np.arange(len(return_df))/length).max()
    #else:
    #    return_df = return_df.groupby(np.arange(len(return_df))/length).min()

    #print(len(return_df))

    return return_df, file_length


def hexint(b,bReverse=True): 
    return int(binascii.hexlify(b[::-1]), 16) if bReverse else int(binascii.hexlify(b), 16)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
