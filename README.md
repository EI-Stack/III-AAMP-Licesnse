

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
|bucket    |bucket name which stored queue content                                       |
|filename  |file to be queue                                                             |

Example
`{
	"panelId": 2, 
	"targets": [
		{
			"target": "{'access_key':'d6dfc3363d0449a1acde32aa844b8c9e', 'secret_key':'ef395b3de653495bbf6490532ced797e', 'host':'124.9.14.38', 'port':8080, 'bucket':'owen_test', 'filename':'test.bin'}", 
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
![image](grafana_create_datasource.PNG =400x)

#### Add a Plotly
![image](grafana_metrics.PNG =400x)
![image](grafana_display_x.PNG =400x)
![image](grafana_display_y.PNG =400x)

#### Result
![image](grafana_outcome.PNG =400x)

### TODO
1. Execption catch, such as (1) file does not exist in bucket, (2) bucket does not exist, (3) file is empty or cannot read by Pandas
2. Multiple file queue (cross file queue): in this scenario, usually create an index file after file upload, when Grafana require data, we should queue index to identify file name and bucket at the first stage, then queue the file accroding to result
3. Cloud Foundry App-lization, you should create your own manifest file and push it to WISE-PaaS

![image](python_read_s3_bin.PNG =400x)
