from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

from .api.agents import agents

app = FastAPI()
app.include_router(agents)

"""
Goal today: initialize a couple of characters locally using langchain generative agents
give characters local IDs
publish API endpoints so users can get a response for prompts
"""
