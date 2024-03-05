from .models import AgentInfo
from typing import List, Tuple

class Prompts:
        
    def get_convo_prompt(message: str, 
                         responderInfo: AgentInfo, 
                         askerInfo: AgentInfo, 
                         relevantMems: List[str], 
                         recentMems: List[Tuple[str, str]]):
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

        if recentMems:
            recent_mems = ""
            for i in range(len(recentMems)):
                recent_mems += f"({recentMems[i][0]} said: \"{recentMems[i][1]}\";\n"
                
            # Create the GPT prompt
            gpt_prompt = f"""
            You are a character with the name {responderInfo.username} and this description:
            \'{responderInfo.description}\'
                
            -----------------------------------------------------------------------------

            You are talking to another character with the name {askerInfo.username} who has this description:
            \'{askerInfo.description}\'

            -----------------------------------------------------------------------------

            You remember the following:
            {relevant_mems}
            -----------------------------------------------------------------------------
                
            This is what you have been talking about

            {recent_mems}

            ...

            {askerInfo.username} says this to you:
            \"{message}\" 
                
            -----------------------------------------------------------------------------

            Reply in a concise and conversational manner according to the context of the conversation
            and the description of your character.
            You say to {askerInfo.username}:
            """
            return gpt_prompt
        
        else:
            gpt_prompt = f"""
            You are a character with the name {responderInfo.username} and this description:
            \'{responderInfo.description}\'
                
            -----------------------------------------------------------------------------

            You remember the following:
            {relevant_mems}
            -----------------------------------------------------------------------------

            You are talking to another character with the name {askerInfo.username} who has this description:
            \'{askerInfo.description}\'

            -----------------------------------------------------------------------------

            {askerInfo.username} says this to you:
            \"{message}\" 
                
            -----------------------------------------------------------------------------

            Reply in a concise and conversational manner according to the context of the conversation
            and the description of your character.

            You say to {askerInfo.username}:
            """
            return gpt_prompt

        
    def get_chat_completion_system_prompt(responderInfo: AgentInfo, askerInfo: AgentInfo, relevantMems: List[str]):
        relevant_mems = ""
        for i in range(len(relevantMems)):
            relevant_mems += f"({i+1}) {relevantMems[i]};\n"

        system_prompt = f"""
            You are a character with the name {responderInfo.username} and this description:
            \'{responderInfo.description}\'
                
            -----------------------------------------------------------------------------

            You are talking to another character with the name {askerInfo.username} who has this description:
            \'{askerInfo.description}\'

            -----------------------------------------------------------------------------

            You remember the following:
            {relevant_mems}

            -----------------------------------------------------------------------------

            Reply in a concise and conversational manner according to the context of the conversation
            and the description of your character.

            You say to {askerInfo.username}:
            """
        
        return system_prompt


    def get_world_thumbnail_prompt(worldDescription: str):
        """
        This function generates a thumbnail prompt for a DALL-E model using the given world description.
        
        :param worldDescription: A string representing the description of the world.
        :return: A string representing the generated thumbnail prompt.
        """
        
        dall_e_prompt = f"""
        Generate a LIGHT-COLORED, SIMPLE, highly PIXELATED, RETRO-style thumbnail that looks like a planet for the world with the following description: 
        {worldDescription}
        """
        return dall_e_prompt
    
    def get_agent_persona_prompt(name: str, questions: List[str], answers: List[List[str]]):
        """
        This function generates a persona prompt for an AI model using the given questions and answers.
        
        :param questions: A list of strings representing the questions about the character's persona.
        :param answers: A list of strings representing the answers to the questions about the character's persona.
        :return: A string representing the generated persona prompt.
        """
        # Check if the lengths of questions and answers are equal
        if len(questions) != len(answers):
            raise ValueError("The number of questions should match with the number of answers.")

        # Initialize the prompt string
        prompt = f"""
        You are an expert at synthesizing details about a characters into detailed descriptions. 
        A character named {name} filled out the following survey to answer questions about themself:\n"""

        # Iterate over the questions and answers
        for question, answer_list in zip(questions, answers):
            # Add the question and answer to the prompt
            for answer in answer_list:
                prompt += f"\"{question}\": \"{answer}\"\n"

        # Add the instruction to generate more details
        prompt += "\nBased on the above information, generate a concise and cohesive summary for {name}:"

        return prompt
    
    def get_question_prompt(responderInfo: AgentInfo, 
                            askerInfo: AgentInfo, 
                            relevantMems: List[str], 
                            recentMems: List[Tuple[str, str]]):
        """
        This function generates a question prompt for an AI model using the given responder and asker agent information.
        Generates a question prompt for an AI model using given responder and asker agent information, and optionally, 
        relevant and recent memories. The generated prompt includes details about the responder and asker agents, 
        their recent conversation, and a request for the AI to generate a question that the responder would ask the asker.
        
        :param responderInfo: An instance of AgentInfo class representing the responder agent's information.
        :param askerInfo: An instance of AgentInfo class representing the asker agent's information.
        :param relevantMems: A list of relevant memories (optional).
        :param recentMems: A list of recent memories (optional).
        :return: A string representing the generated question prompt.
        """
        relevant_mems = ""
        if relevant_mems:
            for i in range(len(relevantMems)):
                relevant_mems += f"({i+1}) {relevantMems[i]};\n"
        
        recent_mems = ""
        if recentMems:
            for i in range(len(recentMems)):
                recent_mems += f"({recentMems[i][0]} said: \"{recentMems[i][1]}\";\n"
        
            # Create the GPT prompt
            gpt_prompt = f"""
            You are a character with the name {responderInfo.username} and this description:
            \'{responderInfo.description}\'

            -----------------------------------------------------------------------------

            You are talking to another character with the name {askerInfo.username} who has this description:
            \'{askerInfo.description}\'

            -----------------------------------------------------------------------------

            You remember the following:
            {relevant_mems}
            
            -----------------------------------------------------------------------------
            
            This is what you have been talking about
            {recent_mems}

            -----------------------------------------------------------------------------

            Based on your understanding of {askerInfo.username} and your own interests, propose a question 
            brings up a new subject and will lead to an interesting conversation.
            
            You ask {askerInfo.username}:
            """
            return gpt_prompt
        
        else:
            gpt_prompt = f"""
            You are a character with the name {responderInfo.username} with this description:
            \'{responderInfo.description}\'

            -----------------------------------------------------------------------------
            
            You remember the following:
            {relevant_mems}
            
            -----------------------------------------------------------------------------

            You are talking to another character with the name {askerInfo.username} who has this description:
            \'{askerInfo.description}\'

            -----------------------------------------------------------------------------

            Based on your understanding of {askerInfo.username} and your own interests, propose a question 
            brings up a new subject and will lead to an interesting conversation.
            
            You ask {askerInfo.username}:
            """
            return gpt_prompt
        
    def get_question_system_prompt(responderInfo: AgentInfo, 
                            askerInfo: AgentInfo, 
                            relevantMems: List[str]):
        """
        This function generates a question prompt for an AI model using the given responder and asker agent information.
        Generates a question prompt for an AI model using given responder and asker agent information, and optionally, 
        relevant and recent memories. The generated prompt includes details about the responder and asker agents, 
        their recent conversation, and a request for the AI to generate a question that the responder would ask the asker.
        
        :param responderInfo: An instance of AgentInfo class representing the responder agent's information.
        :param askerInfo: An instance of AgentInfo class representing the asker agent's information.
        :param relevantMems: A list of relevant memories (optional).
        :return: A string representing the generated question prompt.
        """
        relevant_mems = ""
        if relevant_mems:
            for i in range(len(relevantMems)):
                relevant_mems += f"({i+1}) {relevantMems[i]};\n"
            
        system_prompt = f"""
        You are a character with the name {responderInfo.username} and this description:
        \'{responderInfo.description}\'

        -----------------------------------------------------------------------------
            
        You remember the following:
        {relevant_mems}
            
        -----------------------------------------------------------------------------

        You are talking to another character with the name {askerInfo.username} who has this description:
        \'{askerInfo.description}\'

        -----------------------------------------------------------------------------

        Based on your understanding of {askerInfo.username} and your own interests, propose a question 
        brings up a new subject and will lead to an interesting conversation.
            
        You ask {askerInfo.username}:
        """
        return system_prompt

    
    def get_convo_summary_prompt(convo_transcript:str, responder:AgentInfo, otherAgent:AgentInfo) -> str:
        """
        This function generates a conversation summary prompt for an AI model.
        
        :return: A string representing the generated conversation summary prompt.
        """
        # Create the GPT prompt
        gpt_prompt = f"""
        You are a character with the name {responder.username} with this description:
        \'{responder.description}\'
        
        -----------------------------------------------------------------------------

        Based on the conversation between you and {otherAgent.username}, generate a summary of the conversation.

        The conversation is as follows:

        {convo_transcript}
        """
        return gpt_prompt
    
    def get_avatar_prompt(appearanceDescription: str):
        dall_e_prompt = f"""
        Create an image of a character that looks as follows: {appearanceDescription}

        Pixelate the details to give the character a classic feel. The character should be front-facing and standing in a wide stance,
        
        Make sure that the background is a solid color that can be easily removed.
        
        Make sure there is space between the character and the edges of the image.
        
        The image inlude only ONE intance of the character CENTERED in the image, and it should show the entire body.
        """
        return dall_e_prompt
    
    def combine_chats_and_system_prompt(system_prompt, 
                                      convo_transcript, 
                                      for_agent: str, 
                                      for_agent_name: str,
                                      other_agent_name: str) -> str:
        '''
        This function takes in a list of tuples, each containing a speaker and their message,
        and returns a string representing the conversation from the perspective of the agent
        specified by the for_agent parameter.

        Parameters:
        convo_transcript (List[Tuple[str, str]]): A list of tuples where each tuple contains a speaker ID and a message.
        for_agent (str): The ID of the agent for whom the perspective is to be generated.
        other_agent_name (str): The name of the other agent in the conversation.

        Returns:
        A list of dictionaries, where each dictionary contains the role of the speaker and their message. Prompt returned
        is ready to be fed to chatgpt.
        '''

        convo = []
        convo.append({"role": "system", "content": system_prompt})
        for thing_said in convo_transcript:
            if thing_said[0] == for_agent:
                convo.append({"role": "agent", "name": for_agent_name, "content": thing_said[1]})
            else:
                convo.append({"role": "user", "name": other_agent_name, "content": thing_said[1]})

        return convo