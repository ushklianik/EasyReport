getTestLog = '''
data = from(bucket: "jmeter")
  |> range(start: 0, stop: now())
  |> filter(fn: (r) => r["_measurement"] == "virtualUsers")
  |> filter(fn: (r) => r["_field"] == "maxActiveThreads")
  |> keep(columns: ["_time", "_value", "runId", "testName"])
  |> group(columns: ["runId", "testName"])
  |> fill(column: "testType", value: "-")

maxThreads = data 
  |> max(column: "_value")
  |> keep(columns: ["_value", "runId", "testName"])
  |> group(columns: ["_value", "runId", "testName"])
  |> rename(columns: {_value: "maxThreads"})

endTime = data 
  |> max(column: "_time")
  |> keep(columns: ["_time", "runId", "testName"])
  |> group(columns: ["_time", "runId", "testName"])
  |> rename(columns: {_time: "endTime"})

startTime = data 
  |> min(column: "_time")
  |> keep(columns: ["_time", "runId", "testName"])
  |> group(columns: ["_time", "runId", "testName"])
  |> rename(columns: {_time: "startTime"})

join1 = join(tables: {d1: maxThreads, d2: startTime}, on: ["runId", "testName"])
  |> keep(columns: ["startTime","runId", "testName",  "maxThreads"])
  |> group(columns: ["runId", "testName"])

join(tables: {d1: join1, d2: endTime}, on: ["runId", "testName"])
  |> map(fn: (r) => ({ r with duration: (int(v: r.endTime) - int(v: r.startTime))}))
  |> keep(columns: ["startTime","endTime", "runId", "testName",  "maxThreads", "duration", "dashboard"])
  |> group(columns: ["1"])
'''

getResTime = '''
from(bucket: "jmeter")
  |> range(start: 2022-11-28T09:44:47.47Z, stop: 2022-11-28T09:48:47.47Z)
  |> filter(fn: (r) => r["_measurement"] == "requestsRaw")
  |> filter(fn: (r) => r["_field"] == "responseTime")
  |> filter(fn: (r) => r["runId"] == "R001")
  |> group(columns: ["_field"])
  |> aggregateWindow(every: 1s, fn: mean, createEmpty: false)
'''