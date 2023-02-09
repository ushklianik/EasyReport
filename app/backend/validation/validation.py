import json
from os import path
import os
from app.backend.influxdb.influxdb import influxdb
from app.backend.influxdb import custom

class nfr:
    def __init__(self, project):
        self.project = project
        self.pathToNfrs = "./app/projects/" + project + "/nfrs/nfrs.json"
        self.comparison = {}
    
    def saveNFRs(self, nfrs):
        target = []
        skip = True
        # Check if NFR file exists, if not, create a new one
        if path.isfile(self.pathToNfrs) is False or os.path.getsize(self.pathToNfrs) == 0:
            f = open(self.pathToNfrs, "w")
            f.write('[]')
            f.close()
        # Get current NFRs
        with open(self.pathToNfrs, 'r') as fp:
            target = json.load(fp)
        
        # Add name of NFR
        for nfr in nfrs['rows']:
            name = self.generateName(nfr)
            nfr['name'] = name
        
        # Update weight
        for nfr in nfrs['rows']:
            name = self.generateName(nfr)
            nfr['weight'] = 100/len(nfrs['rows'])
        
        # If NFRs already exists, update only edited NFR
        if len(target) != 0:
            for nfrCurrent in target:
                if nfrCurrent['appName'] == nfrs['appName']:
                    nfrCurrent['rows'] = nfrs['rows'] 
                    skip=False
        
        # Add new NFR
        if skip:
            target.append(nfrs)     
        with open(self.pathToNfrs, 'w') as json_file:
            json.dump(target, json_file, indent=4, separators=(',',': '))
    
    # Method returns NFRs for specific application
    def getNFR(self, appName):
        # Check if NFR file exists, if not, return a watning message
        if path.isfile(self.pathToNfrs) is False or os.path.getsize(self.pathToNfrs) == 0:
            f = open(self.pathToNfrs, "w")
            f.write('[]')
            f.close()
            return {"status":"error", "message":"No nfrs"}
        else:  
            # Return NFRs from file for specific application  
            with open(self.pathToNfrs, 'r') as fp:
                nfrs = json.load(fp)
                for nfr in nfrs:
                    if nfr['appName'] == appName:
                        return nfr
            return {"status":"error", "message":"No such app name"}

    # Method reqturns all NFRs for all applications
    def getNFRs(self):
        # Check if NFR file exists, if not, return a watning message
        if path.isfile(self.pathToNfrs) is False or os.path.getsize(self.pathToNfrs) == 0:
            f = open(self.pathToNfrs, "w")
            f.write('[]')
            f.close()
            return {"status":"error", "message":"No nfrs"}
        else:
            # Return NFRs from file    
            with open(self.pathToNfrs, 'r') as fp:
                nfrs = json.load(fp)
                return nfrs

    def deleteNFR(self, appName):
        # Check if NFR file exists, if not, return a watning message
        if path.isfile(self.pathToNfrs) is False or os.path.getsize(self.pathToNfrs) == 0:
            f = open(self.pathToNfrs, "w")
            f.write('[]')
            f.close()
            return {"status":"error", "message":"No nfrs"}
        else:  
            # Return NFRs from file for specific application  
            with open(self.pathToNfrs, 'r') as fl:
                fl = json.load(fl)
                for idx, obj in enumerate(fl):
                    if obj["appName"] == appName:
                        fl.pop(idx)
            with open(self.pathToNfrs, 'w') as json_file:
                json.dump(fl, json_file, indent=4, separators=(',',': '))

    # Method accepts test value, operation and threshold
    # Compares value with treshold using specified operation
    # Returns PASSED or FAILED status
    def compareValue(self, value, operation, threshold):
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
    def generateName(self, nfrRow):
        name = nfrRow['aggregation'].capitalize() + ' ' + nfrRow['metric'] + ' '

        if  nfrRow['scope'] == 'all':
            name += 'for all requests '
        elif nfrRow['scope'] == 'each':
            name += 'for each requests '
        else:
            name += 'for '+nfrRow['scope']+' request '

        if  nfrRow['operation'] == '>':
            name += 'is greater than '
        elif nfrRow['operation'] == '<':
            name += 'is less than '
        elif nfrRow['operation'] == '==':
            name += 'is equal to '
        elif nfrRow['operation'] == '!=':
            name += 'is not equal to '
        elif nfrRow['operation'] == '>=':
            name += '>= than '
        elif nfrRow['operation'] == '<=':
            name += '<= than '

        name += str(nfrRow['threshold'])
        return name     
    
    # Method generates flux query to get test data based on NFR definition
    def generateFluxQuery(self, appName, runId, start, end, nfr):
        # Flux constructor allows to create flux query to get test data based on NFR definition
        constr = custom.fluxConstructor(appName, runId, start, end, requestName=nfr["scope"])
        # Creates query
        query = constr['source'] + \
                constr["range"]  + \
                constr["_measurement"][nfr["metric"]] + \
                constr["metric"][nfr["metric"]] + \
                constr["runId"]
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
    def compareWithNFRs(self, appName, runId, start, end):
        compResult = []
        # Gets NFRs for specific application
        nfrs = self.getNFR(appName)
        # Create INfluxdb connection
        influxdbObj = influxdb(self.project).connectToInfluxDB()
        if "status" in nfrs:
            return nfrs            
        else:
            # Iterates through NFRs
            for nfr in nfrs["rows"]:
                # Generate flux query to get test data based on NFR definition
                query = self.generateFluxQuery(appName, runId, start, end, nfr)
                
                # Get test data to compare with NFR
                results = influxdbObj.sendQuery(query)

                # If influxdb query returns 0 rows
                if len(results) == 0:
                    compResult.append({"name": nfr['name'], "result": "no data"})
                # If influxdb query returns 1 row
                elif len(results) == 1:
                    compResult.append({"name": nfr['name'], "result": self.compareValue(results[0]['_value'], nfr['operation'], nfr['threshold']), "weight": nfr['weight']})
                # If influxdb query returns more than 1 rows
                elif len(results) > 1:
                    status = "PASSED"
                    # If onw request doesn't meet treashold the whole nfr will be failed
                    for result in results:
                        a = self.compareValue(result['_value'], nfr['operation'], nfr['threshold'])
                        if a == "FAILED":
                            status = "FAILED"
                            break
                    compResult.append({"name": nfr['name'], "result": status, "weight": nfr['weight']})
        return compResult

    def calculateApdex(self, compResult):
        passed = 0
        failed = 0
        if "status" not in compResult:
            for result in compResult:
                if result["result"] == "PASSED":
                    passed += float(result["weight"])
                else:
                    failed += float(result["weight"])
            apdex = passed / (passed + failed) * 100
        else:
            apdex = 0
            
        return int(apdex)



            
            
            


    