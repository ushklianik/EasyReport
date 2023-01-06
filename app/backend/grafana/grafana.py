from os import path
from app.backend import pkg
import os
import json

class grafana:
    def __init__(self, project, name = None):
        self.project                    = project
        self.path                       = "./app/projects/" + project + "/config.json"
        self.setConfig(name)
    
    def setConfig(self, name):
        if path.isfile(self.path) is False or os.path.getsize(self.path) == 0:
            return {"status":"error", "message":"No config.json"}
        else:   
            if name == None:
                name = pkg.getDefaultGrafana(self.project)
            with open(self.path, 'r') as fp:
                fl = json.load(fp)
                for config in fl["integrations"]["grafana"]:
                    if config['name'] == name:
                        self.name                      = config["name"]
                        self.grafanaServer             = config["grafanaServer"]
                        self.grafanaToken              = config["grafanaToken"]
                        self.grafanaDashboard          = config["grafanaDashboard"]
                        self.grafanaOrgId              = config["grafanaOrgId"]
                        self.grafanaDashRenderPath     = config["grafanaDashRenderPath"]
                        self.grafanaDashRenderCompPath = config["grafanaDashRenderCompPath"]
                    else:
                        return {"status":"error", "message":"No such config name"}

    def getGrafanaLink(self, dashId, start, end, testName):
        url = self.grafanaServer + dashId + '?orgId=' + self.grafanaOrgId + '&from='+str(start)+'&to='+str(end)+'&var-aggregation=60&var-sampleType=transaction&var-testName='+str(testName)
        # if "render" not in dash_id:
        #     url = url + "&var-runId="+str(param.current_runId)
        return url  
    
    def renderImage(self, metricNames):
        metrics = []
        for metricName in metricNames:
            

        # if "comparison" in dash_id:
        #     url = getGrafanaLink(dash_id, param.current_runId_start_tmp, param.current_runId_end_tmp)
        #     url = url+"&var-current_runId="+param.current_runId+"&var-baseline_runId="+param.baseline_runId+"&panelId="+panelId+"&width="+width+"&height="+height 
        # else:
        #     url = getGrafanaLink(dash_id, param.current_runId_start_tmp, param.current_runId_end_tmp)
        #     url = url+"&var-runId="+str(param.current_runId)+"&panelId="+panelId+"&width="+width+"&height="+height
        # try:   
        #     response = requests.get(url=url, headers=param.headers_grafana, timeout=180)
        # except Exception as er:
        #     logging.warning('ERROR: downloading image from Grafana failed')
        #     logging.warning(er)
        # if response.status_code == 200:
        #         image = base64.b64encode(response.content)
        #         putImageToAzure(metric, image, filename+".png") 
        # else:
        #     logging.info('ERROR: downloading image from Grafana failed, metric: ' + metric)