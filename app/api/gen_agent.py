"""
All functionality relating to interfacing with langchain generative agents
"""

import math
from mimetypes import init
import faiss
from langchain_experimental.generative_agents import GenerativeAgent, GenerativeAgentMemory

from datetime import datetime, timedelta
from typing import List

from langchain.chat_models import ChatOpenAI
from langchain.docstore import InMemoryDocstore
from langchain.embeddings import OpenAIEmbeddings
from langchain.retrievers import TimeWeightedVectorStoreRetriever
from langchain.vectorstores import FAISS

from .models import Agent

"""
TOOD: Move these so they're not poluting the name space
"""
def relevance_score_fn(score: float) -> float:
    """Return a similarity score on a scale [0, 1]."""
    # This will differ depending on a few things:
    # - the distance / similarity metric used by the VectorStore
    # - the scale of your embeddings (OpenAI's are unit norm. Many others are not!)
    # This function converts the euclidean norm of normalized embeddings
    # (0 is most similar, sqrt(2) most dissimilar)
    # to a similarity function (0 to 1)
    return 1.0 - score / math.sqrt(2)


def create_new_memory_retriever():
    """Create a new vector store retriever unique to the agent."""
    # Define your embedding model
    embeddings_model = OpenAIEmbeddings()
    # Initialize the vectorstore as empty
    embedding_size = 1536
    index = faiss.IndexFlatL2(embedding_size)
    vectorstore = FAISS(
        embeddings_model.embed_query,
        index,
        InMemoryDocstore({}),
        {},
        relevance_score_fn=relevance_score_fn,
    )
    return TimeWeightedVectorStoreRetriever(
        vectorstore=vectorstore, other_score_keys=["importance"], k=15
    )

class GenerativeAgent:

    def __init__(self, agent: Agent, llm) -> None:
        memory = GenerativeAgentMemory(
            llm=llm,
            memory_retriever=create_new_memory_retriever(),
            verbose=False,
            reflection_threshold=8,  # we will give this a relatively low number to show how reflection works
        )

        self.genAgent = GenerativeAgent(
            name = agent.name,
            age = agent.age,
            traits = agent.traits,
            status = agent.status,
            memory_retriver = create_new_memory_retriever(),
            llm = llm,
            memory = memory
        )

        for observation in agent.memories:
            self.genAgent.memory.add_memory(observation)
    
    def interview_agent(self, message: str) -> str:
        
        # return self.genAgent.llm.predict(message)
        return self.genAgent.name
        