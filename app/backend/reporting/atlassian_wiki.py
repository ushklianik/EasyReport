from app.backend import pkg
from app.backend.reporting.reporting_base import reporting_base
from app.backend.integrations.atlassian.wiki import wiki
from datetime import datetime
from html import escape
import re

class atlassian_wiki_report(reporting_base):

    def __init__(self, project, template):
        super().__init__(project, template)
        self.output_obj  = wiki(project=self.project, name=self.output)
        self.report_body = ""
        self.page_id     = None

    def add_text(self, text):
        text = self.replace_variables(text)
        text += '''\n'''
        text += '''\n'''
        text = text.replace('\\"', '"')
        text = text.replace('&', '&amp;')
        return text
    
    def add_graph(self, name, current_run_id, baseline_run_id):
        image = self.grafana_obj.render_image(name, self.current_start_timestamp, self.current_end_timestamp, self.test_name, current_run_id, baseline_run_id)
        fileName = self.output_obj.put_image_to_confl(image, name, self.page_id, current_run_id)
        if(fileName):
            graph = '''<ac:image ac:align="center" ac:layout="center" ac:original-height="500" ac:original-width="1000"><ri:attachment ri:filename="''' + str(fileName) + '''" /></ac:image>'''
        else:
            graph = 'Image failed to load, name: '+ name
        graph = graph + '''\n'''
        graph = graph + '''\n'''
        return graph  

    def generate_path(self):
        title = self.replace_variables(self.title)
        return title   

    def create_page_id(self):
        path = self.generate_path()
        response = self.output_obj.put_page(title=path, content="")
        self.page_id=response["id"] 
        self.page_name = path
    
    def generate_report(self, tests):
        if len(tests) == 2: 
            self.report_body += self.generate(current_run_id=tests[0], baseline_run_id=tests[-1])
        elif(len(tests) == 0):
            return "Please provide for which tests you need to make a report"
        else:
            for test in tests:
                self.report_body += self.generate(current_run_id=test)
        print(self.report_body)
        self.output_obj.create_or_update_page(title=self.page_name, content=self.report_body)
        return self.report_body

    def generate(self, current_run_id, baseline_run_id = None):     
        self.collect_data(current_run_id, baseline_run_id)
        if not self.page_id:
           self.create_page_id()
        report_body = ""
        for obj in self.data:
            if obj["type"] == "text":
                report_body += self.add_text(obj["content"])
            elif obj["type"] == "graph":
                report_body += self.add_graph(obj["content"], current_run_id, baseline_run_id)
            elif obj["type"] == "template":
                for sub_obj in self.get_template_data(obj["content"]):
                    if sub_obj["type"] == "text":
                        report_body += self.add_text(sub_obj["content"])
                    elif sub_obj["type"] == "graph":
                        report_body += self.add_graph(sub_obj["content"], current_run_id, baseline_run_id)
        return report_body