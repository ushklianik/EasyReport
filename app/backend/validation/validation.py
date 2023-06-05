import json
from os.path import isfile, getsize
from app.backend.integrations.influxdb.influxdb import influxdb
from app.backend.integrations.influxdb.backend_listener import custom

class NFR:
    def __init__(self, project):
        self.project = project
        self.path_to_nfrs = f"./app/projects/{project}/nfrs/nfrs.json"
        self.comparison = {}

    def save_nfrs(self, nfrs):
        target = []

        # Check if NFR file exists, if not, create a new one
        if not isfile(self.path_to_nfrs) or getsize(self.path_to_nfrs) == 0:
            with open(self.path_to_nfrs, "w") as f:
                f.write('[]')

        # Get current NFRs
        with open(self.path_to_nfrs, 'r') as fp:
            target = json.load(fp)

        # Add name of NFR
        for nfr in nfrs['rows']:
            print("row" + str(nfr))
            name = self.generate_name(nfr)
            nfr['name'] = name

        # If NFRs already exist, update only the edited NFR
        if len(target) != 0:
            for nfr_current in target:
                if nfr_current['test_name'] == nfrs['test_name']:
                    nfr_current['rows'] = nfrs['rows']
                    break
        else:
            # Add new NFR
            target.append(nfrs)

        with open(self.path_to_nfrs, 'w') as json_file:
            json.dump(target, json_file, indent=4, separators=(',', ': '))

    def delete_nfrs(self, test_name):
        target = []

        # Check if NFR file exists, if not, create a new one
        if not isfile(self.path_to_nfrs) or getsize(self.path_to_nfrs) == 0:
            with open(self.path_to_nfrs, "w") as f:
                f.write('[]')

        # Get current NFRs
        with open(self.path_to_nfrs, 'r') as fp:
            target = json.load(fp)

        # Filter out records with the specified test_name
        new_json = [record for record in target if record['test_name'] != test_name]
        
        with open(self.path_to_nfrs, 'w') as json_file:
            json.dump(new_json, json_file, indent=4, separators=(',', ': '))
        

    # Method returns NFRs for specific application
    def get_nfr(self, test_name):
        # Check if NFR file exists, if not, return a warning message
        if not isfile(self.path_to_nfrs) or getsize(self.path_to_nfrs) == 0:
            with open(self.path_to_nfrs, "w") as f:
                f.write('[]')
            return {"status": "error", "message": "No nfrs"}
        else:
            # Return NFRs from file for the specific application
            with open(self.path_to_nfrs, 'r') as fp:
                nfrs = json.load(fp)
                for nfr in nfrs:
                    if nfr['test_name'] == test_name:
                        return nfr
                return {"status": "error", "message": "No such app name"}

    # Method reqturns all NFRs for all applications
    def get_nfrs(self):
        if not isfile(self.path_to_nfrs) or getsize(self.path_to_nfrs) == 0:
            with open(self.path_to_nfrs, "w") as f:
                f.write('[]')
            return {"status": "error", "message": "No nfrs"}
        else:
            # Return NFRs from file
            with open(self.path_to_nfrs, 'r') as fp:
                nfrs = json.load(fp)
                return nfrs


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
    
    # Method generates flux query to get test data based on NFR definition
    def generate_flux_query(self, test_name, run_id, start, end, bucket, nfr):
        try:
            # Flux constructor allows creating a flux query to get test data based on NFR definition
            constr = custom.flux_constructor(test_name, run_id, start, end, bucket, request_name=nfr["scope"])
            # Create query
            query = (
                constr['source']
                + constr["range"]
                + constr["_measurement"][nfr["metric"]]
                + constr["metric"][nfr["metric"]]
                + constr["run_id"]
            )
            # If scope is a specific request name, use the key "request"
            if nfr['scope'] not in ['all', 'each']:
                query += constr["scope"]['request']
            else:
                query += constr["scope"][nfr['scope']]

            # If the metric is rps, then add the aggregation window
            if nfr['metric'] == 'rps':
                query += constr["aggregation"][nfr['metric']]
            query += constr["aggregation"][nfr['aggregation']]
            return query

        except KeyError:
            # Handle missing keys in the flux_constructor dictionary
            pass 
    
    # Method takes a list of NFRs 
    # Constructs a flux request to the InfluxDB based on the NFRs
    # Takes test data and compares it with the NFRs
    def compare_with_nfrs(self, test_name, run_id, start, end):
        comp_result = []
        try:
            # Get NFRs for the specific application
            nfrs = self.get_nfr(test_name)
            # Create InfluxDB connection
            influxdb_obj = influxdb(self.project).connect_to_influxdb()
            if "status" in nfrs:
                return nfrs
            else:
                # Iterate through NFRs
                for nfr in nfrs["rows"]:
                    # Generate flux query to get test data based on NFR definition
                    query = self.generate_flux_query(test_name, run_id, start, end, influxdb_obj.bucket, nfr)

                    # Get test data to compare with NFR
                    results = influxdb_obj.send_query(query)

                    # If InfluxDB query returns 0 rows
                    if len(results) == 0:
                        comp_result.append({"name": nfr['name'], "result": "no data"})
                    # If InfluxDB query returns 1 row
                    elif len(results) == 1:
                        comp_result.append(
                            {"name": nfr['name'], "result": self.compare_value(results[0]['_value'], nfr['operation'],
                                                                                 nfr['threshold']),
                             "weight": nfr['weight']})
                    # If InfluxDB query returns more than 1 row
                    elif len(results) > 1:
                        status = "PASSED"
                        # If one request doesn't meet the threshold, the whole NFR will be failed
                        for result in results:
                            if self.compare_value(result['_value'], nfr['operation'], nfr['threshold']) == "FAILED":
                                status = "FAILED"
                                break
                        comp_result.append({"name": nfr['name'], "result": status, "weight": nfr['weight']})
            return comp_result

        except Exception:
            # Handle exceptions here
            pass

    def calculate_apdex(comp_result):
        try:
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

        except ZeroDivisionError:
            # Handle division by zero error
            pass



            
            
            


    