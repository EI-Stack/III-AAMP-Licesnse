
# -*- coding: utf-8 -*-

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

import requests

from flask import Flask
from flask import request
from flask import jsonify
from influxdb import DataFrameClient

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
    
    SAMPLE_RATE = 8192
    DISPLAY_POINT = 65536
    
    # retrieve post JSON object
    jsonobj = request.get_json(silent=True)
    target_obj = jsonobj['targets'][0]['target']
    date_obj = jsonobj['range']['from']
    date_obj = date_obj.split('T')[0]

    EQU_NAME = target_obj.split('@')[0]
    FEATURE = target_obj.split('@')[1]
    TYPE = target_obj.split('@')[2]
    DATE = date_obj.replace("-", "/")

    print('EQU_NAME=' + EQU_NAME)
    print('Feature=' + FEATURE)
    print('Type=' + TYPE)
    print('Date=' + DATE)
    
    EQU_ID = convert_equ_name(EQU_NAME)
    print('EQU_ID='+EQU_ID)
    TS = query_timestamp(TYPE, FEATURE, EQU_ID, DATE)
    print(type(TS), TS)
    ## TODO Retrive bin file

    # load value of key for access blob container (bucket)
    ACCESS_KEY = 'cc0b4b06affd4f599dff7607f1556811'
    SECRET_KEY = 'U7fxYmr8idml083N8zo7JRddXiNbyCmNN'
    HOST = '192.168.123.226'
    PORT = 8080
    BUCKET_NAME = 'FOMOS-Y5'
    FILE_NAME = 'Raw Data-1-1Y510110100-06-29-06_8192.bin'
    ID_MACHINE = 'smartbox11 Signal Data'
    #ID_TAG = '1Y510110100'
    #S3_PATH = '2018/11/18'




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
    PATH_DEST = ID_MACHINE + '/' + EQU_ID + '/' + TS.strftime('%Y/%m/%d') + '/'
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

def combine_return (TIME_START, TIME_DELTA, BIN_DF, BIN_LENGTH){
    return jsonarr
}
    

def query_timestamp (TYPE, feature, ChannelName, date):
    
    ## InfluxDB Configuration
    IDB_HOST = '192.168.123.240'
    IDB_PORT = 8086
    IDB_DBNAME = '3243ffc7-76ab-4c5f-a248-ad1ccd68849e'
    IDB_USER = '9f5b4165-abce-4be7-92f6-20126ad3130b'
    IDB_PASSWORD = 'RoKZUtYYOK45cqEmhn6k1XniY'

    #TODO Calculate from-to datetime
    ## Query InfluxDB
    measurement, data = read_influxdb_data(host = IDB_HOST,
                                       port = IDB_PORT,
                                       dbname = IDB_DBNAME,
                                       ChannelName = ChannelName,
                                       time_start = '2019-02-25',
                                       time_end = '2019-02-26',
                                       user = IDB_USER,
                                       password = IDB_PASSWORD
                                      )

    if TYPE == 'max':
        max_value = data[feature].max()
    elif TYPE == 'mean':
        max_value = data[feature].mean()
    else:
        max_value = data[feature].min()

    ## Retrive timestamp
    index_series = data[feature]
    dt64 = index_series[index_series == max_value].index.values[0]
    TS = datetime.datetime.utcfromtimestamp(dt64.tolist()/1e9)

    return TS


