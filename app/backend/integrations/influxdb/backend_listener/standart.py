def get_test_log_query(bucket):
  return '''data = from(bucket: "'''+bucket+'''")
    |> range(start: 0, stop: now())
    |> filter(fn: (r) => r["_measurement"] == "jmeter")
    |> filter(fn: (r) => r["_field"] == "maxAT")
    |> aggregateWindow(every: 1m, fn: last, createEmpty: false)

  maxThreads = data
    |> keep(columns: ["_value", "testTitle", "application"])
    |> max()
    |> group(columns: ["_value", "testTitle", "application"])
    |> rename(columns: {_value: "maxThreads"})

  endTime = data 
    |> max(column: "_time")
    |> keep(columns: ["_time", "testTitle", "application"])
    |> group(columns: ["_time", "testTitle", "application"])
    |> rename(columns: {_time: "endTime"})

  startTime = data 
    |> min(column: "_time")
    |> keep(columns: ["_time", "testTitle", "application"])
    |> group(columns: ["_time", "testTitle", "application"])
    |> rename(columns: {_time: "startTime"})

  join1 = join(tables: {d1: maxThreads, d2: startTime}, on: ["testTitle", "application"])
    |> keep(columns: ["startTime","testTitle", "application",  "maxThreads"])
    |> group(columns: ["testTitle", "application"])

  join(tables: {d1: join1, d2: endTime}, on: ["testTitle", "application"])
    |> map(fn: (r) => ({ r with duration: (int(v: r.endTime)/1000000000 - int(v: r.startTime)/1000000000)}))
    |> keep(columns: ["startTime","endTime","testTitle", "application", "maxThreads", "duration"])
    |> group()
    |> rename(columns: {testTitle: "runId"})
    |> rename(columns: {application: "testName"})'''

def get_start_time(testTitle, bucket):
  return '''from(bucket: "'''+bucket+'''")
  |> range(start: 0, stop: now())
  |> filter(fn: (r) => r["_measurement"] == "jmeter")
  |> filter(fn: (r) => r["_field"] == "maxAT")
  |> filter(fn: (r) => r["testTitle"] == "'''+testTitle+'''")
  |> keep(columns: ["_time"])
  |> min(column: "_time")'''

def get_end_time(testTitle, bucket):
  return '''from(bucket: "'''+bucket+'''")
  |> range(start: 0, stop: now())
  |> filter(fn: (r) => r["_measurement"] == "jmeter")
  |> filter(fn: (r) => r["_field"] == "maxAT")
  |> filter(fn: (r) => r["testTitle"] == "'''+testTitle+'''")
  |> keep(columns: ["_time"])
  |> max(column: "_time")'''

def get_max_active_users_stats(testTitle, start, stop, bucket):
  return '''from(bucket: "'''+bucket+'''")
  |> range(start: '''+str(start)+''', stop: '''+str(stop)+''')
  |> filter(fn: (r) => r["_measurement"] == "jmeter")
  |> filter(fn: (r) => r["_field"] == "maxAT")
  |> filter(fn: (r) => r["testTitle"] == "'''+testTitle+'''")
  |> keep(columns: ["_value"])
  |> max(column: "_value")'''

def get_app_name(testTitle, start, stop, bucket):
  return '''from(bucket: "'''+bucket+'''")
  |> range(start: '''+str(start)+''', stop: '''+str(stop)+''')
  |> filter(fn: (r) => r["_measurement"] == "events")
  |> filter(fn: (r) => r["testTitle"] == "'''+testTitle+'''")
  |> distinct(column: "application")
  |> keep(columns: ["application"])'''

