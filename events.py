import json
import time
import datetime

def  NewFormLogEntries(logs):
    events = []
    GMT_FORMAT = '%a, %d %b %Y %H:%M:%S GMT+0800 (CST)'
    for log in logs:
        logdict = {"timestamp": "", "webview": "", "params": {}, "method": ""}
        localtime = time.localtime(log.get("timestamp"))
        logdict["timestamp"] = time.strftime(GMT_FORMAT, localtime)
        message = json.loads(log.get("message"))
        logdict["webview"] = message.get("webview")
        logdict["params"] = message.get("message").get("params")
        logdict["method"] = message.get("message").get("method")
        events.append(logdict)
    return events
