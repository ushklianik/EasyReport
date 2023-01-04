from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime
import requests
import base64
import json
import random
import json
import logging
import urllib.parse
from config.parameters import parameters
from checkSLA import compareWithNFRs

param = parameters()

################## Declaring methods #####################
def calculateHeight(current_runId):
    labels_count = getLabelsCount(current_runId)
    height = str(int(int(int(labels_count)+2) * 35.2))
    return height

def putImageToAzure(metric, image, name):
    for i in range(3):
        try:
            response = requests.put(
            url=param.azure_wiki_organization_url + "/"+param.azure_wiki_project+"/_apis/wiki/wikis/"+param.azure_wiki_identifier+"/attachments?name="+name+"&api-version=6.0", headers=param.headers_azure_attachments, data=image)
        except Exception as er:
            logging.warning('ERROR: uploading image to azure failed')
            logging.warning(er)    
        if response.status_code != 201:
            name = str(random.randint(1,100)) + name
        elif response.status_code == 201:
            param.all_images[metric] = name

def getGrafanaLink(dash_id, start_tmp, end_tmp):
    url = param.grafana_server + dash_id + '?orgId=' + param.grafana_orgId + '&from='+str(start_tmp)+'&to='+str(end_tmp)+'&var-aggregation=60&var-sampleType=transaction&var-testName='+str(param.testName)
    if "render" not in dash_id:
        url = url + "&var-runId="+str(param.current_runId)
    return url  

def downloadScreenshot(metric, dash_id, panelId, filename, width, height): 
    # The length of the median response time comparison table is calculated here, this value depends on the number of transactions
    if metric == "Median response time":
        height = calculateHeight(param.current_runId)

    if "comparison" in dash_id:
        url = getGrafanaLink(dash_id, param.current_runId_start_tmp, param.current_runId_end_tmp)
        url = url+"&var-current_runId="+param.current_runId+"&var-baseline_runId="+param.baseline_runId+"&panelId="+panelId+"&width="+width+"&height="+height 
    else:
        url = getGrafanaLink(dash_id, param.current_runId_start_tmp, param.current_runId_end_tmp)
        url = url+"&var-runId="+str(param.current_runId)+"&panelId="+panelId+"&width="+width+"&height="+height
    try:   
        response = requests.get(url=url, headers=param.headers_grafana, timeout=180)
    except Exception as er:
        logging.warning('ERROR: downloading image from Grafana failed')
        logging.warning(er)
    if response.status_code == 200:
            image = base64.b64encode(response.content)
            putImageToAzure(metric, image, filename+".png") 
    else:
        logging.info('ERROR: downloading image from Grafana failed, metric: ' + metric)
    
def getAllScreenshots():
    try:
        screenshots = open('./config/screenshots.json')
        screenshots = json.load(screenshots)
    except Exception as er:
        logging.warning('ERROR: failed to open screenshots.json file')
        logging.warning(er) 
    
    for metrics_source in screenshots:
        if any(x in metrics_source for x in ["ALL", param.testName]):
            for metric in screenshots[metrics_source]:
                downloadScreenshot(metric=metric, 
                    dash_id = screenshots[metrics_source][metric]["dash_id"], 
                    panelId = screenshots[metrics_source][metric]["id"], 
                    filename = param.current_runId + "_" + screenshots[metrics_source][metric]["filename"],
                    width = screenshots[metrics_source][metric]["width"], 
                    height = screenshots[metrics_source][metric]["height"])
    

def createOrUpdatePage(path, page_content):
    content = { "content": page_content }
    wiki_api_url = param.azure_wiki_organization_url + "/"+param.azure_wiki_project+"/_apis/wiki/wikis/"+param.azure_wiki_identifier+"/pages?path="+path+"&api-version=6.0"
    try:
        response = requests.put(
            url=wiki_api_url, headers=param.headers_page,json=content)
    except Exception as er:
        logging.warning('ERROR: failed to upload the page to wiki')
        logging.warning(er)
    if "specified in the add operation already exists in the wiki" in str(response.content):
        try:
            response_get_page = requests.get(
                url=wiki_api_url, headers=param.headers_page)
        except Exception as er:
            logging.warning('ERROR: getting ETag failed')
            logging.warning(er)       
        param.headers_page["If-Match"]=str(response_get_page.headers["ETag"])
        try:
            response = requests.put(
            url=wiki_api_url, headers=param.headers_page,json=content)
        except Exception as er:
            logging.warning('ERROR: failed to update the page in wiki')
            logging.warning(er)    

