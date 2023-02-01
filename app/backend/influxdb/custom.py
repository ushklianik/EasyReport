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
  |> map(fn: (r) => ({ r with duration: ((int(v: r.endTime) - int(v: r.startTime))/1000000000)}))
  |> keep(columns: ["startTime","endTime", "runId", "testName",  "maxThreads", "duration", "dashboard"])
  |> group(columns: ["1"])
'''

def getResponseTime(runId):
  return '''from(bucket: "jmeter")
  |> range(start: 2022-11-28T09:44:47.47Z, stop: 2022-11-28T09:48:47.47Z)
  |> filter(fn: (r) => r["_measurement"] == "requestsRaw")
  |> filter(fn: (r) => r["_field"] == "responseTime")
  |> filter(fn: (r) => r["runId"] == "R001")
  |> group(columns: ["_field"])
  |> aggregateWindow(every: 1s, fn: mean, createEmpty: false)
  '''

def getStartTime(runId):
  return '''from(bucket: "jmeter")
  |> range(start: -2y)
  |> filter(fn: (r) => r["_measurement"] == "virtualUsers")
  |> filter(fn: (r) => r["_field"] == "maxActiveThreads")
  |> filter(fn: (r) => r["runId"] == "'''+runId+'''")
  |> keep(columns: ["_time"])
  |> min(column: "_time")'''

def getEndTime(runId):
  return '''from(bucket: "jmeter")
  |> range(start: -2y)
  |> filter(fn: (r) => r["_measurement"] == "virtualUsers")
  |> filter(fn: (r) => r["_field"] == "maxActiveThreads")
  |> filter(fn: (r) => r["runId"] == "'''+runId+'''")
  |> keep(columns: ["_time"])
  |> max(column: "_time")'''

def getMaxActiveUsers_stats(runId, start, stop):
  return '''from(bucket: "jmeter")
  |> range(start: '''+str(start)+''', stop: '''+str(stop)+''')
  |> filter(fn: (r) => r["_measurement"] == "virtualUsers")
  |> filter(fn: (r) => r["_field"] == "maxActiveThreads")
  |> filter(fn: (r) => r["runId"] == "'''+runId+'''")
  |> keep(columns: ["_value"])
  |> max(column: "_value")'''

def getAverageRPS_stats(runId, start, stop):
  return '''from(bucket: "jmeter")
  |> range(start: '''+str(start)+''', stop: '''+str(stop)+''')
  |> filter(fn: (r) => r["_measurement"] == "requestsRaw")
  |> filter(fn: (r) => r["_field"] == "responseTime")
  |> filter(fn: (r) => r["runId"] == "'''+runId+'''")
  |> group(columns: ["_field"])
  |> aggregateWindow(every: 1s, fn: count, createEmpty: false)   
  |> mean()'''


def getErrorsPerc_stats(runId, start, stop):
  return '''countResponseTime=from(bucket: "jmeter")
  |> range(start: '''+str(start)+''', stop: '''+str(stop)+''')
  |> filter(fn: (r) => r["_measurement"] == "requestsRaw")
  |> filter(fn: (r) => r["_field"] == "responseTime")
  |> filter(fn: (r) => r["runId"] == "'''+runId+'''")
  |> group()
  |> count()
  |> toFloat()
  |> set(key: "key", value: "value")

sumerrorCount=from(bucket: "jmeter")
  |> range(start: '''+str(start)+''', stop: '''+str(stop)+''')
  |> filter(fn: (r) => r["_measurement"] == "requestsRaw")
  |> filter(fn: (r) => r["_field"] == "errorCount")
  |> filter(fn: (r) => r["runId"] == "'''+runId+'''")
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

def getAvgResponseTime_stats(runId, start, stop):
  return '''from(bucket: "jmeter")
  |> range(start: '''+str(start)+''', stop: '''+str(stop)+''')
  |> filter(fn: (r) => r["_measurement"] == "requestsRaw")
  |> filter(fn: (r) => r["_field"] == "responseTime")
  |> filter(fn: (r) => r["runId"] == "'''+runId+'''")
  |> group(columns: ["_field"]) 
  |> mean()'''

def get90ResponseTime_stats(runId, start, stop):
  return '''from(bucket: "jmeter")
  |> range(start: '''+str(start)+''', stop: '''+str(stop)+''')
  |> filter(fn: (r) => r["_measurement"] == "requestsRaw")
  |> filter(fn: (r) => r["_field"] == "responseTime")
  |> filter(fn: (r) => r["runId"] == "'''+runId+'''")
  |> group(columns: ["_field"]) 
  |> toFloat() 
  |> quantile(q: 0.90)'''

