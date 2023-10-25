from crypt import methods
from api.models import Agent, Query
from api.gen_agent import GenerativeAgent

from os import stat
from typing import List
from fastapi import HTTPException, APIRouter, Header

from dotenv import load_dotenv, find_dotenv
from langchain.chat_models import ChatOpenAI


# TODO: Move this to non-local storage
agents_db = {
    1: Agent(name="Joe",
            age=19, traits="anxious, artistic, talkative",
            status="Joe is moving into Dartmouth college as a freshman", 
            memories=["Joe misses his parents and is very homesick", "Joe feels tired from driving so far", "Joe likes his new dorm room", "Joe is hungry"]
    )
}

"""
Questions:
 - When should we load our dotenv (should we have an initialization function? or should we have call it every time the backend is queried (probably not the latter))
 - How do we store our agents? Currently modeling in a form that could easily be stored in a SQL database -- load into a generative agent on-demand, rather than keeping
        a bunch of generative agents in memory -- Could be slow, but it has the benefit of making our service stateless
 - How to use a vector-store that is indexed by agent so we don't have to rebuild a langchain generative agent every time we're queried.
        - Idea here would be to store basic details related to an agent in basic database (relational could work, document-oriented could work too) and memories in a separate vector store. Is this slow?
"""

"""
Road-map:
 - Test with locally stored agents
 - Test with a document-oriented database
 - Incorporate a vector-store -- research this
"""

agents = APIRouter()

# GET for all agents in database
@agents.get("/api/agents")
def get_agents():
    return {"agents" : agents_db}

# POST to create a new agent
@agents.post('/api/agents')
def add_agent(agentID: int, name: str, age: int, traits: str, status: str):
    agents_db[agentID] = Agent(name, age, traits, status)

# PUT to modify an agent
@agents.put('/api/agents')
def modify_agent(agentID: int, name: str, age: int, traits: str, status: str):
    agents_db[agentID].name = name
    agents_db[agentID].age = age
    agents_db[agentID].traits = traits
    agents_db[agentID].status = status

# DELETE to delete an agent by its ID
@agents.delete('/api/agents')
def delete_agent(agentID: int):
    agents_db[agentID] = Agent()

# POST to prompt an agent with a query
@agents.post('/api/agents/prompt')
def prompt_agent(agentID: int, query: str):
    if agentID not in agents_db.keys():
        raise HTTPException(status_code=404, detail="GenerativeAgent with id not found")
    load_dotenv(find_dotenv())
    LLM = ChatOpenAI(max_tokens=1500)  # Can be any LLM you want.

    #TODO: Get this part working
    # agent = GenerativeAgent(agents[agentID], LLM)
    # return agent.interview_agent(query.prompt)
    return {"id" : agentID, "query" : query}
    