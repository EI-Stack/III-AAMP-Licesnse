

import boto
import boto.s3.connection
import pandas as pd
import os
from flask import Flask
from flask import request





app = Flask(__name__)



@app.route('/blob/api/v1.0/get_content', methods=['POST'])
def get_content():
    # retrieve post JSON object
    jsonobj = request.get_json()

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
    bucket = s3_connection.get_bucket(BUCKET_NAME, validate=False)
    key = bucket.get_key(FILE_NAME)
    key.get_contents_to_filename(FILE_NAME)

    # read file and translate it to JSON formate
    df_file = pd.read_csv(FILE_NAME)

    # delete file which stored in local
    os.remove(FILE_NAME)

    return df_file.to_json(orient='split')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
