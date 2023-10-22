from fastapi import FastAPI

app = FastAPI()

"""
Goal today: initialize a couple of characters locally using langchain generative agents
give characters local IDs
publish API endpoints so users can get a response for prompts
"""

@app.get('/')
async def index():
    return {"Real": "Python"}