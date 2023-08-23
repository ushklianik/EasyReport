from abc import ABC, abstractmethod
from app import config_path

class integration(ABC):
    def __init__(self, project):
        self.project     = project
        self.config_path = config_path

    @abstractmethod
    def set_config(self):
        pass

    @abstractmethod
    def __str__(self):
        pass
        

    