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

import json

from app                                                           import config_path
from app.backend                                                   import pkg
from app.backend.integrations.secondary.influxdb                   import Influxdb
from app.backend.integrations.secondary.influxdb_backend_listeners import custom
from os.path                                                       import isfile, getsize


class Nfr:

    def __init__(self, project):
        self.project      = project
        self.path_to_nfrs = config_path
        self.comparison   = {}

    def save_nfrs(self, nfrs):
        pkg.save_nfrs(self.project, nfrs)

    def delete_nfrs(self, name):
        pkg.delete_nfr(self.project, name)

    # Method returns NFRs for specific application
    def get_nfr(self, name):
        return pkg.get_nfr(self.project, name)

    # Method reqturns all NFRs for all applications
    def get_nfrs(self):
        return pkg.get_nfrs(self.project)


    # Method accepts test value, operation and threshold
    # Compares value with treshold using specified operation
    # Returns PASSED or FAILED status
    @staticmethod
    def compare_value(value, operation, threshold):
        try:
            if isinstance(value, (int, float)) and isinstance(threshold, (int, float)):
                if operation == '>':
                    return "PASSED" if value > threshold else "FAILED"
                elif operation == '<':
                    return "PASSED" if value < threshold else "FAILED"
                elif operation == '==':
                    return "PASSED" if value == threshold else "FAILED"
                elif operation == '!=':
                    return "PASSED" if value != threshold else "FAILED"
                elif operation == '>=':
                    return "PASSED" if value >= threshold else "FAILED"
                elif operation == '<=':
                    return "PASSED" if value <= threshold else "FAILED"
            else:
                return "threshold is not a number"
        except TypeError:
            return "value is not a number"

    # Method generates name based on NFR definition, for example:
    # NFR: {"scope": "all","metric": "response-time","aggregation": "95%-tile","operation": ">","threshold": 4000}
    # Name: 95%-tile response-time for all requests is greater than 4000
    def generate_name(self, nfr_row):
        name = f"{nfr_row['aggregation'].capitalize()} {nfr_row['metric']} "
        if nfr_row['scope'] == 'all':
            name += 'for all requests '
        elif nfr_row['scope'] == 'each':
            name += 'for each request '
        else:
            name += f"for {nfr_row['scope']} request "
        operations = {
            '>': 'is greater than',
            '<': 'is less than',
            '==': 'is equal to',
            '!=': 'is not equal to',
            '>=': 'is greater than or equal to',
            '<=': 'is less than or equal to'
        }
        name += f"{operations[nfr_row['operation']]} {nfr_row['threshold']}"
        return name

    def is_float(self, string):
        try:
            float(string)
            return True
        except ValueError:
            return False

    # Method takes a list of NFRs 
    # Constructs a flux request to the InfluxDB based on the NFRs
    # Takes test data and compares it with the NFRs
    def compare_with_nfrs(self, test_name, run_id, start = None, end = None):
        comp_result        = []
        total_weight       = 0
        empty_weight_count = 0
        try:
            # Get NFRs for the specific application
            nfrs = self.get_nfr(test_name)
            # Create InfluxDB connection
            influxdb_obj = Influxdb(self.project).connect_to_influxdb()
            if start == None:
                start = influxdb_obj.get_start_time(run_id)
            if end == None:
                end = influxdb_obj.get_end_time(run_id)
            # Iterate through NFRs
            for nfr in nfrs["rows"]:
                # Generate flux query to get test data based on NFR definition
                query   = influxdb_obj.generate_flux_query(test_name, run_id, start, end, influxdb_obj.bucket, nfr)
                # Get test data to compare with NFR
                results = influxdb_obj.send_query(query)
                # If InfluxDB query returns 0 rows
                if len(results) == 0:
                    name = self.generate_name(nfr)
                    comp_result.append({"name": name, "result": "no data"})
                # If InfluxDB query returns 1 row
                elif len(results) == 1:
                    name = self.generate_name(nfr)
                    comp_result.append({"name": name, "result": self.compare_value(results[0]['_value'], nfr['operation'],nfr['threshold']),"value": str(results[0]['_value']),"weight": str(nfr['weight'])})
                # If InfluxDB query returns more than 1 row
                elif len(results) > 1:
                    if nfr['weight'].isnumeric():
                        if nfr['weight'] != "":
                            nfr['weight'] = float(nfr['weight'])/len(results)
                    # If one request doesn't meet the threshold, the whole NFR will be failed
                    for result in results:
                        nfr["scope"] = result['transaction']
                        name         = self.generate_name(nfr)
                        comp_result.append({"name": name, "result": self.compare_value(result['_value'], nfr['operation'],nfr['threshold']),"value": str(result['_value']),"weight": str(nfr['weight'])})
            for result in comp_result:
                if "weight" in result:
                    if self.is_float(result["weight"]):
                        total_weight+=float(result['weight'])
                    else:
                        result["weight"] = "0"
                        empty_weight_count +=1
            for result in comp_result:
                if "weight" in result:
                    if result["weight"] == "0":
                        if (100-total_weight) > 0:
                            result['weight'] = str((100-total_weight)/empty_weight_count)
            return comp_result
        except Exception:
            pass

    def calculate_apdex(self, test_name, run_id, start = None, end = None):
        comp_result = self.compare_with_nfrs(test_name, run_id, start, end)
        try:
            passed = 0
            failed = 0
            if len(comp_result) > 0:
                for result in comp_result:
                    if result["result"] == "PASSED":
                        passed += float(result["weight"])
                    else:
                        failed += float(result["weight"])
                apdex = passed / (passed + failed) * 100
            else:
                apdex = 0
            return int(apdex)
        except ZeroDivisionError:
            pass