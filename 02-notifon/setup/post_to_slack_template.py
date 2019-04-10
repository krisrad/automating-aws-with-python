import requests
url = 'https://hooks.slack.com/services/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'
data = {"text": "Hello World. This is RK."}
requests.post(url, json=data)
