from app.backend.reporting.reporting_base import reporting_base

obj = reporting_base("default", "temp1")
print(obj.title)
print(obj.influxdb)
print(obj.data)
