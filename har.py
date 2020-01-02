import json
import time
import re
import logging
import urllib.parse

from events import NewFormLogEntries

params = {
				"requestId": "",
				"documentUrl": "",
				"request": {
							"headers": {},
							"method": "",
							"postData": "",
							"url": ""
							},
				"wallTime": "",
				"timestamp": "",
				"redirectResponse": {
							"headers": {},
							"headersText": "",
							"mimeType": "",
							"requestHeaders": {},
							"requestHeadersText": "",
							"status": "",
							"statusText": "",
							"url": "",
							"timing": {},
							"protocal": ""
				}
			}
from urllib import parse
def getCurrentPageId(har):
	return "page_{}".format(len(har["pages"]))

def ParseQuertString(req):
	queryString = []
	reqUrl = parse.urlparse(req.get("url")).query
	print(reqUrl)
	urlList =  [i for i in reqUrl.split("&")]
	if len(urlList) > 1:
		for url in urlList:
			url = url.split("=")
			singUrl = {}
			singUrl["name"] = url[0]
			singUrl["value"] = url[1]
			queryString.append(singUrl)
	return queryString

def EpochToTime(timestamp):
	GMT_FORMAT = '%a, %d %b %Y %H:%M:%S GMT+0800 (CST)'	
	localtime = time.localtime(timestamp)
	return time.strftime(GMT_FORMAT, localtime)

def GetEntryByRequestId(har, id):
	for e in har.get("entries"):
		if e.get("requestId") == id:
			return e

def parseHeaders(headers):
	result = []
	for key, value in headers.items():
		headerdict = {}
		headerdict["name"] = key
		headerdict["value"] = value
		result.append(headerdict)
	return result

def setHeadersSize(headers):
	header = "{} {} {}\r\n".format(headers.get("httpVersion"), headers.get("status"), headers.get("statusText"))
	for mess in headers.get("headers"):
		header = header + "{}: {}\r\n".format(mess.get("name"), mess.get("value"))
	header + "\r\n"
	return len(header.encode("utf-8"))
	
def ParseCookies(req):
	cookiesList = []
	for mess in req.get("headers"):
		if mess["name"] == "cookie":
			cookies = mess["value"].split(";")
			for mid in cookies:
				cook = {}
				cookie = mid.strip()
				parts = cookie.split("=")
				cook["name"] = parts[0]
				cook["value"] = parts[1]
				cookiesList.append(cook)
	return cookiesList

def ProcessResponse(entry, timestamp, response):
	entry["request"]["httpVersion"] = response.get("protocol")
	entry["request"]["headers"] = parseHeaders(response.get("requestHeaders"))
	entry["request"]["headersSize"] = setHeadersSize(response.get("requestHeaders"))
	entry["request"]["cookies"] = ParseCookies(entry.get("request").get("cookies"))
	
	resp = {
		"status": response["status"],
		"statusText": response["statusText"],
		"httpVersion": entry["request"].get("httpVersion"),
		'headers': parseHeaders(response.get("headers")),
		"cookies": ParseCookies(response.get("cookies")),
		"content": {"size": "", "mimeType": "", "compression": ""},
		"redirectUrl": "",
		"headerSize": setHeadersSize(parseHeaders(response.get("headers"))),
		"bodySize": "",
		"timestamp": timestamp
	}
	entry["response"] = resp
	entry["response"]["content"]["mimeType"] = response.get("mimeType")
 
	blocked = response["timing"]["dnsStart"]
	if blocked < 0.0:
		blocked == 0.0
	dns = response["timing"]["dnsEnd"] - response["Timing"]["dnsStart"]
	if dns < 0.0:
		dns = 0.0
	connect = response["timing"]["connectEnd"] - response["timing"]["connectStart"]
	if connect < 0.0:
		connect = 0.0
	send = response["timing"]["sendEnd"] - response["timing"]["connectStart"]
	if send < 0.0:
		send = 0.0
	wait = response["timing"]["receiveHeadersEnd"] - response["timing"]["sendEnd"]
	if wait < 0.0:
		wait = 0.0
	ssl = response["timing"]["sslEnd"] - response["timing"]["sslStart"]
	if ssl < 0.0:
		ssl = 0.0
	timings = {
		"blocked": blocked,
		"dns": dns,
		"connect": connect,
		"send": send,
		"wait": wait,
		"receive": 0.0 - response.get("timing").get("requestTime")*1000 + response.get("timing").get("receiveHeaderSEnd"),
		"ssl": ssl
	}
	entry["timings"] = timings
	return entry["request"], entry["response"], entry["timings"]

