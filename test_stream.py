import json
import requests

# tests for the streaming api
url = "http://localhost:8000/api/agents/prompt"
message = "Hello, how are you?"
agentID = "test"
data = {"agentID": agentID,
        "prompt": message}

headers = {"Content-type": "application/json"}

r = requests.post(url, data=json.dumps(data), headers=headers, stream=True)
for chunk in r.iter_content(1024):
    print(chunk)