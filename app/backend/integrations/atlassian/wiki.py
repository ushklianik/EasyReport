from os import path
from app.backend import pkg
import os
import logging
from atlassian import Confluence
from app.backend.integrations.integration import integration

class confluence(integration):
    def __init__(self, project, name = None):
        super().__init__(project)
        self.setConfig(name)
    
    def setConfig(self, name):
        if path.isfile(self.config_path) is False or os.path.getsize(self.config_path) == 0:
            return {"status ":"error", "message":"No config.json"}
        else:   
            if name == None:
                name = pkg.getDefaultConfl(self.project)
            config = pkg.getConflWikiConfigValues(self.project, name)
            if "name" in config:
                if config['name'] == name:
                    self.name                 = config["name"]
                    self.personalAccessToken  = config["personalAccessToken"]
                    self.wikiOrganizationUrl  = config["wikiOrganizationUrl"]
                    self.wikiParentId         = config["wikiParentId"]
                    self.wikiSpaceKey         = config["wikiSpaceKey"]
                    self.username             = config["username"]
                    self.confl                = Confluence(
                        url=self.wikiOrganizationUrl,
                        username=self.username,
                        password=self.personalAccessToken
                    )
                else:
                    return {"status":"error", "message":"No such config name"}

    def putImageToConfl(self, image, name, pageId):
        name = name.replace(" ", "-") + ".png"
        for i in range(3):
            try:
                # response = self.confl.attach_file(filename=image, page_id=pageId, name=name)
                self.confl.attach_content(content=image, page_id=pageId, name=name, content_type="image/png")
                return name
            except Exception as er:
                print(er)
                logging.warning('ERROR: uploading image to confluence failed')
                logging.warning(er)  


    def putPage(self, title, content):
        try:
            response = self.confl.update_or_create(title=title, body=content, parent_id=self.wikiParentId, representation='storage')
            return response
        except Exception as er:
            logging.warning(er) 
            return {"status":"error", "message":er}

    def createOrUpdatePage(self, title, content):
        response = self.putPage(title, content)
        # print(response)