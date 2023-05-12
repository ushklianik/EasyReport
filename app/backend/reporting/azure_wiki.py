from app.backend import pkg
from app.backend.integrations.grafana.grafana import grafana
from app.backend.integrations.influxdb.influxdb import influxdb
from app.backend.integrations.azure.azure import azure
import re

class azureport:

    def __init__(self, project, report_name):
        self.project        = project
        self.report_name    = report_name
        self.set_config()
        self.grafana_obj    = grafana(project=self.project, name=self.grafana_name)
        self.influxdb_obj   = influxdb(project=self.project, name=self.influxdb_name).connect_to_influxdb()
        self.output_obj     = azure(project=self.project, name=self.output_name)
        self.progress       = 0
        self.status         = "Not started"

    def set_config(self):
        config = pkg.get_flow_config_values_in_dict(self.project, self.report_name)
        self.influxdb_name = config["influxdb_name"]
        self.grafana_name  = config["grafana_name"]
        self.output_name   = config["output_name"]  
        self.graphs        = config["graphs"]
        self.footer        = config["footer"]
        self.header        = config["header"]
    
    def generate_report(self, current_run_id, baseline_run_id = None):
        self.current_start_time         = self.influxdb_obj.get_start_time(current_run_id)
        self.current_end_time           = self.influxdb_obj.get_end_time(current_run_id)
        self.current_start_timestamp    = self.influxdb_obj.get_start_tmp(current_run_id)
        self.current_end_timestamp      = self.influxdb_obj.get_end_tmp(current_run_id)
        self.test_name                  = self.influxdb_obj.get_test_name(current_run_id, self.current_start_time, self.current_end_time)

        self.parameters = {}
        self.parameters["test_name"]                = self.test_name
        self.parameters["current_start_time"]       = self.influxdb_obj.get_human_start_time(current_run_id)
        self.parameters["current_end_time"]         = self.influxdb_obj.get_human_end_time(current_run_id)
        self.parameters["current_grafana_link"]     = self.grafana_obj.get_grafana_test_link(self.current_start_timestamp, self.current_end_timestamp, self.test_name, current_run_id)
        self.parameters["current_duration"]         = str(int((self.current_end_timestamp - self.current_start_timestamp)/1000))
        self.parameters["current_vusers"]           = self.influxdb_obj.get_max_active_users(current_run_id, self.current_start_time, self.current_end_time)
        
        if baseline_run_id != None:
            self.current_start_time                 = self.influxdb_obj.get_start_time(baseline_run_id)
            self.baseline_end_time                  = self.influxdb_obj.get_end_time(baseline_run_id)
            self.baseline_end_time                  = self.influxdb_obj.get_start_tmp(baseline_run_id)
            self.baseline_end_time                  = self.influxdb_obj.get_end_tmp(baseline_run_id)

            self.parameters["baseline_start_time"]   = self.influxdb_obj.get_human_start_time(baseline_run_id)
            self.parameters["baseline_end_time"]     = self.influxdb_obj.get_human_end_time(baseline_run_id)
            self.parameters["baseline_grafana_link"] = self.grafana_obj.get_grafana_test_link(self.baseline_end_time, self.baseline_end_time, self.test_name, baseline_run_id)
            self.parameters["baseline_duration"]     = str(int((self.baseline_end_time - self.baseline_end_time)/1000))
            self.parameters["baseline_vusers"]       = self.influxdb_obj.get_max_active_users(baseline_run_id, self.current_start_time, self.baseline_end_time)
        
        self.influxdb_obj.close_influxdb_connection()

        self.status = "Collected data from InfluxDB"
        self.progress = 25

        screenshots = self.grafana_obj.render_image_encoded(self.graphs, self.current_start_timestamp, self.current_end_timestamp, self.test_name, current_run_id, baseline_run_id)
        self.status = "Rendered images in Grafana"
        self.progress = 50

        for screenshot in screenshots:
            fileName = self.output_obj.put_image_to_azure(screenshot["image"], screenshot["name"])
            screenshot["filename"] = fileName

        self.status = "Uploaded images to Azure"
        self.progress = 75

        wikiPageName = str(self.parameters["current_vusers"]) + " users | Azure candidate | " + self.parameters["current_startTime"]
        wikiPagePath = self.output_obj.get_path() + wikiPageName
        
        variables = re.findall(r"\$\{(.*?)\}", self.header)
        for var in variables:
            self.header = self.header.replace("${"+var+"}", str(self.parameters[var]))
        
        variables = re.findall(r"\$\{(.*?)\}", self.footer)
        for var in variables:
            self.footer = self.footer.replace("${"+var+"}", str(self.parameters[var]))
     
        body = self.header

        for idx in range(len(screenshots)):
            for screenshot in screenshots:
                if idx == screenshot["position"]:
                    body = body + '''\n'''
                    body = body + '''## ''' + str(screenshot["name"])
                    body = body + '''\n'''
                    body = body + '''![image.png](/.attachments/''' + str(screenshot["filename"]) + ''')'''
                    body = body + '''\n'''
                    body = body + '''\n'''

        body += self.footer

        self.output_obj.create_or_update_page(wikiPagePath, body)

        self.status = "Created Azure page"
        self.progress = 100