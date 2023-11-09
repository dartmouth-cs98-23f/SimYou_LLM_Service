import asyncio
from typing import AsyncIterable
import chromadb

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from dotenv import load_dotenv, find_dotenv
import os

from langchain.callbacks import AsyncIteratorCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage

from .models import Prompt
from .memory.chroma_client_wrapper import ChromaClientWrapper


load_dotenv(find_dotenv())
chroma_url = os.getenv("CHROMA_DB")
openai_api_key = os.getenv("OPENAI_API_KEY")

chroma_client = chromadb.HttpClient(
    host = chroma_url,
    port="8000"
)

chroma_manager = ChromaClientWrapper(chroma_client)

secret_key = os.getenv("OPENAI_API_KEY")
model = ChatOpenAI(
    streaming=True,
    verbose=True,
    openai_api_key=secret_key
)

agents = APIRouter()

# GET for all agents in database
@agents.get("/api/agents")
def get_agents():
    return

# POST to create a new agent
@agents.post('/api/agents')
def add_agent(agentID: int, name: str, age: int, traits: str, status: str):
    chroma_manager.add_agent(agent_id=agentID)
    return

# PUT to modify an agent
@agents.put('/api/agents')
def modify_agent(agentID: int, name: str, age: int, traits: str, status: str):
    return

# DELETE to delete an agent by its ID
@agents.delete('/api/agents')
def delete_agent(agentID: int):
    chroma_manager.delete_agent(agent_id=agentID)
    return

# POST to prompt an agent with a prompt
@agents.post('/api/agents/prompt')
async def prompt_agent(prompt: Prompt) -> StreamingResponse:
    mems = asyncio.create_task(chroma_manager.retrieve_relevant_memories(
        agent_id=prompt.agentID,
        prompt=prompt.prompt
    ))
    await mems 
    # TODO: Make async
    new_mem = "PLACEHOLDER_FOR_NAME said to you: " + str(prompt.prompt)
    asyncio.create_task(chroma_manager.add_memory(agent_id=prompt.agentID, memory=prompt.prompt))
    return StreamingResponse(streaming_request(prompt.prompt, prompt.agentID), media_type="text/event-stream")

# Stream response generator
async def streaming_request(prompt: str, agentID: str) -> AsyncIterable[str]:
    """Generator for each chunk received from OpenAI as response"""
    callback = AsyncIteratorCallbackHandler()
    model.callbacks = [callback]
    task = asyncio.create_task(
        model.agenerate(messages=[[HumanMessage(content=prompt)]])
    )

    response = []
    try:
        async for token in callback.aiter():
            yield token
            response.append(token)
    except Exception as e:
        print(f"Caught exception: {e}")
    finally:
        callback.done.set()

    await task

    new_mem = "You said to PLACEHOLDER: " + "".join(response)
    asyncio.create_task(chroma_manager.add_memory(agent_id=agentID, memory=new_mem))

