from os import path
import os
import json

class grfana:

    def __init__(self, project):
        self.project    = project
        self.path       = "./app/projects/" + project + "/config.json"
    
    def getGrafanaConfigs(self):
        if path.isfile(self.path) is False or os.path.getsize(self.path) == 0:
            return {"status":"error", "message":"No config.json"}
        else:   
            with open(self.path, 'r') as fp:
                nfrs = json.load(fp)
                for nfr in nfrs:
                    if nfr['appName'] == appName:
                        return nfr
            return {"status":"error", "message":"No such app name"}