from app.backend import pkg

class report:

    def __init__(self, project, reportName):
        self.project    = project
        self.reportName = reportName

    def readGrafanaConfig(self):
        config = pkg.getReportConfigValues(self.project, self.reportName)
        grafanaConfig = pkg.getReportConfigValues(self.project, self.reportName)["grafanaName"]

        return config

