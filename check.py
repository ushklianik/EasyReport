influxdbConfig = "influxdb.yaml"
from werkzeug.datastructures import MultiDict
import yaml

config = {}
with open("./app/integrations/influxdb/"+influxdbConfig, "r") as f:
    config = yaml.safe_load(f)

output = MultiDict()
config = config["influxdb"]
for item in config:
    output.add(item, config[item])
print(output)