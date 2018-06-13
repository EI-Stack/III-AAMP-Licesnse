

### Request

`POST|GET /`

For Grafana test connection

`POST /query`

Post Body

|Key       | Value                                                                       |
|----------|-----------------------------------------------------------------------------|
|access_key| Key to access blob storage, for example: d6dfc3363d0449a1acde32aa844b8c9e   |
|secret_key| Key to identify user's premission, example: d6dfc3363d0449a1acde32aa844b8c9e|
|host      | address of private blob storage, could be a IP address or domain name       |
|port      | port of private blob storage                                                |
|bucket    | bucket name which stored queue content                                      |
|filename  | file to be queue                                                            |
|sid       | ID of Smart Machine Box, ex. smartbox11 signal Data                         |
|tag       | ID of tag, ex. 1Y510110100                                                  |
|date      | date, ex. 2018/6/10, 2018/10/6                                              |

Example
`{
	"panelId": 2, 
	"targets": [
		{
			"target": "{'access_key':'d6dfc3363d0449a1acde32aa844b8c9e', 'secret_key':'ef395b3de653495bbf6490532ced797e', 'host':'124.9.14.38', 'port':8080, 'bucket':'FOMOS-Y5', 'filename':'Raw Data-1-1Y510110100-00-01-12_8192.bin', 'sid':'smartbox11 signal Data', 'tag':'1Y510110100', 'date':'2018/6/10'}", 
			"refId": "A", "type": "timeserie"
		}
	], 
	"range": {"from": "2018-05-15T06:40:57.454Z", "to": "2018-05-15T12:40:57.454Z", 
	"raw": {"from": "now-6h", "to": "now"}}, 
	"intervalMs": 30000, 
	"interval": "30s", 
	"maxDataPoints": 683, 
	"scopedVars": {"__interval": {"text": "30s", "value": "30s"}, 
	"__interval_ms": {"text": 30000, "value": 30000}}, 
	"rangeRaw": {"from": "now-6h", "to": "now"}, 
	"timezone": "browser"
}`

### Configure Grafana

#### Add Datasource
![image](images/grafana_create_datasource.PNG)

#### Add a Plotly
![image](images/grafana_metrics.PNG)

![image](images/grafana_display_x.PNG)

![image](images/grafana_display_y.PNG)

#### Result
![image](images/grafana_outcome.PNG)

### TODO
1. Execption catch, such as (1) file does not exist in bucket, (2) bucket does not exist, (3) file is empty or cannot read by Pandas
2. Multiple file queue (cross file queue): in this scenario, usually create an index file after file upload, when Grafana require data, we should queue index to identify file name and bucket at the first stage, then queue the file accroding to result
3. Cloud Foundry App-lization, you should create your own manifest file and push it to WISE-PaaS

![image](python_read_s3_bin.PNG =400x)
