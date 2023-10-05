def get_test_log_query(bucket):
  return '''data = from(bucket: "'''+bucket+'''")
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
  |> map(fn: (r) => ({ r with duration: ((int(v: r.endTime)/1000000000 - int(v: r.startTime)/1000000000))}))
  |> keep(columns: ["startTime","endTime", "runId", "testName",  "maxThreads", "duration", "dashboard"])
  |> group(columns: ["1"])
'''


def get_start_time(run_id, bucket):
  return '''from(bucket: "'''+bucket+'''")
  |> range(start: -2y)
  |> filter(fn: (r) => r["_measurement"] == "virtualUsers")
  |> filter(fn: (r) => r["_field"] == "maxActiveThreads")
  |> filter(fn: (r) => r["runId"] == "'''+run_id+'''")
  |> keep(columns: ["_time"])
  |> min(column: "_time")'''

def get_end_time(run_id, bucket):
  return '''from(bucket: "'''+bucket+'''")
  |> range(start: -2y)
  |> filter(fn: (r) => r["_measurement"] == "virtualUsers")
  |> filter(fn: (r) => r["_field"] == "maxActiveThreads")
  |> filter(fn: (r) => r["runId"] == "'''+run_id+'''")
  |> keep(columns: ["_time"])
  |> max(column: "_time")'''

def get_max_active_users_stats(run_id, start, stop, bucket):
  return '''from(bucket: "'''+bucket+'''")
  |> range(start: '''+str(start)+''', stop: '''+str(stop)+''')
  |> filter(fn: (r) => r["_measurement"] == "virtualUsers")
  |> filter(fn: (r) => r["_field"] == "maxActiveThreads")
  |> filter(fn: (r) => r["runId"] == "'''+run_id+'''")
  |> keep(columns: ["_value"])
  |> max(column: "_value")'''

def get_average_rps_stats(run_id, start, stop, bucket):
  return '''from(bucket: "'''+bucket+'''")
  |> range(start: '''+str(start)+''', stop: '''+str(stop)+''')
  |> filter(fn: (r) => r["_measurement"] == "requestsRaw")
  |> filter(fn: (r) => r["_field"] == "responseTime")
  |> filter(fn: (r) => r["runId"] == "'''+run_id+'''")
  |> group(columns: ["_field"])
  |> aggregateWindow(every: 1s, fn: count, createEmpty: false)   
  |> mean()'''


def get_errors_perc_stats(run_id, start, stop, bucket):
  return '''countResponseTime=from(bucket: "'''+bucket+'''")
  |> range(start: '''+str(start)+''', stop: '''+str(stop)+''')
  |> filter(fn: (r) => r["_measurement"] == "requestsRaw")
  |> filter(fn: (r) => r["_field"] == "responseTime")
  |> filter(fn: (r) => r["runId"] == "'''+run_id+'''")
  |> group()
  |> count()
  |> toFloat()
  |> set(key: "key", value: "value")

sumerrorCount=from(bucket: "'''+bucket+'''")
  |> range(start: '''+str(start)+''', stop: '''+str(stop)+''')
  |> filter(fn: (r) => r["_measurement"] == "requestsRaw")
  |> filter(fn: (r) => r["_field"] == "errorCount")
  |> filter(fn: (r) => r["runId"] == "'''+run_id+'''")
  |> group()
  |> sum()
  |> toFloat()
  |> set(key: "key", value: "value")

join(
      tables:{countResponseTime:countResponseTime, sumerrorCount:sumerrorCount},
      on:["key"]
    )    
    |> map(fn:(r) => ({
             key: r.key,
             _value: r._value_sumerrorCount / r._value_countResponseTime * 100.0        
    }))  '''

def get_avg_response_time_stats(run_id, start, stop, bucket):
  return '''from(bucket: "'''+bucket+'''")
  |> range(start: '''+str(start)+''', stop: '''+str(stop)+''')
  |> filter(fn: (r) => r["_measurement"] == "requestsRaw")
  |> filter(fn: (r) => r["_field"] == "responseTime")
  |> filter(fn: (r) => r["runId"] == "'''+run_id+'''")
  |> group(columns: ["_field"]) 
  |> mean()'''

def get_90_response_time_stats(run_id, start, stop, bucket):
  return '''from(bucket: "'''+bucket+'''")
  |> range(start: '''+str(start)+''', stop: '''+str(stop)+''')
  |> filter(fn: (r) => r["_measurement"] == "requestsRaw")
  |> filter(fn: (r) => r["_field"] == "responseTime")
  |> filter(fn: (r) => r["runId"] == "'''+run_id+'''")
  |> group(columns: ["_field"]) 
  |> toFloat() 
  |> quantile(q: 0.90)'''

def get_median_response_time_stats(run_id, start, stop, bucket):
  return '''from(bucket: "'''+bucket+'''")
  |> range(start: '''+str(start)+''', stop: '''+str(stop)+''')
  |> filter(fn: (r) => r["_measurement"] == "requestsRaw")
  |> filter(fn: (r) => r["_field"] == "responseTime")
  |> filter(fn: (r) => r["runId"] == "'''+run_id+'''")
  |> group(columns: ["_field"]) 
  |> toFloat() 
  |> median()'''

