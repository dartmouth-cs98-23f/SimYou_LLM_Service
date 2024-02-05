import asyncio
from typing import AsyncIterable, List
import chromadb
import psycopg2


from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv, find_dotenv
import os

from langchain.callbacks import AsyncIteratorCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
from .models import ConversationInfo, InfoToInitAgent, Prompt, AgentInfo, ThumbnailInfo
from .memory.chroma_client_wrapper import ChromaClientWrapper
from .prompts import Prompts


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

game_db_name = os.getenv("GAME_DB_NAME")
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
    relevant_mems = asyncio.create_task(chroma_manager.retrieve_relevant_memories(
        agent_id=prompt.responderID,
        prompt=prompt.msg
    ))
    recent_mems = asyncio.create_task(get_recent_messages(prompt.convoID, prompt.responderID))
    questioner_info = asyncio.create_task(get_agent_info(prompt.questionerID))
    responder_info = asyncio.create_task(get_agent_info(prompt.responseID))
    await relevant_mems, recent_mems, questioner_info, responder_info

    if not questioner_info.result():
        raise HTTPException(
            status_code=400,
            detail=f"Bad questioner agent id: {prompt.questionerID}"
            )
    if not responder_info.result():
        raise HTTPException(status_code=400, 
        detail=f"Bad target agent id: {prompt.responderID}"
        )
    if not recent_mems.result():
        raise HTTPException(status_code=400, 
        detail=f"Bad conversation id: {prompt.convoID}"
        )

    gpt_prompt = Prompts.get_convo_prompt(
        prompt.msg, 
        responder_info.result(), 
        questioner_info.result(), 
        relevant_mems.result(), 
        recent_mems.result()
    )

    if prompt.streamResponse:
        return StreamingResponse(
            streaming_request(
                gpt_prompt,
                prompt.responderID,
                questioner_info.result()
                ), 
            media_type="text/event-stream")
    else:
        gpt = asyncio.create_task(
            model.apredict(gpt_prompt)
        )
        await gpt
        return gpt.result()

@agents.post('/api/agents/endConversation')
async def end_conversation(convoInfo: ConversationInfo):
    # Get ordered list of all messages from this conversation from back-end DB
    # Ideal format is [(AgentID, what they said), (AgentID, what they responded), ...] in order of least to most recent

    # Put all of messages into a prompt (ideally one from each agent's POV)

    # Send both prompts to GPT to summarize

    # Write conversation summaries to respective Chroma collections
    pass

@agents.post('/api/agents/generatePersona')
async def generate_agent(initInfo: InfoToInitAgent):
    # Put all of responses into a prompt (could play around with doing summaries of summaries)

    # Send to GPT

    # Send summary back to game-service

    pass

@agents.post('/api/agents/generateWorldThumbnail')
async def generate_thumbnail(initInfo: ThumbnailInfo):
    # 

    pass

@agents.post('/api/agents/getQuestion')
async def generate_question(initInfo: InfoToInitAgent):
    # Pseudocode very similar to generic generate response

    # Slight difference is we should expect that conversation might be un-initialized (i.e., this is the first message)
    pass

# # POST to prompt an agent with a prompt and stream the response
# @agents.post('/api/agents/prompt/stream')
# async def prompt_agent_stream(prompt: Prompt) -> StreamingResponse:
#     relevant_mems = asyncio.create_task(chroma_manager.retrieve_relevant_memories(
#         agent_id=prompt.targetAgentID,
#         prompt=prompt.msg
#     ))
#     recent_mems = asyncio.create_task(get_recent_messages(prompt.msg))
#     source_agent_info = asyncio.create_task(get_agent_info(prompt.sourceAgentID))
#     target_agent_info = asyncio.create_task(get_agent_info(prompt.targetAgentID))
#     await relevant_mems
#     await source_agent_info
#     await target_agent_info

#     # TODO: Pop the last k messages from the current conversation

#     if not source_agent_info.result():
#         raise HTTPException(status_code=400, detail=f"Bad source agent id: {prompt.sourceAgentID}")

#     if not target_agent_info.result():
#         raise HTTPException(status_code=400, detail=f"Bad target agent id: {prompt.targetAgentID}")

#     gpt_prompt = Prompts.get_convo_prompt(prompt.msg, target_agent_info.result(), source_agent_info.result(), mems.result())

#     # Don't need this any more
#     # new_mem = source_agent_info.result().firstName + " " + source_agent_info.result().lastName + " said to you: " + str(prompt.msg)

#     asyncio.create_task(chroma_manager.add_memory(agent_id=prompt.targetAgentID, memory=new_mem, unique_id=prompt.msgID))
#     return StreamingResponse(streaming_request(gpt_prompt, prompt.targetAgentID, source_agent_info.result()), media_type="text/event-stream")

# Stream response generator
async def streaming_request(prompt: str) -> AsyncIterable[str]:
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

# Helper method to get the info for an agent with id agentID
async def get_agent_info(agentID) -> AgentInfo:
    # db connection string
    results = None
    conn = psycopg2.connect(
        dbname=game_db_name,
        user=game_db_user,
        password=game_db_pass,
        host=game_db_url
        )
    try:
        cursor = conn.cursor()      
        query = f"""
        SELECT \"FirstName\", \"LastName\", \"Description\"
        FROM \"Users\"
        WHERE \"UserId\" = \'{agentID}\'
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


async def get_recent_messages(conversationID: str, responderID: str, num_popped = 10) -> List[str]:
    '''
    NOTE - ideally this function returns an ordered list of [(speaker, contents)]
    where the first entry in the list is the least recent and the last entry is the
    most recent, and where if speaker = person responding, then the speaker should
    be listed as "You"
    '''

    return ["fee", "fi", "fo", "fum"]
