from http import client
import chromadb
import heapq
import datetime
import random


class ChromaClientWrapper:

    def __init__(self, client: chromadb.Client):
        self.client = client

    def dateTime_str_to_time(self, str):
        date, time = str.split(" ")
        year, month, day = date.split("-")
        hour, minute, seconds = time.split(":")
        second, ms = seconds.split(".")
        return datetime.datetime(int(year), int(month), int(day), int(hour), int(minute), int(second), int(ms))


    async def add_memory(self, agent_id: str, memory: str, unique_id=""):
        '''
        Adds a memory to the collection belonging to the agent
        NOTE: might need to maintain another database to handle the memory IDs
        '''
        
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
            #TODO: Figure out a better way to handle this
            return

        

    def add_agent(self, agent_id: str):
        '''
        Initializes a collection in the client corresponding to the agent_id
        Note -- eventually we might expand this implementation to include a core memory / stable traits
        '''
        self.client.get_or_create_collection(agent_id)
    
    def delete_agent(self, agent_id: str):
        # Raises ValueError if the collection does not exist -- handle this so the operation 
        # fails gracefully

        try:
            self.client.delete_collection(agent_id)
        except ValueError as e:
            #TODO: figure out a better way to handle this
            return


    async def retrieve_relevant_memories(self, agent_id: str, prompt: str, k=10, mem_boost_seconds_threshold=600, cutoff=1.50):
        '''
        Input: chroma client, agent_id, prompt, and k (how many memories you want to retrieve)
        Ouput: <= k most relevant memories
        '''

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
                last_touched_str = metadata['last-touched']
                last_touched = self.dateTime_str_to_time(last_touched_str)
                time_elapsed = now - last_touched

                if time_elapsed.seconds <= mem_boost_seconds_threshold:
                    distance *= .80

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
            

    

    # def summarizeCollection(self, collection_id: str, destination_id: str):
    #     '''
    #     Given a chroma client and a collection ID, summarizes all memories in the collection belonging
    #     to collection_id and puts summary in destination_id
    #     NOTE: Don't need for MVP
    #     '''
    #     collection = self.client.get_collection(collection_id)
    #     mems = collection.get()['documents']
    #     chunk = []
    #     for mem in mems:
    #         chunk.append(mem)
            
    #         if len(chunk) == 10:
    #             summary = prompt_gpt_for_summary(chunk, destination_id)

    #             chunk = []
        
    #     if chunk:
    #         prompt_gpt_for_summary(chunk, destination_id)
    #     client.delete_collection(collection_id)
    #     client.create_collection(collection_id)



    # def prompt_gpt_for_summary(self, text_list, summary_dest):
    #     '''
    #     Given a list of strings, prompt GPT to summarize the list into higher-level reflections
    #     NOTE: Don't need for MVP
    #     '''

    #     pass
        