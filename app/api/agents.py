import asyncio
from typing import AsyncIterable

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from dotenv import load_dotenv, find_dotenv
from langchain.callbacks import AsyncIteratorCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage

from .models import Prompt

agents = APIRouter()

# GET for all agents in database
@agents.get("/api/agents")
def get_agents():
    return

# POST to create a new agent
@agents.post('/api/agents')
def add_agent(agentID: int, name: str, age: int, traits: str, status: str):
    return
# PUT to modify an agent
@agents.put('/api/agents')
def modify_agent(agentID: int, name: str, age: int, traits: str, status: str):
    return
# DELETE to delete an agent by its ID
@agents.delete('/api/agents')
def delete_agent(agentID: int):
    return

# POST to prompt an agent with a prompt
@agents.post('/api/agents/prompt')
async def prompt_agent(prompt: Prompt) -> StreamingResponse:
    load_dotenv(find_dotenv())
    return StreamingResponse(streaming_request(prompt.prompt), media_type="text/event-stream")

# Stream response generator
async def streaming_request(prompt: str) -> AsyncIterable[str]:
    """Generator for each chunk received from OpenAI as response"""
    callback = AsyncIteratorCallbackHandler()
    model = ChatOpenAI(
        streaming=True,
        verbose=True,
        callbacks=[callback],
    )

    task = asyncio.create_task(
        model.agenerate(messages=[[HumanMessage(content=prompt)]])
    )

    try:
        async for token in callback.aiter():
            yield token
    except Exception as e:
        print(f"Caught exception: {e}")
    finally:
        callback.done.set()

    await task