def CurrentPage(har):
	if len(har["pages"]) < 1:
		print("page to low")
	return len(har["pages"])-1

def from_page(chromelogs):
	har = {}
	har["version"] = "1.1"
	har["creater"] = {"name": "quicksmoke capture har", "version": "1.1"}
	har["pages"] = []
	har["entries"] = []
	for event in chromelogs:
		if event.get("method") == "Page.frameStartedLoading":
			page = {}
			page["startedDateTime"] = event.get("timestamp")
			page["id"] = getCurrentPageId(har)
			page["title"] = ""
			page["pageTimings"] = {"onContentLoad": "", "onLoad": ""}
			page["timestamp"] = ""
			har["pages"].append(page)
		if event.get("method") == "Network.requestWillBeSent":
			if len(har["pages"]) < 1:
				print("start request")
			params = {}
			for key, value in event.get("params").items():
				params[key] = value
		# 	if params.get("request").get("postData"):
		# 		bodysize = len(params.get("request").get("postData"))
		# 	else:
		# 		bodysize = 0
			req = {
				"method": params.get("request").get("method"),
				"url": params.get("request").get("url"),
				"httpVersion": "",
				"headers": "",
				"queryString": ParseQuertString(params.get("request")),
				"cookies": "",
				"headersSize": "",
				"bodySize": "",
				"timestamp": params.get("timestamp")
			}
		# 	entry = {
		# 		"startDateTime": EpochToTime(params.get("wallTime")),
		# 		"time": "",
		# 		"request": req,
		# 		"response": {},
		# 		"cache": {},
		# 		"timings": "",
		# 		"pageref": getCurrentPageId(har),
		# 		"requestId": params.get("requestId")
		# 	}
		# 	if params.get("redirectResponse"):
		# 		lastEntry = GetEntryByRequestId(har, params.get("requestId"))
		# 		lastEntry["requestId"] = lastEntry.get("requestId") + "r"
		# 		lastEntry["request"], lastEntry["response"], lastEntry["timings"] = ProcessResponse(lastEntry, params.get("timestamp"), params.get("redirectResponse"))
		# 		lastEntry["response"]["redirectUrl"] = params.get("request").get("url")
		# 		lastEntry["timings"]["receive"] = 0.0
		# 	har["entries"].append(entry)
		# 	pagenum = CurrentPage(har)
		# 	if not har["pages"][pagenum]["title"]:
		# 		har["pages"][pagenum]["title"] = req.get("url")
		# 		har["pages"][pagenum]["timestamp"] = params["timestamp"]

		if event.get("method") == "":
			pass
		if event.get("method") == "":
			pass
		if event.get("method") == "":
			pass
		if event.get("method") == "":
			pass
	return har





import json
if __name__ == '__main__':
	with open('test.json', 'r') as f:
		info = json.loads(f.read())
	# for key, value in info[0].items():
	# 	print(key, value)
	# print(info[0])
	logs = NewFormLogEntries(info)
	# har = {
	# 	"version": "1.2",
	# 	"creator": {"name": "har capture", "version": "0.1"},
	# 	"pages": [],
	# 	"entries": []
	# }
	# print(logs[0])
	# for log in logs:
	# 	if log.get("method") == "Page.frameStartedLoading":
	# 		page = {"startDateTime": log.get(""), ""}

	har = from_page(logs)
	with open('test.har', 'w') as f:
		f.write(json.dumps(har))
	print(har)
  