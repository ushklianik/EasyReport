from os import path
from app.backend import pkg
from app.backend.integrations.integration import integration
import os
import requests
import logging
import base64

class grafana(integration):
    def __init__(self, project, name = None):
        super().__init__(project)
        self.set_config(name)

    def __str__(self):
        return f'Integration name is {self.name}, url is {self.server}'

    def set_config(self, name):
        if path.isfile(self.config_path) is False or os.path.getsize(self.config_path) == 0:
            raise Exception('No config.json')
        else:  
            if name == None:
                name = pkg.get_default_grafana(self.project)
            config = pkg.get_grafana_config_values(self.project, name)
            if "name" in config:
                if config['name'] == name:
                    self.name       = config["name"]
                    self.server     = config["server"]
                    self.org_id     = config["org_id"]
                    self.token      = config["token"]
                    self.dashboards = config["dashboards"]
                else:
                    raise Exception(f'No such config name: {name}')

    def get_grafana_link(self, start, end, test_name, dash_id = None):
        if dash_id != None:
            url = self.server + dash_id + '?orgId=' + self.org_id + '&from='+str(start)+'&to='+str(end)+'&var-aggregation=60&var-sampleType=transaction&var-testName='+str(test_name)
        else:
            url = self.server + self.dashboards[0] + '?orgId=' + self.org_id + '&from='+str(start)+'&to='+str(end)+'&var-aggregation=60&var-sampleType=transaction&var-testName='+str(test_name)
        # if "render" not in dash_id:
        #     url = url + "&var-runId="+str(param.current_runId)
        return url  
    
    def get_grafana_test_link(self, start, end, test_name, run_id, dash_id = None):
        url = self.get_grafana_link(start, end, test_name, dash_id)
        url = url+"&var-runId="+run_id
        return url  
    
    def dash_id_to_render(self, dash_id):
        return dash_id.replace("/d/", "/render/d-solo/")
    
    def render_image_encoded(self, graph_name, start, stop, test_name, run_id, baseline_run_id = None):
        image = None
        if (pkg.check_graph(self.project, graph_name)):
            graph_json = pkg.get_graph(self.project, graph_name)
            graph_json["dash_id"] = self.dash_id_to_render(graph_json["dash_id"])
            url = self.get_grafana_link(start, stop, test_name, graph_json["dash_id"]) + "&panelId="+graph_json["view_panel"]+"&width="+graph_json["width"]+"&height="+graph_json["height"]
            if baseline_run_id:
                url = url+"&var-current_runId="+run_id+"&var-baseline_runId="+baseline_run_id
            else:
                url = url+"&var-runId="+run_id
            try:   
                response = requests.get(url=url, headers={ 'Authorization': 'Bearer ' + self.token}, timeout=180)
                if response.status_code == 200:
                    image = base64.b64encode(response.content)
                else:
                    logging.info('ERROR: downloading image from Grafana failed, metric: ' + graph_name)
            except Exception as er:
                logging.warning('ERROR: downloading image from Grafana failed')
                logging.warning(er)
        return image

    def render_image(self, graph_names, start, stop, test_name, run_id, baseline_run_id = None):
        graphs = []
        screenshots = []
        for graph in graph_names:
            graph_json = pkg.get_graph(self.project, graph["name"])
            graph_json["position"] = graph["position"]
            graphs.append(graph_json)
        for graph in graphs:
            if "comparison" in graph["dashId"]:
                url = self.get_grafana_link(start, stop, test_name, graph["dashId"])
                url = url+"&var-current_runId="+run_id+"&var-baseline_runId="+baseline_run_id+"&panelId="+graph["viewPanel"]+"&width="+graph["width"]+"&height="+graph["height"]
            else:
                url = self.get_grafana_link(start, stop, test_name, graph["dashId"])
                url = url+"&var-runId="+run_id+"&panelId="+graph["viewPanel"]+"&width="+graph["width"]+"&height="+graph["height"]
            try:   
                response = requests.get(url=url, headers={ 'Authorization': 'Bearer ' + self.token}, timeout=180)
                if response.status_code == 200:
                    screenshots.append({"image": response.content, "position": graph["position"], "name": graph["name"]})
                else:
                    logging.info('ERROR: downloading image from Grafana failed, metric: ' + graph["name"])
            except Exception as er:
                logging.warning('ERROR: downloading image from Grafana failed')
                logging.warning(er)
        return screenshots