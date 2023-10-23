import re
import requests

print(requests.get(
    "http://127.0.0.1:8000/prompt/", 
    json={"agent_id": 1, "prompt": "What is your name?"}
    ).json()
)