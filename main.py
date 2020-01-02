from selenium import webdriver
import json

caps = {
    'browserName': 'chrome',
    'loggingPrefs': {
        'browser': 'ALL',
        'driver': 'ALL',
        'performance': 'ALL',
    },
    'goog:chromeOptions': {
        'perfLoggingPrefs': {
            'enableNetwork': True,
        },
        'w3c': False, 
    },
}
# options = webdriver.ChromeOptions()
# options.add
driver = webdriver.Chrome(desired_capabilities=caps)
driver.get("http://www.baidu.com")
driver.get("http://www.zhihu.com")
logs = driver.get_log('performance')
with open('test.json', 'w') as f:
    f.write(json.dumps(logs))
driver.quit()