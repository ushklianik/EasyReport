from app.backend import pkg
from app.backend.integrations.grafana.grafana import grafana
from app.backend.integrations.influxdb.influxdb import influxdb
from app.backend.validation.validation import NFR
import re

class reporting_base:

    def __init__(self, project):
        self.project        = project
        self.progress       = 0
        self.status         = "Not started"
        self.validation_obj = NFR(project)

    def __del__(self):
        self.influxdb_obj.close_influxdb_connection()

    def set_template(self, template):
        template_obj = pkg.get_template_values(self.project, template)
        flow_name    = template_obj["flow"]
        self.title   = template_obj["title"]
        self.data    = template_obj["data"]
        self.set_flow(flow_name)
        self.grafana_obj    = grafana(project=self.project, name=self.grafana)
        self.influxdb_obj   = influxdb(project=self.project, name=self.influxdb).connect_to_influxdb()

    def set_template_group(self, template_group):
        template_group_obj     = pkg.get_template_group_values(self.project, template_group)
        self.group_title             = template_group_obj["title"]
        self.template_order    = template_group_obj["data"]

    def add_appdex(self):
        return self.validation_obj.calculate_apdex(self.test_name, self.current_run_id)

    def get_template_data(self, template):
        template_obj = pkg.get_template_values(self.project, template)
        return template_obj["data"]

    def set_flow(self, flow_name):
        flow          = pkg.get_flow_values(self.project, flow_name)
        self.influxdb = flow["influxdb"]
        self.grafana  = flow["grafana"]
        self.output   = flow["output"]

    def replace_variables(self, text):
        variables = re.findall(r"\$\{(.*?)\}", text)
        for var in variables:
            text = text.replace("${"+var+"}", str(self.parameters[var]))
            if var == "appdex":
                text = text.replace("${"+"appdex"+"}", str(self.add_appdex()))
        return text

    def collect_data(self, current_run_id, baseline_run_id = None):
        self.current_run_id             = current_run_id
        self.baseline_run_id            = baseline_run_id
        self.current_start_time         = self.influxdb_obj.get_start_time(current_run_id)
        self.current_end_time           = self.influxdb_obj.get_end_time(current_run_id)
        self.current_start_timestamp    = self.influxdb_obj.get_start_tmp(current_run_id)
        self.current_end_timestamp      = self.influxdb_obj.get_end_tmp(current_run_id)
        self.test_name                  = self.influxdb_obj.get_test_name(current_run_id, self.current_start_time, self.current_end_time)

        self.parameters = {}
        self.parameters["test_name"]                 = self.test_name
        self.parameters["current_start_time"]        = self.influxdb_obj.get_human_start_time(current_run_id)
        self.parameters["current_end_time"]          = self.influxdb_obj.get_human_end_time(current_run_id)
        self.parameters["current_grafana_link"]      = self.grafana_obj.get_grafana_test_link(self.current_start_timestamp, self.current_end_timestamp, self.test_name, current_run_id)
        self.parameters["current_duration"]          = str(int((self.current_end_timestamp - self.current_start_timestamp)/1000))
        self.parameters["current_vusers"]            = self.influxdb_obj.get_max_active_users(current_run_id, self.current_start_time, self.current_end_time)
        
        if baseline_run_id != None:
            self.baseline_start_time                 = self.influxdb_obj.get_start_time(baseline_run_id)
            self.baseline_end_time                   = self.influxdb_obj.get_end_time(baseline_run_id)
            self.baseline_start_timestamp            = self.influxdb_obj.get_start_tmp(baseline_run_id)
            self.baseline_end_timestamp              = self.influxdb_obj.get_end_tmp(baseline_run_id)

            self.parameters["baseline_start_time"]   = self.influxdb_obj.get_human_start_time(baseline_run_id)
            self.parameters["baseline_end_time"]     = self.influxdb_obj.get_human_end_time(baseline_run_id)
            self.parameters["baseline_grafana_link"] = self.grafana_obj.get_grafana_test_link(self.baseline_start_timestamp, self.baseline_end_timestamp, self.test_name, baseline_run_id)
            self.parameters["baseline_duration"]     = str(int((self.baseline_end_timestamp - self.baseline_start_timestamp)/1000))
            self.parameters["baseline_vusers"]       = self.influxdb_obj.get_max_active_users(baseline_run_id, self.baseline_start_time, self.baseline_end_time)

        self.status = "Collected data from InfluxDB"
        self.progress = 25