def get_test_duration(testTitle, start, stop, bucket):
  return '''data = from(bucket: "'''+bucket+'''")
  |> range(start: '''+str(start)+''', stop: '''+str(stop)+''')
  |> filter(fn: (r) => r["_measurement"] == "jmeter")
  |> filter(fn: (r) => r["_field"] == "maxAT")
  |> filter(fn: (r) => r["testTitle"] == "'''+testTitle+'''")
  
  endTime = data 
    |> max(column: "_time")
    |> keep(columns: ["_time", "testTitle"])
    |> group(columns: ["_time", "testTitle"])
    |> rename(columns: {_time: "endTime"})

  startTime = data 
    |> min(column: "_time")
    |> keep(columns: ["_time", "testTitle"])
    |> group(columns: ["_time", "testTitle"])
    |> rename(columns: {_time: "startTime"})

  join(tables: {d1: startTime, d2: endTime}, on: ["testTitle"])
    |> map(fn: (r) => ({ r with duration: (int(v: r.endTime)/1000000000 - int(v: r.startTime)/1000000000)}))
    |> keep(columns: ["duration"])
  '''

################################################################# NFR requests
  
def flux_constructor(app_name, testTitle, start, stop, bucket, request_name = ''):
  constr                                  = {}
  constr["source"]                        = 'from(bucket: "'+bucket+'")\n'
  constr["range"]                         = '|> range(start: '+str(start)+', stop: '+str(stop)+')\n'
  constr["_measurement"]                  = '|> filter(fn: (r) => r["_measurement"] == "jmeter")\n'
  constr["metric"]                        = {}
  constr["metric"]["avg"]                 = '|> filter(fn: (r) => r["_field"] == "avg")\n' + \
                                            '|> filter(fn: (r) => r["statut"] == "all")\n'
  constr["metric"]["median"]              = '|> filter(fn: (r) => r["_field"] == "pct50.0")\n' + \
                                            '|> filter(fn: (r) => r["statut"] == "all")\n'
  constr["metric"]["75%-tile"]            = '|> filter(fn: (r) => r["_field"] == "pct75.0")\n' + \
                                            '|> filter(fn: (r) => r["statut"] == "all")\n'
  constr["metric"]["90%-tile"]            = '|> filter(fn: (r) => r["_field"] == "pct90.0")\n' + \
                                            '|> filter(fn: (r) => r["statut"] == "all")\n'
  constr["metric"]["95%-tile"]            = '|> filter(fn: (r) => r["_field"] == "pct95.0")\n' + \
                                            '|> filter(fn: (r) => r["statut"] == "all")\n'
  constr["metric"]["errors"]              = '|> filter(fn: (r) => r["_field"] == "count")\n' + \
                                            '|> filter(fn: (r) => r["statut"] == "ko")\n'
  constr["metric"]["rps"]                 = '|> filter(fn: (r) => r["_field"] == "count")\n' + \
                                            '|> filter(fn: (r) => r["statut"] == "all")\n'
  constr["testTitle"]                     = '|> filter(fn: (r) => r["testTitle"] == "'+testTitle+'")\n'
  constr["scope"]                         = {}
  constr["scope"]['all']                  = '|> filter(fn: (r) => r["transaction"] == "all")\n' + \
                                            '|> group(columns: ["_field"])\n'
  constr["scope"]['each']                 = '|> filter(fn: (r) => r["transaction"] != "all")\n' + \
                                            '|> group(columns: ["transaction"])\n'
  constr["scope"]['request']              = '|> filter(fn: (r) => r["transaction"] == "'+request_name+'")\n' + \
                                            '|> group(columns: ["transaction"])\n'
  constr["aggregation"]                   = {}
  constr["aggregation"]['avg']            = '|> mean()\n'
  constr["aggregation"]['median']         = '|> median()\n'
  constr["aggregation"]["75%-tile"]       = '|> toFloat()\n' + \
                                            '|> quantile(q: 0.75)\n'
  constr["aggregation"]["90%-tile"]       = '|> toFloat()\n' + \
                                            '|> quantile(q: 0.90)\n'
  constr["aggregation"]["95%-tile"]       = '|> toFloat()\n' + \
                                            '|> quantile(q: 0.95)\n'
  constr["aggregation"]['count']          = '|> count()\n'
  constr["aggregation"]['sum']            = '|> sum()\n'
  constr["aggregation"]["rps"]            = '|> aggregateWindow(every: 1s, fn: sum, createEmpty: false)\n'
  return constr


########################## REPORT STATS