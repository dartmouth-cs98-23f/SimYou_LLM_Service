from .models import AgentInfo
from typing import List

class Prompts:
    def get_convo_prompt(message: str, targetAgentInfo: AgentInfo, sourceAgentInfo: AgentInfo, targetAgentMemories: List[str]):
        memories_str = ""
        for i in range(len(targetAgentMemories)):
            memories_str += f"({i+1}) {targetAgentMemories[i]};\n"
        
        gpt_prompt = f"""
        You are a character named {targetAgentInfo.firstName} {targetAgentInfo.lastName} with this description:
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
        """
        return gpt_prompt