def get_avg_bandwidth_stats(run_id, start, stop, bucket):
  return '''sentBytes = from(bucket: "'''+bucket+'''")
  |> range(start: '''+str(start)+''', stop: '''+str(stop)+''')
  |> filter(fn: (r) => r["_measurement"] == "requestsRaw")
  |> filter(fn: (r) => r["_field"] == "sentBytes")
  |> filter(fn: (r) => r["runId"] == "'''+run_id+'''")
  |> keep(columns: ["_time", "_value", "_field"])
  |> group(columns: ["_field"])
  |> aggregateWindow(every: 1s, fn: mean, createEmpty: false)
  |> mean()
  |> set(key: "key", value: "value")
receivedBytes = from(bucket: "'''+bucket+'''")
  |> range(start: '''+str(start)+''', stop: '''+str(stop)+''')
  |> filter(fn: (r) => r["_measurement"] == "requestsRaw")
  |> filter(fn: (r) => r["_field"] == "receivedBytes")
  |> filter(fn: (r) => r["runId"] == "'''+run_id+'''")
  |> keep(columns: ["_time", "_value", "_field"])
  |> group(columns: ["_field"])
  |> aggregateWindow(every: 1s, fn: mean, createEmpty: false)
  |> mean()
  |> set(key: "key", value: "value")
join(
      tables:{sentBytes:sentBytes, receivedBytes:receivedBytes},
      on:["key"]
    )    
    |> map(fn:(r) => ({
             key: r.key,
             _value: r._value_sentBytes + r._value_receivedBytes     
    }))'''

def get_avg_response_time_graph(run_id, start, stop, bucket):
  return '''from(bucket: "'''+bucket+'''")
  |> range(start: '''+str(start)+''', stop: '''+str(stop)+''')
  |> filter(fn: (r) => r["_measurement"] == "requestsRaw")
  |> filter(fn: (r) => r["_field"] == "responseTime")
  |> filter(fn: (r) => r["runId"] == "'''+run_id+'''")
  |> group(columns: ["_field"])
  |> aggregateWindow(every: 1s, fn: mean, createEmpty: false)
  '''

def get_rps_graph(run_id, start, stop, bucket):
  return '''from(bucket: "'''+bucket+'''")
  |> range(start: '''+str(start)+''', stop: '''+str(stop)+''')
  |> filter(fn: (r) => r["_measurement"] == "requestsRaw")
  |> filter(fn: (r) => r["_field"] == "responseTime")
  |> filter(fn: (r) => r["runId"] == "'''+run_id+'''")
  |> group(columns: ["_field"])
  |> aggregateWindow(every: 1s, fn: count, createEmpty: false)
  '''

################################################################# NFR requests

def get_app_name(run_id, start, stop, bucket):
  return '''from(bucket: "'''+bucket+'''")
  |> range(start: '''+str(start)+''', stop: '''+str(stop)+''')
  |> filter(fn: (r) => r["_measurement"] == "requestsRaw")
  |> filter(fn: (r) => r["runId"] == "'''+run_id+'''")
  |> filter(fn: (r) => r["_field"] == "responseTime")
  |> group(columns: ["testName"])
  |> max()
  |> keep(columns: ["testName"])'''
  
def flux_constructor(app_name, run_id, start, stop, bucket, request_name = ''):
  constr                                  = {}
  constr["source"]                        = 'from(bucket: "'+bucket+'")\n'
  constr["range"]                         = '|> range(start: '+str(start)+', stop: '+str(stop)+')\n'
  constr["_measurement"]                  = {}
  constr["_measurement"]["response-time"] = '|> filter(fn: (r) => r["_measurement"] == "requestsRaw")\n'
  constr["_measurement"]["rps"]           = '|> filter(fn: (r) => r["_measurement"] == "requestsRaw")\n'
  constr["_measurement"]["errors"]        = '|> filter(fn: (r) => r["_measurement"] == "requestsRaw")\n'
  constr["metric"]                        = {}
  constr["metric"]["response-time"]       = '|> filter(fn: (r) => r["_field"] == "responseTime")\n'
  constr["metric"]["rps"]                 = '|> filter(fn: (r) => r["_field"] == "responseTime")\n' 
  constr["metric"]["errors"]              = '|> filter(fn: (r) => r["_field"] == "errorCount")\n'
  constr["runId"]                         = '|> filter(fn: (r) => r["runId"] == "'+run_id+'")\n'
  constr["scope"]                         = {}
  constr["scope"]['all']                  = '|> group(columns: ["_field"])\n'
  constr["scope"]['each']                 = '|> group(columns: ["requestName"])\n'
  constr["scope"]['request']              = '|> filter(fn: (r) => r["requestName"] == "'+request_name+'")\n' + \
                                            '|> group(columns: ["requestName"])\n'
  constr["aggregation"]                   = {}
  constr["aggregation"]['avg']            = '|> mean()\n'
  constr["aggregation"]['median']         = '|> median()\n'
  constr["aggregation"]['75%-tile']       = '|> toFloat()\n' + \
                                            '|> quantile(q: 0.75)\n'
  constr["aggregation"]['90%-tile']       = '|> toFloat()\n' + \
                                            '|> quantile(q: 0.90)\n'
  constr["aggregation"]['95%-tile']       = '|> toFloat()\n' + \
                                            '|> quantile(q: 0.95)\n'
  constr["aggregation"]['count']          = '|> count()\n'
  constr["aggregation"]['sum']            = '|> sum()\n'
  constr["aggregation"]["rps"]            = '|> aggregateWindow(every: 1s, fn: count, createEmpty: false)\n' 
  return constr

def get_test_names(run_id, bucket):
  return '''from(bucket: "'''+bucket+'''")
  |> range(start: -1y)
  |> filter(fn: (r) => r["_measurement"] == "tests")
  |> filter(fn: (r) => r["runId"] == "'''+run_id+'''")
  |> group(columns: ["runId"])
  |> count()
  |> keep(columns: ["runId"])'''