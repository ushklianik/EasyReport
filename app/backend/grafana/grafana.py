from os import path
from app.backend import pkg
import os
import json
import requests
import logging
import base64

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
            config = pkg.getGrafnaConfigValues(self.project, name)
            if "name" in config:
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

    def getGrafanaLink(self, start, end, testName, dashId = None):
        if dashId != None:
            url = self.grafanaServer + dashId + '?orgId=' + self.grafanaOrgId + '&from='+str(start)+'&to='+str(end)+'&var-aggregation=60&var-sampleType=transaction&var-testName='+str(testName)
        else:
            url = self.grafanaServer + self.grafanaDashboard + '?orgId=' + self.grafanaOrgId + '&from='+str(start)+'&to='+str(end)+'&var-aggregation=60&var-sampleType=transaction&var-testName='+str(testName)
        # if "render" not in dash_id:
        #     url = url + "&var-runId="+str(param.current_runId)
        return url  
    
    def getGrafanaTestLink(self, start, end, testName, runId, dashId = None):
        url = self.getGrafanaLink(start, end, testName, dashId)
        url = url+"&var-runId="+runId
        return url  
    
    def renderImageEncoded(self, graphNames, start, stop, testName, runId, baseline_runId = None):
        graphs = []
        screenshots = []
        for graph in graphNames:
            graphJson = pkg.getGraph(self.project, graph["name"])
            graphJson["position"] = graph["position"]
            graphs.append(graphJson)

        for graph in graphs:
            if "comparison" in graph["dashId"]:
                url = self.getGrafanaLink(start, stop, testName, graph["dashId"])
                url = url+"&var-current_runId="+runId+"&var-baseline_runId="+baseline_runId+"&panelId="+graph["viewPanel"]+"&width="+graph["width"]+"&height="+graph["height"]
            else:
                url = self.getGrafanaLink(start, stop, testName, graph["dashId"])
                url = url+"&var-runId="+runId+"&panelId="+graph["viewPanel"]+"&width="+graph["width"]+"&height="+graph["height"]
            try:   
                response = requests.get(url=url, headers={ 'Authorization': 'Bearer ' + self.grafanaToken}, timeout=180)
                if response.status_code == 200:
                    image = base64.b64encode(response.content)
                    screenshots.append({"image": image, "position": graph["position"], "name": graph["name"]})
                else:
                    logging.info('ERROR: downloading image from Grafana failed, metric: ' + graph["name"])
            except Exception as er:
                logging.warning('ERROR: downloading image from Grafana failed')
                logging.warning(er)
        return screenshots

    def renderImage(self, graphNames, start, stop, testName, runId, baseline_runId = None):
        graphs = []
        screenshots = []
        for graph in graphNames:
            graphJson = pkg.getGraph(self.project, graph["name"])
            graphJson["position"] = graph["position"]
            graphs.append(graphJson)

        for graph in graphs:
            if "comparison" in graph["dashId"]:
                url = self.getGrafanaLink(start, stop, testName, graph["dashId"])
                url = url+"&var-current_runId="+runId+"&var-baseline_runId="+baseline_runId+"&panelId="+graph["viewPanel"]+"&width="+graph["width"]+"&height="+graph["height"]
            else:
                url = self.getGrafanaLink(start, stop, testName, graph["dashId"])
                url = url+"&var-runId="+runId+"&panelId="+graph["viewPanel"]+"&width="+graph["width"]+"&height="+graph["height"]
            try:   
                response = requests.get(url=url, headers={ 'Authorization': 'Bearer ' + self.grafanaToken}, timeout=180)
                if response.status_code == 200:
                    screenshots.append({"image": response.content, "position": graph["position"], "name": graph["name"]})
                else:
                    logging.info('ERROR: downloading image from Grafana failed, metric: ' + graph["name"])
            except Exception as er:
                logging.warning('ERROR: downloading image from Grafana failed')
                logging.warning(er)
        return screenshots