import asyncio
from typing import AsyncIterable, List
import chromadb

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv, find_dotenv
import os

from langchain.callbacks import AsyncIteratorCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage

from .request_models.DescribeAgentRequest import InitAgentInfo
from .request_models.EndConvoRequest import ConversationInfo
from .request_models.PromptRequest import PromptInfo

from .response_models.generateAgentResponse import AgentDescriptionModel
from .response_models.promptResponse import PromptResponse

from .memory.chroma_client_wrapper import ChromaClientWrapper
from .prompts import Prompts

from .memory.agent_retrieval import get_agent_info
from .memory.conversation_retrieval import get_recent_messages


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
async def prompt_agent(prompt: PromptInfo):
    """
    This function uses genAI to return a response to the prompt posed by questionerID from the perspective of responderID.

    Args:
    prompt (PromptInfo): The PromptInfo object which contains the world ID, owner ID, and description.

    Returns:
    PromptResponse: a json argument of {response: str}
    """
    if prompt.convoID:
        recent_mems = asyncio.create_task(get_recent_messages(prompt.convoID, prompt.responderID))
        await recent_mems
    relevant_mems = asyncio.create_task(chroma_manager.retrieve_relevant_memories(
        agent_id=prompt.recipientId,
        prompt=prompt.content
    ))
    if prompt.conversationId:
        recent_mems = asyncio.create_task(get_recent_messages(prompt.conversationId, prompt.recipientId))
        questioner_info = asyncio.create_task(
            get_agent_info(
                prompt.senderId, 
                game_db_user=game_db_user, 
                game_db_url=game_db_url, 
                game_db_name=game_db_name, 
                game_db_pass=game_db_pass
            )
        )
    responder_info = asyncio.create_task(
        get_agent_info(
            prompt.recipientId,
            game_db_user=game_db_user, 
            game_db_url=game_db_url, 
            game_db_name=game_db_name, 
            game_db_pass=game_db_pass
        )
    )
    await relevant_mems, questioner_info, responder_info

    if prompt.conversationId:
        await recent_mems

    # Raise HTTPException if any of the tasks return None
    if not questioner_info.result():
        raise HTTPException(
            status_code=400,
            detail=f"Bad questioner agent id: {prompt.questionerID}"
        )
    if not responder_info.result():
        raise HTTPException(status_code=400,
        detail=f"Bad target agent id: {prompt.responderID}"
        )
    if prompt.convoID and not recent_mems.result():
        raise HTTPException(status_code=400,
        detail=f"Bad conversation id: {prompt.convoID}"
    )

    # Generate a prompt for the GPT model using the results of the tasks
    if prompt.respondWithQuestion:
        gpt_prompt = Prompts.get_question_prompt(
            prompt.msg,
            responder_info.result(),
            questioner_info.result(),
            relevant_mems.result(),
            recent_mems.result()
        )
    else:
        gpt_prompt = Prompts.get_convo_prompt(
            prompt.msg,
            responder_info.result(),
            questioner_info.result(),
            relevant_mems.result(),
        )


    # If the response should be streamed, return a StreamingResponse
    if prompt.streamResponse:
        # TODO: Can we return this in a json?
        return StreamingResponse(
            streaming_request(gpt_prompt),
            media_type="text/event-stream",
        )
    else:
        # Otherwise, create a task to generate a response from the GPT model and return the result
        gpt = asyncio.create_task(
            model.apredict(gpt_prompt)
        )
        await gpt
        responseItem = PromptResponse(response=gpt.result())
        json_compatible_item_data = jsonable_encoder(responseItem)
        return JSONResponse(content=json_compatible_item_data)

@agents.post('/api/agents/endConversation')
async def end_conversation(convoInfo: ConversationInfo):
    # Get ordered list of all messages from this conversation from back-end DB
    # Ideal format is [(AgentID, what they said), (AgentID, what they responded), ...] in order of least to most recent

    # Put all of messages into a prompt (ideally one from each agent's POV)

    # Send both prompts to GPT to summarize
    
    # Write conversation summaries to respective Chroma collections
    pass

@agents.post('/api/agents/generatePersona', response_model=AgentDescriptionModel)
async def generate_agent(initInfo: InitAgentInfo):
    # TODO: initialize a vector store for this agent...
    # Put all of responses into a prompt (could play around with doing summaries of summaries)
    gpt_prompt = Prompts.get_agent_persona_prompt(initInfo.questions, initInfo.answers)
    # Send to GPT
    gpt = asyncio.create_task(
            model.apredict(gpt_prompt)
        )
    await gpt
    # Send summary back to game-service
    responseItem = AgentDescriptionModel(response=gpt.result())
    json_compatible_item_data = jsonable_encoder(responseItem)
    return JSONResponse(content=json_compatible_item_data)



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