# Code specificall for PMI
def getFailuresUrl(start_tmp, end_tmp):
    url = param.failures_url[param.testName]
    domain = 'https://portal.azure.com/#blade'
    body = {"filters":[],"timeContext":{"durationMs":0,"createdTime":"","endTime":""},"selectedOperation":"null","experience":1,"roleSelectors":[],"clientTypeMode":"Server"}
    durationMs = int(int(end_tmp)-int(start_tmp))
    createdTime = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000Z')
    endTime = datetime.utcfromtimestamp(int(end_tmp)/1000).strftime('%Y-%m-%dT%H:%M:%S.000Z')
    body["timeContext"]["durationMs"]=durationMs
    body["timeContext"]["createdTime"]=str(createdTime)
    body["timeContext"]["endTime"]=str(endTime)
    body = json.dumps(body)
    url = urllib.parse.quote(url+body)
    return domain+url 
        
def generateReport(current_runId, testName, baseline_runId = None):
    if baseline_runId == None:
        param.baseline_runId = getBaselineRunId(testName) 
    else:
        param.baseline_runId = baseline_runId
    param.current_runId = current_runId
    param.testName = testName
    param.current_runId_start_tmp = getTestStartTime(param.current_runId)
    param.current_runId_end_tmp = getTestEndTime(param.current_runId)
    param.baseline_runId_start_tmp = getTestStartTime(param.baseline_runId)
    param.baseline_runId_end_tmp = getTestEndTime(param.baseline_runId)
    current_test_grafana_link = getGrafanaLink(param.grafana_dashboard, param.current_runId_start_tmp, param.current_runId_end_tmp)
    baseline_test_grafana_link = getGrafanaLink(param.grafana_dashboard, param.baseline_runId_start_tmp, param.baseline_runId_end_tmp)
    current_runId_max_threads = getMaxThreads(param.current_runId)
    baseline_runId_max_threads = getMaxThreads(param.baseline_runId)
    getAllScreenshots()
    azure_wiki_page_name = str(current_runId_max_threads) + " users | Azure candidate | " + str(datetime.utcfromtimestamp(param.current_runId_start_tmp/1000).strftime("%d-%m-%Y %I:%M %p"))
    if param.testName not in param.test_settings:
        thinktimes = ''
    else:
        thinktimes = param.test_settings[param.testName]["thinktimes"]
    azure_wiki_path_final = param.azure_wiki_path + "/" + param.testName + "/" + azure_wiki_page_name
    body = '''##Status: `To fill in manually`\n'''
    body += compareWithNFRs(param.testName, param.current_runId)
    body +='''
[[_TOC_]]

# Summary
 - To fill in manually

# Test settings
|vUsers| Ramp-up period | Duration | Think-times | Start time | End time | Comments | Grafana dashboard |
|--|--|--|--|--|--|--|--|
|'''+str(current_runId_max_threads)+''' |600 sec|'''+str(int((param.current_runId_end_tmp/1000)-(param.current_runId_start_tmp/1000)))+''' sec |''' + thinktimes + '''|'''+str(datetime.utcfromtimestamp(param.current_runId_start_tmp/1000).strftime("%d-%m-%Y %I:%M %p"))+''' UTC |'''+str(datetime.utcfromtimestamp(param.current_runId_end_tmp/1000).strftime("%d-%m-%Y %I:%M %p"))+''' UTC | Current test | [Grafana link]('''+current_test_grafana_link+''') |
|'''+str(baseline_runId_max_threads)+''' |600 sec|'''+str(int((param.baseline_runId_end_tmp/1000)-(param.baseline_runId_start_tmp/1000)))+''' sec |''' + thinktimes + '''|'''+str(datetime.utcfromtimestamp(param.baseline_runId_start_tmp/1000).strftime("%d-%m-%Y %I:%M %p"))+''' UTC |'''+str(datetime.utcfromtimestamp(param.baseline_runId_end_tmp/1000).strftime("%d-%m-%Y %I:%M %p"))+''' UTC | Baseline test | [Grafana link]('''+baseline_test_grafana_link+''') |
---
'''
    for image in param.all_images:
        if not "Graphql response time" in image:
            body = body + '''\n'''
            body = body + '''## ''' + str(image)
            body = body + '''\n'''
            body = body + '''![image.png](/.attachments/''' + str(param.all_images[image]) + ''')'''
            body = body + '''\n'''
            body = body + '''\n'''
            
    body += '''## Failures | [Link](''' + getFailuresUrl(param.current_runId_start_tmp, param.current_runId_end_tmp) + ''')'''
    body = body + '''\n'''

    if param.testName == "SPX":
        current_graphql = ''''''
        baseline_graphql = ''''''
        
        body = body + '''\n'''
        body = body + '''## Graphql response time'''
        body = body + '''\n'''
        
        for image in param.all_images:
            if "Graphql response time" in image:               
                if "current" in image:
                    current_graphql = '''![image.png](/.attachments/''' + str(param.all_images[image]) + ''')'''
                elif "baseline" in image:
                    baseline_graphql = '''![image.png](/.attachments/''' + str(param.all_images[image]) + ''')'''
        
        
        body += '''
|Current test| Baseline test | 
|--|--|
|'''+current_graphql+'''|'''+baseline_graphql+'''|'''

    body = body + param.envConfig[param.testName]
    createOrUpdatePage(azure_wiki_path_final, body)