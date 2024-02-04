from .models import AgentInfo
from typing import List

class Prompts:
    def get_convo_prompt(message: str, responderInfo: AgentInfo, askerInfo: AgentInfo, relevantMems: List[str], recentMems: List[(str, str)]):
        relevant_mems = ""
        for i in range(len(relevantMems)):
            relevant_mems += f"({i+1}) {relevantMems[i]};\n"
        

        #TODO: Assemble the recent memory from the list of chat summaries
        recent_mems = ""
        for i in range(len(recentMems)):
            relevant_mems += f"({relevantMems[i][0]} said: \"{relevantMems[i][1]}\";\n"
        
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
        """
        return gpt_prompt