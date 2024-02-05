from .models import AgentInfo
from typing import List

class Prompts:
    def get_convo_prompt(message: str, targetAgentInfo: AgentInfo, sourceAgentInfo: AgentInfo, targetAgentMemories: List[str]):
        """
        This function generates a conversation prompt for a GPT model using the given parameters.
        
        :param message: The message that the source agent says to the target agent.
        :param targetAgentInfo: An instance of AgentInfo class representing the target agent's information.
        :param sourceAgentInfo: An instance of AgentInfo class representing the source agent's information.
        :param targetAgentMemories: A list of the target agent's memories.
        :return: A string representing the generated conversation prompt.
        """
        
        # Concatenate the target agent's memories into a single string
        memories_str = ""
        for i in range(len(targetAgentMemories)):
            memories_str += f"({i+1}) {targetAgentMemories[i]};\n"
        
        # Create the GPT prompt
        gpt_prompt = f"""
        You are a character with the name {targetAgentInfo.firstName} {targetAgentInfo.lastName} this description:
        \'{targetAgentInfo.description}\'
        
        -----------------------------------------------------------------------------

        You have these memories:
        {memories_str}
        -----------------------------------------------------------------------------

        Another character with the name {sourceAgentInfo.firstName} {sourceAgentInfo.lastName} has this description:
        \'{sourceAgentInfo.description}\'

        -----------------------------------------------------------------------------

        {sourceAgentInfo.firstName} {sourceAgentInfo.lastName} says this to you:
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