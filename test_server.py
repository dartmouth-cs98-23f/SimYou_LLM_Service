import requests

# print(requests.get("http://127.0.0.1:8000/").json())

print(requests.get(
    "http://127.0.0.1:8000/prompt/", 
   params={'agentID' : 1, 'query' : 'lets test this out'}
    ).json()
)

# print(requests.get(
#     "http://127.0.0.1:8000/prompt/1/").json()
# )