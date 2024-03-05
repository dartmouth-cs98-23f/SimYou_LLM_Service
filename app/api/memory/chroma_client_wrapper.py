from http import client
import chromadb
import heapq
import datetime
import random


class ChromaClientWrapper:

    def __init__(self, client: chromadb.Client):
        """
        Initialize ChromaClientWrapper with a chromadb.Client object.

        Args:
            client (chromadb.Client): The chromadb client object.
        """
        self.client = client

    def dateTime_str_to_time(self, str):
        """
        Converts a datetime string to a datetime object.

        Args:
            str (str): A string representing a datetime.

        Returns:
            datetime.datetime: A datetime object.
        """
        date, time = str.split(" ")
        year, month, day = date.split("-")
        hour, minute, seconds = time.split(":")
        second, ms = seconds.split(".")
        return datetime.datetime(int(year), int(month), int(day), int(hour), int(minute), int(second), int(ms))


    async def add_memory(self, agent_id: str, memory: str, unique_id=""):
        """
        Adds a memory to the collection belonging to the agent.
        NOTE: We might need to maintain another database to handle the memory IDs

        Args:
            agent_id (str): The id of the agent.
            memory (str): The memory to be added.
            unique_id (str, optional): The unique id for the memory. Defaults to "".

        Raises:
            ValueError: If the memory cannot be added.
        """
        
        COLLECTION = self.client.get_or_create_collection(agent_id)
        now = datetime.datetime.now()

        # Generate unique ID
        if not unique_id:
            timestamp = int(datetime.datetime.timestamp(now)) * 1000
            unique_id = f"{timestamp}-{random.randint(1, 1000)}"

        try:
            COLLECTION.add(
                ids=[unique_id],
                documents=[memory],
                metadatas=[{'last-touched':str(now)}]
            )
        except ValueError as e:
            return

        

    def add_agent(self, agent_id: str):
        """
        Initializes a collection in the client corresponding to the agent_id.
        NOTE: We might expand this implementation to include a core memory / stable traits


        Args:
            agent_id (str): The id of the agent.
        """
        self.client.get_or_create_collection(agent_id)
    
    def delete_agent(self, agent_id: str):
        """
        Deletes a collection in the client corresponding to the agent_id.

        Args:
            agent_id (str): The id of the agent.

        Raises:
            ValueError: If the collection does not exist.
        """

        try:
            self.client.delete_collection(agent_id)
        except ValueError as e:
            #TODO: figure out a better way to handle this
            return


    async def retrieve_relevant_memories(self, agent_id: str, prompt: str, k=10, mem_boost_seconds_threshold=600, cutoff=1.50):
        """
        Retrieves the most relevant memories for the given agent and prompt.

        Args:
            agent_id (str): The id of the agent.
            prompt (str): The prompt for the memory retrieval.
            k (int, optional): The number of memories to retrieve. Defaults to 10.
            mem_boost_seconds_threshold (int, optional): The threshold for boosting recent memories. Defaults to 600.
            cutoff (float, optional): The similarity cutoff for memory retrieval. Defaults to 1.50.

        Returns:
            list: The list of most relevant memories.
        """

        most_relevant = []

        now = datetime.datetime.now()

        # Grab the agent's memory
        COLLECTION = self.client.get_or_create_collection(agent_id)
        results = None
        # Query the agent with the prompt and get <= 20 most semantically relevant memories
        try:
            results = COLLECTION.query(query_texts=[prompt], n_results=20)
        except Exception as e:
            return []
        finally:
            if not results:
                return []
            ids, documents, distances, metadatas = results['ids'][0], results['documents'][0], results['distances'][0], results['metadatas'][0]

            for i in range(len(ids)):
                metadata, id, document, distance = metadatas[i], ids[i], documents[i], distances[i]

                # Adjust score to favor newer memories and (eventually) more salient memories
                # Need to be careful about weighting using time -- beware the case of essentially wiping an agent's memory overnight
                # due to time elapsing
                # To avoid this case, let's just give memories that were last touched within the last 5 minutes a similarity boost -- should have
                # the desired effect for technigala
                # last_touched_str = metadata['last-touched']
                # last_touched = self.dateTime_str_to_time(last_touched_str)
                # time_elapsed = now - last_touched

                # if time_elapsed.seconds <= mem_boost_seconds_threshold:
                #     distance *= .80
                
                if not most_relevant or -1 * distance < most_relevant[0][0]:
                    heapq.heappush(most_relevant, (-1 * distance, document, id))
                
                if len(most_relevant) > k:
                    heapq.heappop(most_relevant)
                
            ret = []
            for mem in most_relevant:
                # Only keep memories with distance below cut-off
                if mem[0] * -1 < cutoff:
                    # Update last-touched
                    COLLECTION.upsert(ids=[mem[2]], documents=[mem[1]], metadatas=[{'last-touched': str(now)}])

                    # add memory to return list
                    ret.append(mem[1])

            return ret
