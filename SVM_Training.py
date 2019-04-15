
# coding: utf-8

# In[1]:


get_ipython().system('pip install afs')


# In[2]:


import requests
import os
import pandas as pd
from pandas.io.json import json_normalize
import numpy as np

from datetime import datetime, timedelta

import warnings
warnings.filterwarnings('ignore')


# In[3]:


now = datetime.now() + timedelta(hours=8)
past = now - timedelta(days=60)

now = now.strftime("%Y-%m-%dT%H:%M:%S.000Z")
past = past.strftime("%Y-%m-%dT%H:%M:%S.000Z")

#Query_from = past
#Query_to =   now

#print(Query_from, Query_to)


# In[4]:


Query_from = '2019-02-01T00:00:00.000Z'
Query_to =   '2019-02-27T00:00:00.000Z'
EQU_NAME = 'ANN 全氫退火爐 #694 循環風扇馬達 A點H向'


# In[5]:


WISE_PAAS_INSTANCE = 'fomos.csc.com.tw'
ENDPOINT_SSO = 'portal-sso'
ENDPOINT_AFS = 'api-afs-develop'
ENDPOINT_APM = 'api-apm-csc-srp'


# In[6]:


payload = dict()
if 'USERNAME' not in os.environ:
    payload['username'] = 'william.cheng@advantech.com.tw'
    payload['password'] = 'Tzukai3038!'


# In[7]:


resp_sso = requests.post('https://' + ENDPOINT_SSO + '.' + WISE_PAAS_INSTANCE + '/v2.0/auth/native', 
                     json=payload,
                     verify=False)

header = dict()
header['content-type'] = 'application/json'
header['Authorization'] = 'Bearer ' + resp_sso.json()['accessToken']


# In[8]:


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

resp_apm_nodeid_json = resp_apm_nodeid.json()
node_id_df = pd.DataFrame(resp_apm_nodeid_json)
node_id_df = node_id_df[['id', 'name']]

apm_nodeid = int(node_id_df.loc[node_id_df['name'] == EQU_NAME]['id'])
apm_nodeid


# In[9]:


APM_TOPO_INFO = 'https://' + ENDPOINT_APM + '.' + WISE_PAAS_INSTANCE + '/topo/node/detail/info'

param = dict()
param['id'] = apm_nodeid

resp_apm_feature = requests.get(APM_TOPO_INFO, 
                     params=param,
                     headers=header,
                     verify=False)

resp_tag = resp_apm_feature.json()['dtInstance']['feature']['monitor']
feature_list = pd.DataFrame(resp_tag)['tag'].str.split('@', expand=True)[2].sort_values()


# In[10]:


EQU_ID = str(resp_apm_feature.json()['dtInstance']['property']['iotSense']['deviceId']).split('@')[2]
EQU_ID


# In[11]:


# HIST_RAW_DATA
APM_HIST = 'https://' + ENDPOINT_APM + '.' + WISE_PAAS_INSTANCE + '/hist/raw/data'

feature_df = pd.DataFrame()

for feature in feature_list:
    payload = dict()
    payload['nodeId'] = apm_nodeid
    payload['sensorType'] = 'monitor'
    payload['sensorName'] = feature
    payload['startTs'] = Query_from
    payload['endTs'] = Query_to

    resp_apm_raw = requests.get(APM_HIST, 
                                params=payload, 
                                headers=header,
                                verify=False)
    
    #print(resp_apm_raw.text)

    df_apm_raw = pd.read_json(resp_apm_raw.text)
    df_apm_raw = json_normalize(df_apm_raw['value'])
    df_apm_raw = df_apm_raw.set_index(pd.DatetimeIndex(df_apm_raw['ts']))
    df_apm_raw = df_apm_raw.drop(columns='ts')
    df_apm_raw = df_apm_raw.rename(columns={'v': feature})

    feature_df = pd.concat([feature_df, df_apm_raw], axis=1, sort=False)
    
    


# In[12]:


APM_EVENT = 'https://' + ENDPOINT_APM + '.' + WISE_PAAS_INSTANCE + '/hist/event'

payload = dict()
payload['nodeId'] = apm_nodeid
payload['count'] = '100'
payload['startTs'] = Query_from
payload['endTs'] = Query_to

resp_apm_event = requests.get(APM_EVENT, 
                              params=payload, 
                              headers=header,
                              verify=False)

resp_apm_event_json = resp_apm_event.json()['documents']
event_df = pd.DataFrame(resp_apm_event_json)
event_df = event_df[['eventTime', 'eventName']]


# In[13]:


feature_df["event"] = ""
feature_df["event"] = 0

for event_time in event_df['eventTime'].unique():
    event = event_df.loc[event_df['eventTime'] == event_time]['eventName']
    
    feature_df.at[event_time, 'event'] = 1

dataset = feature_df.reset_index(drop=True)
#dataset = feature_df
#dataset


# In[14]:


from sklearn.svm import SVC  
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import train_test_split 
from sklearn.externals import joblib 
from sklearn.metrics import classification_report, confusion_matrix  
from sklearn.metrics import accuracy_score
from sklearn.metrics import roc_auc_score
import matplotlib.pyplot as plt
from afs import models


# In[15]:


X = dataset[list(dataset)[1:-2]]
y = dataset[list(dataset)[-1]]
 
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.20) 

svclassifier = SVC(kernel='linear')  
svclassifier.fit(X_train, y_train) 

y_pred = svclassifier.predict(X_test)  

print(confusion_matrix(y_test,y_pred))  
print(classification_report(y_test,y_pred)) 
acc = accuracy_score(y_test, y_pred)
auc = roc_auc_score(y_test, y_pred)


# In[16]:


MODEL_NAME = str(EQU_ID) + '.pkl'

joblib.dump(svclassifier, MODEL_NAME)
afs_models = models()

extra_evaluation = {
    'AUC': auc,
    'date':now
}

afs_models.upload_model(
    model_path = MODEL_NAME, 
    accuracy=acc, 
    loss=1-acc, 
    extra_evaluation=extra_evaluation, 
    model_repository_name=MODEL_NAME)

# Get the latest model info 
#model_info = afs_models.get_latest_model_info(model_repository_name=MODEL_NAME)

