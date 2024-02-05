from .models import AgentInfo
from typing import List

class Prompts:
    def get_convo_prompt(message: str, responderInfo: AgentInfo, askerInfo: AgentInfo, relevantMems: List[str], recentMems: List[(str, str)]):
        """
        This function generates a conversation prompt for a GPT model using the given parameters.
        
        :param message: The message that the source agent says to the target agent.
        :param targetAgentInfo: An instance of AgentInfo class representing the target agent's information.
        :param sourceAgentInfo: An instance of AgentInfo class representing the source agent's information.
        :param targetAgentMemories: A list of the target agent's memories.
        :return: A string representing the generated conversation prompt.
        """
        relevant_mems = ""
        for i in range(len(relevantMems)):
            relevant_mems += f"({i+1}) {relevantMems[i]};\n"
        

        #TODO: Assemble the recent memory from the list of chat summaries
        recent_mems = ""
        for i in range(len(recentMems)):
            relevant_mems += f"({relevantMems[i][0]} said: \"{relevantMems[i][1]}\";\n"
        
        # Create the GPT prompt
        gpt_prompt = f"""
        You are a character with the name {responderInfo.firstName} {responderInfo.lastName} this description:
        \'{responderInfo.description}\'
        
        -----------------------------------------------------------------------------

        You remember the following:
        {relevant_mems}
        -----------------------------------------------------------------------------

        You are talking to another character with the name {askerInfo.firstName} {askerInfo.lastName} who has this description:
        \'{askerInfo.description}\'

        -----------------------------------------------------------------------------
        
        This is what you have been talking about

        {recent_mems}

        ...

        {askerInfo.firstName} {askerInfo.lastName} says this to you:
        \"{message}\" 
        
        -----------------------------------------------------------------------------

        Please reply in a concise and conversational manner!

        You say to {sourceAgentInfo.firstName} {sourceAgentInfo.lastName}:
        """
        return gpt_prompt

    def get_world_thumbnail_prompt(worldDescription: str):
        """
        This function generates a thumbnail prompt for a DALL-E model using the given world description.
        
        :param worldDescription: A string representing the description of the world.
        :return: A string representing the generated thumbnail prompt.
        """
        
        dall_e_prompt = f"""
        Create a thumbnail image of a video game world described as: {worldDescription}
        """
        return dall_e_prompt