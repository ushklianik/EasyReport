import json
from os import path
import os

class nfr:
    def __init__(self, project):
        self.project = project
        self.pathToNfrs = "./app/projects/" + project + "/nfrs/nfrs.json"
    
    def saveNFRs(self, nfrs):
        target = []
        skip = True
        if path.isfile(self.pathToNfrs) is False or os.path.getsize(self.pathToNfrs) == 0:
            f = open(self.pathToNfrs, "w")
            f.write('[]')
            f.close()

        with open(self.pathToNfrs, 'r') as fp:
            target = json.load(fp)

        if len(target) != 0:
            for nfrCurrent in target:
                if nfrCurrent['appName'] == nfrs['appName']:
                    nfrCurrent['rows'] = nfrs['rows'] 
                    skip=False
        if skip:
            target.append(nfrs)     
        with open(self.pathToNfrs, 'w') as json_file:
            json.dump(target, json_file, indent=4, separators=(',',': '))
    
    def getNFR(self, appName):
        if path.isfile(self.pathToNfrs) is False or os.path.getsize(self.pathToNfrs) == 0:
            f = open(self.pathToNfrs, "w")
            f.write('[]')
            f.close()
            return {"status":"error", "message":"No nfrs"}
        else:    
            with open(self.pathToNfrs, 'r') as fp:
                nfrs = json.load(fp)
                for nfr in nfrs:
                    if nfr['appName'] == appName:
                        return nfr
            return {"status":"error", "message":"No such app name"}

            
    def getNFRs(self):
        if path.isfile(self.pathToNfrs) is False or os.path.getsize(self.pathToNfrs) == 0:
            f = open(self.pathToNfrs, "w")
            f.write('[]')
            f.close()
            return {"status":"error", "message":"No nfrs"}
        else:    
            with open(self.pathToNfrs, 'r') as fp:
                nfrs = json.load(fp)
                return nfrs

    def compareWithNFRs(self, appName):
        nfrs = self.getNFR(appName)
        for nfr in nfrs["rows"]:
            print(nfr)
            


    