import requests
from time import sleep

# WAQI info
waqi_token = '12eb788d1022dcc7f7f04c7219f21eec3fcbb9e2'
query = {'token': waqi_token}

# Djanog info
url = 'http://127.0.0.1:8000/api/sensorvalues'
django_token = '9aacaeef2bdc9145a6823938719289567fd9e2e5'
headers = {'Authorization' : 'Token ' + django_token}
while(True):
	response = requests.get('http://api.waqi.info/feed/athens/', params=query)
	#print(response.json())
	json = response.json()
	#print(json["data"]["aqi"])
	aqi_parameter = 1
	aqi_value = json["data"]["aqi"]
	aqi_timestamp = json["data"]["time"]["iso"]

	post_json = { "parameter": aqi_parameter, "value": aqi_value, "timestamp": aqi_timestamp }
	response = requests.post(url, data = post_json, headers=headers)
	print(response.json())
	sleep(60)
