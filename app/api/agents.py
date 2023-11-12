from typing import List
import asyncio
from typing import AsyncIterable
import chromadb
import psycopg2

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv, find_dotenv
import os

from langchain.callbacks import AsyncIteratorCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
from .models import Prompt, AgentInfo
from .memory.chroma_client_wrapper import ChromaClientWrapper


load_dotenv(find_dotenv())
chroma_url = os.getenv("CHROMA_DB")

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

game_db_url = os.getenv("GAME_DB_ADDRESS")
game_db_pass = os.getenv("GAME_DB_PASS")
game_db_user = os.getenv("GAME_DB_USER")

agents = APIRouter()

# POST to create a new agent
@agents.post('/api/agents')
def add_agent(agentID: int):
    chroma_manager.add_agent(agent_id=agentID)
    return

# DELETE to delete an agent by its ID
@agents.delete('/api/agents')
def delete_agent(agentID: int):
    chroma_manager.delete_agent(agent_id=agentID)
    return

# POST to prompt an agent with a prompt
@agents.post('/api/agents/prompt')
async def prompt_agent(prompt: Prompt):
    mems = asyncio.create_task(chroma_manager.retrieve_relevant_memories(
        agent_id=prompt.targetAgentID,
        prompt=prompt.prompt
    ))
    source_agent_info = asyncio.create_task(get_agent_info(prompt.sourceAgentID))
    target_agent_info = asyncio.create_task(get_agent_info(prompt.targetAgentID))
    await mems
    await source_agent_info
    await target_agent_info

    if not source_agent_info.result():
        raise HTTPException(status_code=400, detail=f"Bad source agent id: {prompt.sourceAgentID}")
    if not target_agent_info.result():
        raise HTTPException(status_code=400, detail=f"Bad target agent id: {prompt.targetAgentID}")

    gpt_prompt = get_gpt_prompt(prompt.prompt, target_agent_info.result(), source_agent_info.result(), mems.result())
    new_mem = source_agent_info.result().firstName + " " + source_agent_info.result().lastName + " said to you: " + str(prompt.prompt)
    asyncio.create_task(chroma_manager.add_memory(agent_id=prompt.targetAgentID, memory=new_mem, unique_id=prompt.msgID))

    gpt = asyncio.create_task(
        model.apredict(gpt_prompt)
    )
    await gpt
    new_mem = "You said to " + source_agent_info.result().firstName + " " + source_agent_info.result().lastName + ": " + "".join(gpt.result())
    asyncio.create_task(chroma_manager.add_memory(agent_id=prompt.targetAgentID, memory=new_mem, unique_id=prompt.responseID))
    return gpt.result()

# POST to prompt an agent with a prompt and stream the response
@agents.post('/api/agents/prompt/stream')
async def prompt_agent_stream(prompt: Prompt) -> StreamingResponse:
    mems = asyncio.create_task(chroma_manager.retrieve_relevant_memories(
        agent_id=prompt.targetAgentID,
        prompt=prompt.prompt
    ))
    source_agent_info = asyncio.create_task(get_agent_info(prompt.sourceAgentID))
    target_agent_info = asyncio.create_task(get_agent_info(prompt.targetAgentID))
    await mems
    await source_agent_info
    await target_agent_info

    if not source_agent_info.result():
        raise HTTPException(status_code=400, detail=f"Bad source agent id: {prompt.sourceAgentID}")

    if not target_agent_info.result():
        raise HTTPException(status_code=400, detail=f"Bad target agent id: {prompt.targetAgentID}")

    gpt_prompt = get_gpt_prompt(prompt.prompt, target_agent_info.result(), source_agent_info.result(), mems.result())
    new_mem = source_agent_info.result().firstName + " " + source_agent_info.result().lastName + " said to you: " + str(prompt.prompt)
    asyncio.create_task(chroma_manager.add_memory(agent_id=prompt.targetAgentID, memory=new_mem, unique_id=prompt.msgID))
    return StreamingResponse(streaming_request(gpt_prompt, prompt.targetAgentID, source_agent_info.result()), media_type="text/event-stream")

# Stream response generator
async def streaming_request(prompt: str, targetAgentID: str, sourceAgentInfo: AgentInfo, responseID="") -> AsyncIterable[str]:
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
        new_mem = "You said to " + sourceAgentInfo.firstName + " " + sourceAgentInfo.lastName + ": " + "".join(response)
        asyncio.create_task(chroma_manager.add_memory(agent_id=targetAgentID, memory=new_mem, unique_id=responseID))
        callback.done.set()
    await task

# Helper method to get the properly formatted gpt prompt
def get_gpt_prompt(message: str, targetAgentInfo: AgentInfo, sourceAgentInfo: AgentInfo, targetAgentMemories: List[str]):
    memories_str = ""
    for mem in targetAgentMemories:
        memories_str += mem
        memories_str += "\n"
    
    gpt_prompt = f"""
    You are a character with this description:
    {targetAgentInfo.description}
    
    You have these memories:
    {memories_str}

    Another character with the name {sourceAgentInfo.firstName} {sourceAgentInfo.lastName} has this description:
    
    {sourceAgentInfo.firstName} {sourceAgentInfo.lastName} says this to you:
    {message} 
    
    Please reply in a concise and conversational manner!
    """
    return gpt_prompt

# Helper method to get the info for an agent with id agentID
async def get_agent_info(agentID) -> AgentInfo:
    # db connection string
    results = None
    conn = psycopg2.connect(
        dbname="demo",
        user=game_db_user,
        password=game_db_pass,
        host=game_db_url
        )
    try:
        cursor = conn.cursor()      
        query = f"""
        SELECT \"FirstName\", \"LastName\", \"Description\"
        FROM \"Users\"
        WHERE \"Id\" = \'{agentID}\'
        """      
        cursor.execute(query)
        results = cursor.fetchall()[0]
        cursor.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print("no success", error)
    finally:
        if cursor:
            cursor.close()
        if results:
            return AgentInfo(results[0], results[1], results[2])