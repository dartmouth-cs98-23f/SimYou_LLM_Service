from typing import List
import psycopg2

async def get_recent_messages(game_db_name, game_db_user, game_db_pass, game_db_url, conversationID, num_popped = 10) -> List[str]:
    '''
    NOTE - ideally this function returns an ordered list of [(speaker, contents)]
    where the first entry in the list is the least recent and the last entry is the
    most recent. The list should contain num_popped entries.
    '''
    # Need to account for scenario in which we want to get all the memories
    # db connection string
    results = None
    conn = psycopg2.connect(
        dbname=game_db_name,
        user=game_db_user,
        password=game_db_pass,
        host=game_db_url
        )
    try:
        cursor = conn.cursor()      
        query = f"""
        SELECT "Content", "SenderId", "RecipientId"
        FROM "Chats"
        WHERE "ConversationId" = '{conversationID}'
        ORDER BY "CreatedTime\" DESC
        {"LIMIT '{num_popped}'" if (num_popped >= 0) else ""}
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

    convo_transcript = [(speakerID, message), (speakerID, message), ...]
    '''
    convo_str = ""
    for thing_said in convo_transcript:
        if thing_said[0] == for_agent:
            convo_str += f"You said: {thing_said[1]}\n"
        else:
            convo_str += f"{other_agent_name} said: \"{thing_said[1]}\"\n"


    return convo_str