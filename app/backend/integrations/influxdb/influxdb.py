from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from app.backend import pkg
from app.backend.integrations.influxdb.backend_listener import custom
from app.backend.integrations.integration import integration
import logging
import json
from os import path
import os
from datetime import datetime
from dateutil import tz


class influxdb(integration):
    def __init__(self, project, name = None):
        super().__init__(project)
        self.set_config(name)
        self.tmz = tz.tzutc()
    
    def __str__(self):
        return f'Integration name is {self.name}, url is {self.url}'
     
    def set_config(self, name):
        if path.isfile(self.config_path) is False or os.path.getsize(self.config_path) == 0:
            return {"status":"error", "message":"No config.json"}
        else:
            if name == None:
                name = pkg.get_default_influxdb(self.project)
            config = pkg.get_influxdb_config_values(self.project, name)
            if "name" in config:
                if config['name'] == name:
                    self.name        = config["name"]
                    self.url         = config["url"]
                    self.org_id      = config["org_id"]
                    self.token       = config["token"]
                    self.timeout     = config["timeout"]
                    self.bucket      = config["bucket"]
                    self.measurement = config["measurement"]

    def connect_to_influxdb(self):
        try:
            self.influxdb_connection = InfluxDBClient(url=self.url, org=self.org_id, token=self.token)
            msg = {"status":"created", "message":""}
        except Exception as er:
            logging.warning(er)
            msg = {"status":"error", "message":er}
        return self
    
    def close_influxdb_connection(self):
        try:
            self.influxdb_connection.__del__()
        except Exception as er:
            logging.warning('ERROR: influxdb connection closing failed')
            logging.warning(er)

    def get_test_log(self):
        result = []
        try:
            startM = datetime.now().timestamp()
            tables = self.influxdb_connection.query_api().query(custom.get_test_log_query(self.bucket))
            endM = datetime.now().timestamp()
            for table in tables:
                for row in table.records:
                    del row.values["result"]
                    del row.values["table"]
                    result.append(row.values)
            msg = {"status":"good", "message":result}
        except Exception as er:
            logging.warning(er)
            msg = {"status":"error", "message":er}
        return msg

    def send_query(self, query):
        results = []
        flux_tables = self.influxdb_connection.query_api().query(query)
        for flux_table in flux_tables:
            for flux_record in flux_table:
                results.append(flux_record)
        return results
    
    def write_point(self, point):
        self.influxdb_connection.write_api(write_options=SYNCHRONOUS).write(bucket=self.bucket, org=self.org_id, record=point)

    def get_human_start_time(self, run_id):
        flux_tables = self.influxdb_connection.query_api().query(custom.get_start_time(run_id, self.bucket))
        # Influxdb returns a list of tables and rows, therefore it needs to be iterated in a loop
        for flux_table in flux_tables:
            for flux_record in flux_table:               
                tmp = datetime.strftime(flux_record['_time'].astimezone(self.tmz), "%Y-%m-%d %I:%M:%S %p") 
        return tmp

    def get_start_time(self, run_id):
        flux_tables = self.influxdb_connection.query_api().query(custom.get_start_time(run_id, self.bucket))
        # Influxdb returns a list of tables and rows, therefore it needs to be iterated in a loop
        for flux_table in flux_tables:
            for flux_record in flux_table: 
                tmp = datetime.strftime(flux_record['_time'],"%Y-%m-%dT%H:%M:%SZ") 
        return tmp

    def get_start_tmp(self, run_id):
        flux_tables = self.influxdb_connection.query_api().query(custom.get_start_time(run_id, self.bucket))
        # Influxdb returns a list of tables and rows, therefore it needs to be iterated in a loop
        for flux_table in flux_tables:
            for flux_record in flux_table: 
                tmp = int(flux_record['_time'].astimezone(self.tmz).timestamp() * 1000)
        return tmp

    def get_end_tmp(self, run_id):
        flux_tables = self.influxdb_connection.query_api().query(custom.get_end_time(run_id, self.bucket))
        # Influxdb returns a list of tables and rows, therefore it needs to be iterated in a loop
        for flux_table in flux_tables:
            for flux_record in flux_table: 
                tmp = int(flux_record['_time'].astimezone(self.tmz).timestamp() * 1000)
        return tmp

    def get_human_end_time(self, run_id):
        flux_tables = self.influxdb_connection.query_api().query(custom.get_end_time(run_id, self.bucket))
        # Influxdb returns a list of tables and rows, therefore it needs to be iterated in a loop
        for flux_table in flux_tables:
            for flux_record in flux_table: 
                tmp = datetime.strftime(flux_record['_time'].astimezone(self.tmz), "%Y-%m-%d %I:%M:%S %p")
        return tmp

    def get_end_time(self, run_id):
        flux_tables = self.influxdb_connection.query_api().query(custom.get_end_time(run_id, self.bucket))
        # Influxdb returns a list of tables and rows, therefore it needs to be iterated in a loop
        for flux_table in flux_tables:
            for flux_record in flux_table: 
                tmp = datetime.strftime(flux_record['_time'],"%Y-%m-%dT%H:%M:%SZ")                 
        return tmp 

    def get_max_active_users(self, run_id, start, end):
        flux_tables = self.influxdb_connection.query_api().query(custom.get_max_active_users_stats(run_id, start, end, self.bucket))
        # Influxdb returns a list of tables and rows, therefore it needs to be iterated in a loop
        for flux_table in flux_tables:
            for flux_record in flux_table: 
                users = flux_record['_value'] 
        return users  

    def get_test_name(self, run_id, start, end):
        flux_tables = self.influxdb_connection.query_api().query(custom.get_app_name(run_id, start, end, self.bucket))
        for flux_table in flux_tables:
            for flux_record in flux_table: 
                appName = flux_record['testName']
        return appName

    def add_or_update_test(self, run_id, status, build, test_name):
        flux_tables = self.influxdb_connection.query_api().query(custom.get_test_names(run_id, self.bucket))
        is_test_exist = False
        for flux_table in flux_tables:
            for flux_record in flux_table: 
                if run_id == flux_record["runId"]:
                    is_test_exist = True
        if is_test_exist:
            self.delete_test_data("tests", run_id)
            self.add_baseline(run_id, status, build, test_name)
        else:
            self.add_baseline(run_id, status, build, test_name)

    def delete_test_data(self, measurement, run_id, start = None, end = None):
        if start == None: start = "2000-01-01T00:00:00Z"
        else: 
            start = datetime.strftime(datetime.fromtimestamp(int(start)/1000).astimezone(self.tmz),"%Y-%m-%dT%H:%M:%SZ")
        if end   == None: end = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        else: 
            end = datetime.strftime(datetime.fromtimestamp(int(end)/1000).astimezone(self.tmz),"%Y-%m-%dT%H:%M:%SZ")
        try:
            self.influxdb_connection.delete_api().delete(start, end, '_measurement="'+measurement+'" AND runId="'+run_id+'"',bucket=self.bucket, org=self.org_id)
        except Exception as er:
            logging.warning('ERROR: deleteTestPoint method failed')
            logging.warning(er)

    def get_average_rps_stats(self, run_id, start, end):
        flux_tables = self.influxdb_connection.query_api().query(custom.get_average_rps_stats(run_id, start, end, self.bucket))
        # Influxdb returns a list of tables and rows, therefore it needs to be iterated in a loop
        value=""
        for flux_table in flux_tables:
            for flux_record in flux_table: 
                value = round(flux_record['_value'], 2)
        return value

    def get_avg_response_time_stats(self, run_id, start, end):
        flux_tables = self.influxdb_connection.query_api().query(custom.get_avg_response_time_stats(run_id, start, end, self.bucket))
        # Influxdb returns a list of tables and rows, therefore it needs to be iterated in a loop
        value=""
        for flux_table in flux_tables:
            for flux_record in flux_table: 
                value = round(flux_record['_value'], 2)
        return value

    def get_90_response_time_stats(self, run_id, start, end):
        flux_tables = self.influxdb_connection.query_api().query(custom.get_90_response_time_stats(run_id, start, end, self.bucket))
        # Influxdb returns a list of tables and rows, therefore it needs to be iterated in a loop
        value=""
        for flux_table in flux_tables:
            for flux_record in flux_table: 
                value = round(flux_record['_value'], 2)
        return value

    def get_median_response_time_stats(self, run_id, start, end):
        flux_tables = self.influxdb_connection.query_api().query(custom.get_median_response_time_stats(run_id, start, end, self.bucket))
        # Influxdb returns a list of tables and rows, therefore it needs to be iterated in a loop
        value=""
        for flux_table in flux_tables:
            for flux_record in flux_table: 
                value = round(flux_record['_value'], 2)
        return value

    def add_baseline(self, run_id, status, build, test_name):
        self.connect_to_influxdb()
        start_time         = self.get_human_start_time(run_id)
        end_time           = self.get_human_end_time(run_id)
        start_time_infl    = self.get_start_time(run_id)
        end_time_infl      = self.get_end_time(run_id)
        avg_tr             = self.get_avg_response_time_stats(run_id, start_time_infl, end_time_infl)
        percentile_tr      = self.get_90_response_time_stats(run_id, start_time_infl, end_time_infl)
        median_tr          = self.get_median_response_time_stats(run_id, start_time_infl, end_time_infl)
        try:
            p = Point("tests").tag("runId", run_id) \
                    .tag("startTime", start_time).tag("endTime", end_time) \
                    .tag("testName", test_name).tag("status", status) \
                    .tag("build", build) \
                    .field("median_tr", median_tr) \
                    .field("avg_tr", avg_tr) \
                    .field("percentile_tr", percentile_tr)
            self.write_point(p)
        except Exception as er:
            logging.warning('ERROR: baseline stats uploading failed')
            logging.warning(er)