

### Request

`POST /blob/api/v1.0/get_content/`

Post Body

|Key       | Value                                                                       |
|----------|-----------------------------------------------------------------------------|
|access_key| Key to access blob storage, for example: d6dfc3363d0449a1acde32aa844b8c9e   |
|secret_key| Key to identify user's premission, example: d6dfc3363d0449a1acde32aa844b8c9e|
|host      | address of private blob storage, could be a IP address or domain name       |
|port      | port of private blob storage                                                |
|bucket    |bucket name which stored queue content                                       |
|filename  |file to be queue                                                             |

`example: {"access_key":"d6dfc339a1acde32aa844b8c9e", "secret_key":"ef395b3de6bf6490532ced797e", "host":"124.9.xxx.38", "port":xxx, "bucket":"owen_test", "filename":"iris.csv"}`

### TODO
1. Execption catch, such as (1) file does not exist in bucket, (2) bucket does not exist, (3) file is empty or cannot read by Pandas
2. Multiple file queue (cross file queue): in this scenario, usually create an index file after file upload, when Grafana require data, we should queue index to identify file name and bucket at the first stage, then queue the file accroding to result
3. Cloud Foundry App-lization, you should create your own manifest file and push it to WISE-PaaS
