import os
import logging

from app.backend                          import pkg
from app.backend.integrations.integration import Integration
from atlassian                            import Confluence
from os                                   import path


class AtlassianWiki(Integration):

    def __init__(self, project, name = None):
        super().__init__(project)
        self.set_config(name)

    def __str__(self):
        return f'Integration name is {self.name}, url is {self.org_url}'
    
    def set_config(self, name):
        if path.isfile(self.config_path) is False or os.path.getsize(self.config_path) == 0:
            return {"status ":"error", "message":"No config.json"}
        else:   
            if name == None:
                name = pkg.get_default_atlassian_wiki(self.project)
            config = pkg.get_atlassian_wiki_config_values(self.project, name)
            if "name" in config:
                if config['name'] == name:
                    self.name                 = config["name"]
                    self.token                = config["token"]
                    self.org_url              = config["org_url"]
                    self.parent_id            = config["parent_id"]
                    self.space_key            = config["space_key"]
                    self.username             = config["username"]
                    self.confl                = Confluence(
                        url=self.org_url,
                        username=self.username,
                        password=self.token
                    )
                else:
                    return {"status":"error", "message":"No such config name"}

    def put_image_to_confl(self, image, name, page_id, test_id):
        name = f'{test_id}_{name}.png'
        name = name.replace(" ", "-")
        for i in range(3):
            try:
                self.confl.attach_content(content=image, page_id=page_id, name=name, content_type="image/png")
                return name
            except Exception as er:
                logging.warning('ERROR: uploading image to confluence failed')
                logging.warning(er)
        
    def put_page(self, title, content):
        try:
            response = self.confl.update_or_create(title=title, body=content, parent_id=self.parent_id, representation='storage')
            return response
        except Exception as er:
            logging.warning(er)
            return {"status":"error", "message":er}

    def update_page(self, page_id, title, content):
        try:
            response = self.confl.update_page(page_id=page_id, title=title, body=content, type='page', representation='storage')
            return response
        except Exception as er:
            logging.warning(er)
            return {"status":"error", "message":er}