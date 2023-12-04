# Copyright 2023 Uladzislau Shklianik <ushklianik@gmail.com> & Siamion Viatoshkin <sema.cod@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# # Import necessary libraries
# import json
# import requests
# import time
# import sys

# # Variables collected from the Azure pipeline
# INFLUXDB_URL = "$(influxdbURL)"
# INFLUXDB_ORG = "PMI"
# INFLUXDB_BUCKET = "$(applicationTeam)"
# INFLUXDB_TOKEN = "$(influxdbToken)"
# APP = "$(grafanaApplicationName)"
# GRAFANA_LINK = "$(grafanaReportEmailLink)".replace('&amp;', '&')
# JMETER_REPORT_LINK = "$(jmeterReportEmailLink)".replace('&amp;', '&')

# # Parse JSON data
# fIn = open(sys.argv[1])
# data = json.load(fIn)

# # Construct the InfluxDB API URL with the specified parameters
# influxdb_api_url = f"{INFLUXDB_URL}/api/v2/write?org={INFLUXDB_ORG}&bucket={INFLUXDB_BUCKET}&precision=ns"
# headers = {
#     "Authorization": f"Token {INFLUXDB_TOKEN}",
#     "Content-Type": "text/plain"
# }

# # Function to get the latest test title from the designated endpoint
# def get_latest_testtitle():
#     # Define the URL for fetching the latest test title
#     url = 'http://perftest7.pmint.pmihq.org:5000/get-latest-testtitle'
#     params = {
#         'project_name': 'default',
#         'bucket': INFLUXDB_BUCKET,
#         'app': APP
#     }

#     # Send a GET request to retrieve the latest test title
#     response = requests.get(url, params=params)

#     if response.status_code == 200:
#         # Save the fetched test title
#         print(f"Test title: {response.text}")
#         return response.text
#     else:
#         # Print an error message if the request fails
#         print(f"Request failed with status code {response.status_code}")
#         return None

# # Function to send data to InfluxDB
# def send_test_data_to_influxdb(data, TEST_TITLE):
#     data_points = []

#     for transaction, stats in data.items():
#         transaction=transaction.replace(" ", "\\ ")
#         stats['pct90'] = stats.pop('pct1ResTime')
#         stats['pct95'] = stats.pop('pct2ResTime')
#         stats['pct99'] = stats.pop('pct3ResTime')

#         fields = ','.join([f'{key}={value}' for key, value in stats.items() if key != "transaction"])
#         timestamp = int(time.time() * 10**9)
#         if TEST_TITLE:
#             tags = f"application={sys.argv[2]},startTime={sys.argv[3]},releaseId={sys.argv[4]},testTitle={TEST_TITLE}"
#         else:
#             tags = f"application={sys.argv[2]},startTime={sys.argv[3]},releaseId={sys.argv[4]}"

#         data_points.append(f'finalStats,{tags},transaction={transaction} {fields} {timestamp}')

#     payload = '\n'.join(data_points)

#     response = requests.post(influxdb_api_url, headers=headers, data=payload)

#     if response.status_code == 204:
#         print("Data sent to InfluxDB successfully!")
#     else:
#         raise Exception("Failed to send data to InfluxDB. Content: " + str(response.content))

# # Function to send data to InfluxDB
# def send_links_to_influxdb(TEST_TITLE):
    
#     # Prepare the fields, timestamp, and tags for the data payload
#     fields = f'grafanaLink="{GRAFANA_LINK}",jmeterReportLink="{JMETER_REPORT_LINK}"'
#     timestamp = int(time.time() * 10**9)
#     tags = f"application={APP},testTitle={TEST_TITLE}"
#     payload = f'finalStats,{tags} {fields} {timestamp}'

#     # Send a POST request to InfluxDB to store the data
#     response = requests.post(influxdb_api_url, headers=headers, data=payload)

#     if response.status_code == 204:
#         # Print a success message if the data is sent successfully
#         print("Data sent to InfluxDB successfully!")
#     else:
#         # Raise an exception if there's an issue sending data to InfluxDB
#         raise Exception("Failed to send data to InfluxDB. Content: " + str(response.content))

# # Call the function to get the latest test title
# TEST_TITLE = get_latest_testtitle()

# # Call the function to send data to InfluxDB
# send_test_data_to_influxdb(data, TEST_TITLE)

# # Call the function to send links to InfluxDB
# send_links_to_influxdb(TEST_TITLE)