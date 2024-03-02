import asyncio
import uuid
from typing import AsyncIterable, List
from app.api.request_models.QuestionRequest import QuestionInfo
from app.api.response_models.avatarResponse import AvatarResponse
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
from .request_models.GenerateAvatarRequest import GenerateAvatarInfo

from .response_models.generateAgentResponse import AgentDescriptionModel
from .response_models.promptResponse import PromptResponse

from .memory.chroma_client_wrapper import ChromaClientWrapper
from .prompts import Prompts

from .memory.agent_retrieval import get_agent_info
from .memory.conversation_retrieval import get_recent_messages, get_agent_perspective

from .helpers.backoff_retry import retry_with_exponential_backoff

from openai import OpenAI
import base64
import boto3
import rembg
from PIL import Image
from io import BytesIO


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

# Get AWS keys from environment variables
aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_public_key = os.getenv("AWS_ACCESS_KEY_ID")

# Initialize OpenAI and S3 clients
client = OpenAI()
s3 = boto3.resource('s3', region_name='us-east-2', aws_access_key_id=aws_public_key, aws_secret_access_key=aws_secret_key)

# Define S3 bucket name
bucket_name = 'sim-you-media'

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
    
    recent_mems = asyncio.create_task(get_recent_messages(
        game_db_name=game_db_name,
        game_db_user=game_db_user,
        game_db_pass=game_db_pass,
        game_db_url=game_db_url,
        conversationID=prompt.conversationId
        )
    )
    
    relevant_mems = asyncio.create_task(
        chroma_manager.retrieve_relevant_memories(
            agent_id=prompt.recipientId,
            prompt=prompt.content
        )
    )
    sender_info = asyncio.create_task(
        get_agent_info(
            prompt.senderId, 
            isUser=True,    # sender is always a user, right?
            game_db_user=game_db_user, 
            game_db_url=game_db_url, 
            game_db_name=game_db_name, 
            game_db_pass=game_db_pass,
        )
    )
    responder_info = asyncio.create_task(
        get_agent_info(
            prompt.recipientId,
            isUser=prompt.isRecipientUser,
            game_db_user=game_db_user, 
            game_db_url=game_db_url, 
            game_db_name=game_db_name, 
            game_db_pass=game_db_pass
        )
    )
    await sender_info, responder_info        

    # Raise HTTPException if any of the tasks return None
    if not sender_info.result():
        raise HTTPException(status_code=400,
            detail=f"Bad sender agent id: {prompt.senderId}"
        )
    if not responder_info.result():
        raise HTTPException(status_code=400,
            detail=f"Bad target agent id: {prompt.recipientId}"
        )
    
    await recent_mems, relevant_mems
    if recent_mems.result() == [] or not recent_mems.result():
        gpt_prompt = Prompts.get_convo_prompt(
            prompt.content,
            responder_info.result(),
            sender_info.result(),
            None,
            relevant_mems.result()
        )
    else:
        # Generate a prompt for the GPT model using the results of the tasks
        gpt_prompt = Prompts.get_convo_prompt(
            prompt.content,
            responder_info.result(),
            sender_info.result(),
            recent_mems.result(),
            relevant_mems.result()
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

# POST to prompt an agent with a prompt
@agents.post('/api/agents/question')
async def question_agent(questionInfo: QuestionInfo):
    if questionInfo.conversationId:
        recent_mems = asyncio.create_task(get_recent_messages(
            game_db_name=game_db_name,
            game_db_user=game_db_user,
            game_db_pass=game_db_pass,
            game_db_url=game_db_url,
            conversationID=questionInfo.conversationId))
        # questionInfo.recipientId
    
    sender_info = asyncio.create_task(
        get_agent_info(
            questionInfo.senderId, 
            isUser=True,
            game_db_user=game_db_user, 
            game_db_url=game_db_url, 
            game_db_name=game_db_name, 
            game_db_pass=game_db_pass
        )
    )
    responder_info = asyncio.create_task(
        get_agent_info(
            questionInfo.recipientId,
            isUser=questionInfo.isRecipientUser,
            game_db_user=game_db_user, 
            game_db_url=game_db_url, 
            game_db_name=game_db_name, 
            game_db_pass=game_db_pass
        )
    )

    await sender_info, responder_info

    # Raise HTTPException if any of the tasks return None
    if not sender_info.result():
        raise HTTPException(
            status_code=400,
            detail=f"Bad sender agent id: {questionInfo.senderId}"
        )
    if not responder_info.result():
        raise HTTPException(status_code=400,
            detail=f"Bad target agent id: {questionInfo.recipientId}"
        )
    # Check for recent mems error
    # Generate a prompt for the GPT model using the results of the tasks
    chroma_prompt = Prompts.get_question_prompt(
        responder_info.result(),
        sender_info.result(),
    )
    relevant_mems = chroma_manager.retrieve_relevant_memories(
        agent_id=questionInfo.recipientId,
        prompt=chroma_prompt
    )

    await recent_mems

    if recent_mems.result() == [] or not recent_mems.result():
        gpt_prompt = Prompts.get_question_prompt(
            responder_info.result(),
            sender_info.result(),
            relevant_mems,
            None,
        )
    else:
        gpt_prompt = Prompts.get_question_prompt(
            responder_info.result(),
            sender_info.result(),
            relevant_mems,
            recent_mems.result(),
        )

    # If the response should be streamed, return a StreamingResponse
    if questionInfo.streamResponse:
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
    # Get the most recent messages from the conversation
    recent_messages = await asyncio.create_task(get_recent_messages(
            game_db_name=game_db_name,
            game_db_user=game_db_user,
            game_db_pass=game_db_pass,
            game_db_url=game_db_url,
            conversationID=convoInfo.conversationId))
    
    agentA_info = await asyncio.create_task(
        get_agent_info(
            agentID=convoInfo.participantA, 
            isUser=convoInfo.isParticipantUserA,
            game_db_user=game_db_user, 
            game_db_url=game_db_url, 
            game_db_name=game_db_name, 
            game_db_pass=game_db_pass
        )
    )
    agentB_info = await asyncio.create_task(
        get_agent_info(
            agentID=convoInfo.participantB, 
            isUser=convoInfo.isParticipantUserB,
            game_db_user=game_db_user, 
            game_db_url=game_db_url, 
            game_db_name=game_db_name, 
            game_db_pass=game_db_pass
        )
    )

    convo_for_agentA = get_agent_perspective(convo_transcript=recent_messages,
                                              for_agent=convoInfo.participantA,
                                              other_agent_name=agentB_info.username
                                              )
    convo_for_agentB = get_agent_perspective(convo_transcript=recent_messages,
                                                for_agent=convoInfo.participantB,
                                                other_agent_name=agentA_info.username
                                                )

    # Make a prompt for each agent
    prompt_for_agentA = Prompts.get_convo_summary_prompt(convo_transcript=convo_for_agentA, responder=agentA_info, otherAgent=agentB_info)
    prompt_for_agentB = Prompts.get_convo_summary_prompt(convo_transcript=convo_for_agentB, responder=agentB_info, otherAgent=agentA_info)

    # Send both prompts to GPT to summarize
    gpt_agentA = await asyncio.create_task(model.apredict(prompt_for_agentA))
    gpt_agentB = await asyncio.create_task(model.apredict(prompt_for_agentB))

    # Write both to correct Chroma collections
    await asyncio.create_task(chroma_manager.add_memory(convoInfo.participantA, gpt_agentA))
    await asyncio.create_task(chroma_manager.add_memory(convoInfo.participantB, gpt_agentB))
    return

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
    responseItem = AgentDescriptionModel(description=gpt.result())
    return responseItem

# TODO: Handle OpenAI rate limiting - 5 images per minute.
@agents.post('/api/agents/generateAvatar')
async def generate_avatar(avatarInfo: GenerateAvatarInfo):
     # Get prompt for generating the thumbnail
    prompt = Prompts.get_avatar_prompt(avatarInfo.appearanceDescription)

    # Generate image using OpenAI's DALL-E model
    response = generate_avatar_with_retries(prompt)

    # Decode image
    image_bytes = base64.b64decode(response.data[0].b64_json)

    # Remove image background
    # TODO: Do this asynchronously
    avatar_bytes = rembg.remove(image_bytes)

    # Crop for headshot
    headshot_img = Image.open(BytesIO(avatar_bytes))
    headshot_img.crop((50, 0, 150, 100))
    headshot_in_mem = BytesIO()
    headshot_img.save(headshot_in_mem, "PNG")

    # Build file names
    avatar_file_name = "avatars/agents/" + str(uuid.uuid1()) + ".png"
    headshot_file_name = "headshots/agents/" + str(uuid.uuid1()) + "-headshot.png"

    # Put images in S3 bucket
    obj = s3.Object(bucket_name, avatar_file_name)
    obj.put(Body=avatar_bytes)
    obj = s3.Object(bucket_name, headshot_file_name)
    obj.put(Body=headshot_in_mem.getvalue())

    # Get bucket location
    location = boto3.client('s3').get_bucket_location(Bucket=bucket_name)['LocationConstraint']

    # Get URLs
    avatar_url = "https://%s.s3-%s.amazonaws.com/%s" % (bucket_name, location, avatar_file_name)
    headshot_url = "https://%s.s3-%s.amazonaws.com/%s" % (bucket_name, location, headshot_file_name)
    
    response_obj = AvatarResponse(avatarURL=avatar_url, headshotURL=headshot_url)
    return response_obj


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



@retry_with_exponential_backoff
def generate_avatar_with_retries(prompt):
    response = client.images.generate(
        model="dall-e-2",
        prompt=prompt,
        size="256x256",
        quality="standard",
        n=1,
        response_format="b64_json",
    )
    return response