import json
from os import path
import os
from app.backend.integrations.influxdb.influxdb import influxdb
from app.backend.integrations.influxdb.backend_listener import custom

class nfr:
    def __init__(self, project):
        self.project = project
        self.path_to_nfrs = "./app/projects/" + project + "/nfrs/nfrs.json"
        self.comparison = {}

    def save_nfrs(self, nfrs):
        target = []
        skip = True
        # Check if NFR file exists, if not, create a new one
        if path.isfile(self.path_to_nfrs) is False or os.path.getsize(self.path_to_nfrs) == 0:
            f = open(self.path_to_nfrs, "w")
            f.write('[]')
            f.close()
        # Get current NFRs
        with open(self.path_to_nfrs, 'r') as fp:
            target = json.load(fp)
        
        # Add name of NFR
        for nfr in nfrs['rows']:
            name = self.generate_name(nfr)
            nfr['name'] = name
        
        # Update weight
        for nfr in nfrs['rows']:
            name = self.generate_name(nfr)
            nfr['weight'] = 100/len(nfrs['rows'])
        
        # If NFRs already exists, update only edited NFR
        if len(target) != 0:
            for nfr_current in target:
                if nfr_current['app_name'] == nfrs['app_name']:
                    nfr_current['rows'] = nfrs['rows'] 
                    skip=False
        
        # Add new NFR
        if skip:
            target.append(nfrs)     
        with open(self.path_to_nfrs, 'w') as json_file:
            json.dump(target, json_file, indent=4, separators=(',',': '))
    
    # Method returns NFRs for specific application
    def get_nfr(self, app_name):
        # Check if NFR file exists, if not, return a watning message
        if path.isfile(self.path_to_nfrs) is False or os.path.getsize(self.path_to_nfrs) == 0:
            f = open(self.path_to_nfrs, "w")
            f.write('[]')
            f.close()
            return {"status":"error", "message":"No nfrs"}
        else:  
            # Return NFRs from file for specific application  
            with open(self.path_to_nfrs, 'r') as fp:
                nfrs = json.load(fp)
                for nfr in nfrs:
                    if nfr['app_name'] == app_name:
                        return nfr
            return {"status":"error", "message":"No such app name"}

    # Method reqturns all NFRs for all applications
    def get_nfrs(self):
        # Check if NFR file exists, if not, return a watning message
        if path.isfile(self.path_to_nfrs) is False or os.path.getsize(self.path_to_nfrs) == 0:
            f = open(self.path_to_nfrs, "w")
            f.write('[]')
            f.close()
            return {"status":"error", "message":"No nfrs"}
        else:
            # Return NFRs from file    
            with open(self.path_to_nfrs, 'r') as fp:
                nfrs = json.load(fp)
                return nfrs


    # Method accepts test value, operation and threshold
    # Compares value with treshold using specified operation
    # Returns PASSED or FAILED status
    def compare_value(self, value, operation, threshold):
        if type(value) == int or type(value) == float:
            if type(threshold) == int or type(threshold) == float:
                if  operation == '>':
                    if value > threshold:
                        return "PASSED"
                    else: 
                        return "FAILED"
                elif operation == '<':
                    if value < threshold:
                        return "PASSED"
                    else: 
                        return "FAILED"
                elif operation == '==':
                    if value == threshold:
                        return "PASSED"
                    else: 
                        return "FAILED"
                elif operation == '!=':
                    if value != threshold:
                        return "PASSED"
                    else: 
                        return "FAILED"
                elif operation == '>=':
                    if value >= threshold:
                        return "PASSED"
                    else: 
                        return "FAILED"
                elif operation == '<=':
                    if value >= threshold:
                        return "PASSED"
                    else: 
                        return "FAILED"
            else: return "threshold is not number"
        else: return "value is not number"
    
    # Method generates name based on NFR definition, for example:
    # NFR: {"scope": "all","metric": "response-time","aggregation": "95%-tile","operation": ">","threshold": 4000}
    # Name: 95%-tile response-time for all requests is greater than 4000
    def generate_name(self, nfr_row):
        name = nfr_row['aggregation'].capitalize() + ' ' + nfr_row['metric'] + ' '

        if  nfr_row['scope'] == 'all':
            name += 'for all requests '
        elif nfr_row['scope'] == 'each':
            name += 'for each requests '
        else:
            name += 'for '+nfr_row['scope']+' request '

        if  nfr_row['operation'] == '>':
            name += 'is greater than '
        elif nfr_row['operation'] == '<':
            name += 'is less than '
        elif nfr_row['operation'] == '==':
            name += 'is equal to '
        elif nfr_row['operation'] == '!=':
            name += 'is not equal to '
        elif nfr_row['operation'] == '>=':
            name += '>= than '
        elif nfr_row['operation'] == '<=':
            name += '<= than '

        name += str(nfr_row['threshold'])
        return name     
    
    # Method generates flux query to get test data based on NFR definition
    def generate_flux_query(self, app_name, run_id, start, end, bucket, nfr):
        # Flux constructor allows to create flux query to get test data based on NFR definition
        constr = custom.flux_constructor(app_name, run_id, start, end, bucket, request_name=nfr["scope"])
        # Creates query
        query = constr['source'] + \
                constr["range"]  + \
                constr["_measurement"][nfr["metric"]] + \
                constr["metric"][nfr["metric"]] + \
                constr["run_id"]
        # If scope is specific request name, use key "request"
        if nfr['scope'] not in ['all', 'each']:
            query += constr["scope"]['request']
        else: 
            query += constr["scope"][nfr['scope']]
        
        # If metric is rps, then add aggregation window
        if nfr['metric'] == 'rps':
            query += constr["aggregation"][nfr['metric']]
        query += constr["aggregation"][nfr['aggregation']]
        return query        
    
    # Method takes a list of NFRs 
    # Constructs a flux request to the InfluxDB based on the NFRs
    # Takes test data and compares it with the NFRs
    def compare_with_nfrs(self, app_name, run_id, start, end):
        comp_result = []
        # Gets NFRs for specific application
        nfrs = self.get_nfr(app_name)
        # Create INfluxdb connection
        influxdb_obj = influxdb(self.project).connect_to_influxdb()
        if "status" in nfrs:
            return nfrs            
        else:
            # Iterates through NFRs
            for nfr in nfrs["rows"]:
                # Generate flux query to get test data based on NFR definition
                query = self.generate_flux_query(app_name, run_id, start, end, influxdb_obj.bucket, nfr)
                
                # Get test data to compare with NFR
                results = influxdb_obj.send_query(query)

                # If influxdb query returns 0 rows
                if len(results) == 0:
                    comp_result.append({"name": nfr['name'], "result": "no data"})
                # If influxdb query returns 1 row
                elif len(results) == 1:
                    comp_result.append({"name": nfr['name'], "result": self.compare_value(results[0]['_value'], nfr['operation'], nfr['threshold']), "weight": nfr['weight']})
                # If influxdb query returns more than 1 rows
                elif len(results) > 1:
                    status = "PASSED"
                    # If onw request doesn't meet treashold the whole nfr will be failed
                    for result in results:
                        a = self.compare_value(result['_value'], nfr['operation'], nfr['threshold'])
                        if a == "FAILED":
                            status = "FAILED"
                            break
                    comp_result.append({"name": nfr['name'], "result": status, "weight": nfr['weight']})
        return comp_result

    def calculate_apdex(self, comp_result):
        passed = 0
        failed = 0
        if "status" not in comp_result:
            for result in comp_result:
                if result["result"] == "PASSED":
                    passed += float(result["weight"])
                else:
                    failed += float(result["weight"])
            apdex = passed / (passed + failed) * 100
        else:
            apdex = 0
        return int(apdex)



            
            
            


    