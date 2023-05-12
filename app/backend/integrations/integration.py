from abc import ABC, abstractmethod

class integration(ABC):
    def __init__(self, project):
        self.project     = project
        self.config_path = "./app/projects/" + project + "/config.json"

    @abstractmethod
    def set_config(self):
        pass

    @abstractmethod
    def __str__(self):
        pass
        

    