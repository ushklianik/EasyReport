from app.backend.integrations.azure.azure import azure
from app.backend.reporting.reporting_base import reporting_base
import re

class azureport(reporting_base):

    def __init__(self, project, template):
        super().__init__(project, template)
        self.output_obj     = azure(project=self.project, name=self.output)
        self.report_body = ""

    def add_text(self, text):
        text = self.replace_variables(text)
        text += '''\n'''
        text += '''\n'''
        return text
    
    def add_graph(self, name, current_run_id, baseline_run_id):
        image = self.grafana_obj.render_image_encoded(name, self.current_start_timestamp, self.current_end_timestamp, self.test_name, current_run_id, baseline_run_id)
        fileName = self.output_obj.put_image_to_azure(image, name)
        graph = '''![image.png](/.attachments/''' + str(fileName) + ''')'''
        graph = graph + '''\n'''
        graph = graph + '''\n'''
        return graph  

    def generate_path(self):
        title = self.output_obj.get_path() + self.replace_variables(self.title)
        return title   
    
    def generate_report(self, tests):
        if len(tests) == 2: 
            self.report_body += self.generate(tests[0], tests[-1])
        else:
            for test in tests:
                self.report_body += self.generate(test)
        path = self.generate_path()
        self.output_obj.create_or_update_page(path, self.report_body)

    def generate(self, current_run_id, baseline_run_id = None):     
        self.collect_data(current_run_id, baseline_run_id)
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

        # screenshots = self.grafana_obj.render_image_encoded(self.graphs, self.current_start_timestamp, self.current_end_timestamp, self.test_name, current_run_id, baseline_run_id)
        # self.status = "Rendered images in Grafana"
        # self.progress = 50

        # for screenshot in screenshots:
        #     fileName = self.output_obj.put_image_to_azure(screenshot["image"], screenshot["name"])
        #     screenshot["filename"] = fileName

        # self.status = "Uploaded images to Azure"
        # self.progress = 75

        # wikiPageName = str(self.parameters["current_vusers"]) + " users | Azure candidate | " + self.parameters["current_startTime"]
        # wikiPagePath = self.output_obj.get_path() + wikiPageName
        
        # variables = re.findall(r"\$\{(.*?)\}", self.header)
        # for var in variables:
        #     self.header = self.header.replace("${"+var+"}", str(self.parameters[var]))
        
        # variables = re.findall(r"\$\{(.*?)\}", self.footer)
        # for var in variables:
        #     self.footer = self.footer.replace("${"+var+"}", str(self.parameters[var]))
     
        # body = self.header

        # for idx in range(len(screenshots)):
        #     for screenshot in screenshots:
        #         if idx == screenshot["position"]:
        #             body = body + '''\n'''
        #             body = body + '''## ''' + str(screenshot["name"])
        #             body = body + '''\n'''
        #             body = body + '''![image.png](/.attachments/''' + str(screenshot["filename"]) + ''')'''
        #             body = body + '''\n'''
        #             body = body + '''\n'''

        # body += self.footer

        # self.output_obj.create_or_update_page(wikiPagePath, body)

        # self.status = "Created Azure page"
        # self.progress = 100