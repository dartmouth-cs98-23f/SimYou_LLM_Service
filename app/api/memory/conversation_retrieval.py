from typing import List
import psycopg2

async def get_recent_messages(game_db_name, game_db_user, game_db_pass, game_db_url, conversationID, num_popped = 10) -> List[str]:
    '''
    This function connects to a PostgreSQL database and retrieves the recent messages from a conversation.
    
    Parameters:
    game_db_name (str): The name of the database.
    game_db_user (str): The username to connect to the database.
    game_db_pass (str): The password to connect to the database.
    game_db_url (str): The url of the database.
    conversationID (str): The ID of the conversation to retrieve messages from.
    num_popped (int, optional): The number of recent messages to retrieve. Defaults to 10.

    Returns:
    List[str]: An ordered list of tuples, where each tuple contains a speaker and their message. 
               The first entry in the list is the least recent and the last entry is the most recent.
    '''
    # Need to account for scenario in which we want to get all the memories
    # Connect to DB
    results = None
    conn = psycopg2.connect(
        dbname=game_db_name,
        user=game_db_user,
        password=game_db_pass,
        host=game_db_url
        )
    try:
        # Build and execute query
        cursor = conn.cursor()
        query = ""
        if num_popped >= 0:
            query = f"""
            SELECT "Content", "SenderId", "RecipientId"
            FROM "Chats"
            WHERE "ConversationId" = '{conversationID}'
            ORDER BY "CreatedTime" DESC
            LIMIT {num_popped}
            """
        else:
            query = f"""
            SELECT "Content", "SenderId", "RecipientId"
            FROM "Chats"
            WHERE "ConversationId" = '{conversationID}'
            ORDER BY "CreatedTime" DESC
            """
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print("no success", error)
    finally:
        recent_messages = []
        if cursor:
            cursor.close()
        if results:
            for row in results:
                dictionary = dict(row)
                recent_messages.append((dictionary["SenderId"], dictionary["Content"]))
            return reversed(recent_messages)


def get_agent_perspective(convo_transcript, for_agent: str, other_agent_name: str) -> str:
    '''
    This function takes in a list of tuples, each containing a speaker and their message,
    and returns a string representing the conversation from the perspective of the agent
    specified by the for_agent parameter.

    Parameters:
    convo_transcript (List[Tuple[str, str]]): A list of tuples where each tuple contains a speaker ID and a message.
    for_agent (str): The ID of the agent for whom the perspective is to be generated.
    other_agent_name (str): The name of the other agent in the conversation.

    Returns:
    str: A string representing the conversation from the perspective of the specified agent.
    '''
    convo_str = ""
    for thing_said in convo_transcript:
        if thing_said[0] == for_agent:
            convo_str += f"You said: {thing_said[1]}\n"
        else:
            convo_str += f"{other_agent_name} said: \"{thing_said[1]}\"\n"


    return convo_str