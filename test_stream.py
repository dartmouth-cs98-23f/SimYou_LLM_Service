import json
import requests

# Test for the streaming api
def testRequest():
    url = "http://localhost:8000/api/agents/prompt"
    message = "Who was George Washington's wife?"
    agentID = "a6d8ef44-9b33-4421-9526-69af615e22cb"
    msgID = "a6d8ef44-9b33-4421-9526-69aoiaoifnf615"
    responseID = "a6d8ef44-9b33-6492-9526-69af615e22cb"
    data = {"sourceAgentID": agentID,
    "targetAgentID": agentID,
    "prompt": message}

    headers = {"Content-type": "application/json"}

    r = requests.post(url, data=json.dumps(data), headers=headers)
    print(r.text)

def testRequestWithStreaming():
    url = "http://localhost:8000/api/agents/prompt/stream"
    message = "Who was George Washington's wife?"
    agentID = "a6d8ef44-9b33-4421-9526-69af615e22cb"
    data = {"sourceAgentID": agentID,
    "targetAgentID": agentID,
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
testRequestWithStreaming()

"""
TODO: 
[ ] Update README.md
[ ] Look into keeping a persistent connection to Chroma
"""