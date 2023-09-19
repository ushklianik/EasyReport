from app.backend.reporting.reporting_base import reporting_base
from app.backend.integrations.email.mail import mail
import time

class smtp_mail_report(reporting_base):

    def __init__(self, project, template):
        super().__init__(project, template)
        self.output_obj  = mail(project=self.project, name=self.output)
        self.report_body = ""
        self.images = []

    def add_text(self, text):
        text = self.replace_variables(text)
        text = f'<p>{text}</p><br>'
        # text = text.replace('\\"', '"')
        # text = text.replace('&', '&amp;')
        return text
    
    def add_graph(self, name, current_run_id, baseline_run_id):
        image = self.grafana_obj.render_image(name, self.current_start_timestamp, self.current_end_timestamp, self.test_name, current_run_id, baseline_run_id)
        if(image):
            timestamp = str(round(time.time() * 1000))
            content_id = f"{self.test_name}_{name}_{timestamp}"
            file_name = f"{content_id}.png"
            self.images.append({'file_name':file_name, 'data': image, 'content_id': content_id})
            graph = f'<img src="cid:{content_id}"><br>'
        else:
            graph = 'Image failed to load, name: '+ name
        return graph

    def generate_path(self):
        title = self.replace_variables(self.title)
        return title

    def generate_report(self, tests):
        if len(tests) == 2: 
            self.report_body += self.generate(current_run_id=tests[0], baseline_run_id=tests[-1])
        elif(len(tests) == 0):
            return "Please provide for which tests you need to make a report"
        else:
            for test in tests:
                self.report_body += self.generate(current_run_id=test)
        self.output_obj.put_page_to_mail(self.report_body, self.images)
        return self.report_body

    def generate(self, current_run_id, baseline_run_id = None):
        self.collect_data(current_run_id, baseline_run_id)
        report_body = ""
        report_body += f'<h1>{self.generate_path()}</h1><br>'
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