def convert_equ_name (EQU_NAME):
    
    ## Connection Information
    WISE_PAAS_INSTANCE = 'fomos.csc.com.tw'
    ENDPOINT_SSO = 'portal-sso'
    ENDPOINT_APM = 'api-apm-csc-srp'

    payload = dict()
    payload['username'] = 'william.cheng@advantech.com.tw'
    payload['password'] = 'Tzukai3038!'


    ## Get Token through SSO Login
    resp_sso = requests.post('https://' + ENDPOINT_SSO + '.' + WISE_PAAS_INSTANCE + '/v2.0/auth/native', 
                     json=payload,
                     verify=False)

    header = dict()
    header['content-type'] = 'application/json'
    header['Authorization'] = 'Bearer ' + resp_sso.json()['accessToken']


    ## Get NodeID by EQU_NAME
    APM_NODEID = 'https://' + ENDPOINT_APM + '.' + WISE_PAAS_INSTANCE + '/topo/progeny/node'

    param = dict()
    param['topoName'] = 'MAIN_CSC'
    param['path'] = '/'
    param['type'] = 'layer'
    param['layerName'] = 'Machine'

    resp_apm_nodeid = requests.get(APM_NODEID, 
                     params=param,
                     headers=header,
                     verify=False)

    ## Retrive NodeID
    resp_apm_nodeid_json = resp_apm_nodeid.json()
    node_id_df = pd.DataFrame(resp_apm_nodeid_json)
    node_id_df = node_id_df[['id', 'name']]

    apm_nodeid = int(node_id_df.loc[node_id_df['name'] == EQU_NAME]['id'])
    

    ## Get EQU_ID by NodeID
    APM_TOPO_INFO = 'https://' + ENDPOINT_APM + '.' + WISE_PAAS_INSTANCE + '/topo/node/detail/info'

    param = dict()
    param['id'] = apm_nodeid

    resp_apm_feature = requests.get(APM_TOPO_INFO, 
                     params=param,
                     headers=header,
                     verify=False)

    ## Retrive EQU_ID
    resp_tag = resp_apm_feature.json()['dtInstance']['feature']['monitor']
    feature_list = pd.DataFrame(resp_tag)['tag'].str.split('@', expand=True)[2].sort_values()
    EQU_ID = str(resp_apm_feature.json()['dtInstance']['property']['iotSense']['deviceId']).split('@')[2]

    return EQU_ID


def get_bin ():
    return bin_df



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

def read_influxdb_data(host='192.168.123.245', 
                       port=8086, 
                       dbname = 'c9377a95-82f3-4af3-ac14-40d14f6d2abe', 
                       ChannelName='1Y520210100', 
                       time_start='', 
                       time_end='', 
                       user = 'a1555b8e-6148-4ef0-af5b-c2195ac4ecd7', 
                       password = 'ENbC4hwn1OedsIH6yvO8X4EqJ',
                       keyword=''):
    
    #Example: read_influxdb_data(ChannelName='1Y520210200')
    #Example: read_influxdb_data(ChannelName='1Y520210200',time_start='2018-05-28',time_end='2018-05-29')
    client = DataFrameClient(host, port, user, password, dbname)
    measurements = client.get_list_measurements()
    
    if keyword is None: keyword = ''
        
    if keyword=='':
        measurement = [mea.get(u'name') for mea in measurements if mea.get(u'name').find(ChannelName)>=0]
    else:
        measurement = [mea.get(u'name') for mea in measurements if mea.get(u'name').find(ChannelName)>=0 and mea.get(u'name').find(keyword)>=0]
    
    if len(measurement)==0: 
        print('No data retrieved.')
        return None
    
    measurement = measurement[-1]
    
    time_end = 'now()' if time_end=='' else "'" + time_end + ' 15:59:00' + "'"
    #print(time_end)
    
    time_start = 'now()' if time_start=='' else "'" + time_start + ' 16:00:00' + "'"
    #print(time_start)
    
    querystr = 'select * from "{}" where time > {} and time < {}'.format(measurement,time_start,time_end)
    #print(querystr)
    
    df = client.query(querystr).get(measurement)
    client.close()
    
    if df is None: 
        print('No data retrieved.')
        return None    
    
    dff = df.groupby('id')
    columns = [name for name, group in dff]
    groups = [group['val'] for name, group in dff]
    
    #check datatime alginment: all([all(groups[i].index==groups[0].index) for i in range(1,len(groups))])
    result = pd.concat(groups,axis=1)
    result.columns = columns
    result.index = groups[0].index
    
    print('data between {} and {} are retrieved, dimension: {}x{}'.format(time_start,time_end,result.shape[0],result.shape[1]))
    
    return measurement, result

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
