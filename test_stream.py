import json
import requests

# tests for the streaming api

def testRequest():
        url = "http://localhost:8000/api/agents/prompt"
        message = "What is 10 + 12?"
        agentID = "test"
        data = {"agentID": agentID,
                "prompt": message}

        headers = {"Content-type": "application/json"}

        r = requests.post(url, data=json.dumps(data), headers=headers, stream=True)
        if r.status_code != 200:
                print("Error!")
        try:
                for chunk in r.iter_content(1024):
                        if chunk:
                               print(chunk)
        except requests.exceptions.ChunkedEncodingError as ex:
                print(f"Invalid chunk encoding {str(ex)}")

       
testRequest()