def getAvgBandwidth_stats(runId, start, stop):
  return '''sentBytes = from(bucket: "jmeter")
  |> range(start: '''+str(start)+''', stop: '''+str(stop)+''')
  |> filter(fn: (r) => r["_measurement"] == "requestsRaw")
  |> filter(fn: (r) => r["_field"] == "sentBytes")
  |> filter(fn: (r) => r["runId"] == "'''+runId+'''")
  |> keep(columns: ["_time", "_value", "_field"])
  |> group(columns: ["_field"])
  |> aggregateWindow(every: 1s, fn: mean, createEmpty: false)
  |> mean()
  |> set(key: "key", value: "value")

receivedBytes = from(bucket: "jmeter")
  |> range(start: '''+str(start)+''', stop: '''+str(stop)+''')
  |> filter(fn: (r) => r["_measurement"] == "requestsRaw")
  |> filter(fn: (r) => r["_field"] == "receivedBytes")
  |> filter(fn: (r) => r["runId"] == "'''+runId+'''")
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

def getAvgResponseTime_graph(runId, start, stop):
  return '''from(bucket: "jmeter")
  |> range(start: '''+str(start)+''', stop: '''+str(stop)+''')
  |> filter(fn: (r) => r["_measurement"] == "requestsRaw")
  |> filter(fn: (r) => r["_field"] == "responseTime")
  |> filter(fn: (r) => r["runId"] == "'''+runId+'''")
  |> group(columns: ["_field"])
  |> aggregateWindow(every: 1s, fn: mean, createEmpty: false)
  '''

def getRPS_graph(runId, start, stop):
  return '''from(bucket: "jmeter")
  |> range(start: '''+str(start)+''', stop: '''+str(stop)+''')
  |> filter(fn: (r) => r["_measurement"] == "requestsRaw")
  |> filter(fn: (r) => r["_field"] == "responseTime")
  |> filter(fn: (r) => r["runId"] == "'''+runId+'''")
  |> group(columns: ["_field"])
  |> aggregateWindow(every: 1s, fn: count, createEmpty: false)
  '''

################################################################# NFR requests
def getAvgAllRT(runId, start, stop):
  return '''from(bucket: "jmeter")
  |> range(start: '''+str(start)+''', stop: '''+str(stop)+''')
  |> filter(fn: (r) => r["_measurement"] == "requestsRaw")
  |> filter(fn: (r) => r["_field"] == "responseTime")
  |> filter(fn: (r) => r["runId"] == "'''+runId+'''")
  |> group(columns: ["_field"])
  |> mean()
  '''

def getAvgEachRT(runId, start, stop):
  return '''from(bucket: "jmeter")
  |> range(start: '''+str(start)+''', stop: '''+str(stop)+''')
  |> filter(fn: (r) => r["_measurement"] == "requestsRaw")
  |> filter(fn: (r) => r["_field"] == "responseTime")
  |> filter(fn: (r) => r["runId"] == "'''+runId+'''")
  |> group(columns: ["requestName"])
  |> mean()
  |> group()
  '''

def getAvgRequestRT(runId, start, stop, requestName):
  return '''from(bucket: "jmeter")
  |> range(start: '''+str(start)+''', stop: '''+str(stop)+''')
  |> filter(fn: (r) => r["_measurement"] == "requestsRaw")
  |> filter(fn: (r) => r["_field"] == "responseTime")
  |> filter(fn: (r) => r["runId"] == "'''+runId+'''")
  |> filter(fn: (r) => r["requestName"] == "'''+requestName+'''")
  |> group(columns: ["requestName"])
  |> mean()
  '''

def getAppName(runId, start, stop):
  return '''from(bucket: "jmeter")
  |> range(start: '''+str(start)+''', stop: '''+str(stop)+''')
  |> filter(fn: (r) => r["_measurement"] == "requestsRaw")
  |> filter(fn: (r) => r["runId"] == "'''+runId+'''")
  |> filter(fn: (r) => r["_field"] == "responseTime")
  |> group(columns: ["testName"])
  |> max()
  |> keep(columns: ["testName"])'''
  

def fluxConstructor(appName, runId, start, stop, requestName = ''):
  constr                                  = {}
  constr["source"]                        = 'from(bucket: "jmeter")\n'
  constr["range"]                         = '|> range(start: '+str(start)+', stop: '+str(stop)+')\n'
  constr["_measurement"]                  = {}
  constr["_measurement"]["response-time"] = '|> filter(fn: (r) => r["_measurement"] == "requestsRaw")\n'
  constr["_measurement"]["rps"]           = '|> filter(fn: (r) => r["_measurement"] == "requestsRaw")\n'
  constr["_measurement"]["errors"]        = '|> filter(fn: (r) => r["_measurement"] == "requestsRaw")\n'
  constr["metric"]                        = {}
  constr["metric"]["response-time"]       = '|> filter(fn: (r) => r["_field"] == "responseTime")\n'
  constr["metric"]["rps"]                 = '|> filter(fn: (r) => r["_field"] == "responseTime")\n' 
  constr["metric"]["errors"]              = '|> filter(fn: (r) => r["_field"] == "errorCount")\n'
  constr["runId"]                         = '|> filter(fn: (r) => r["runId"] == "'+runId+'")\n'
  constr["scope"]                         = {}
  constr["scope"]['all']                  = '|> group(columns: ["_field"])\n'
  constr["scope"]['each']                 = '|> group(columns: ["requestName"])\n'
  constr["scope"]['request']              = '|> filter(fn: (r) => r["requestName"] == "'+requestName+'")\n' + \
                                            '|> group(columns: ["requestName"])\n'
  constr["aggregation"]                   = {}
  constr["aggregation"]['avg']            = '|> mean()\n'
  constr["aggregation"]['median']         = '|> median()\n'
  constr["aggregation"]['90%-tile']       = '|> toFloat()\n' + \
                                            '|> quantile(q: 0.90)\n'
  constr["aggregation"]['95%-tile']       = '|> toFloat()\n' + \
                                            '|> quantile(q: 0.95)\n'
  constr["aggregation"]['count']          = '|> count()\n'
  constr["aggregation"]['sum']            = '|> sum()\n'
  constr["aggregation"]["rps"]            = '|> aggregateWindow(every: 1s, fn: count, createEmpty: false)\n' 
  return constr

  
