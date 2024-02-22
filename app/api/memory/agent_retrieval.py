import psycopg2
from ..models import AgentInfo
from .lru_cache import LRUCache

agent_info_cache = LRUCache(128)

async def get_agent_info(agentID, isUser, game_db_name, game_db_user, game_db_pass, game_db_url) -> AgentInfo:
    """
    This asynchronous function retrieves information about an agent from a PostgreSQL database.
    
    Parameters:
    agentID (str): The ID of the agent whose information needs to be retrieved.
    isUser (bool): A boolean value indicating whether the agent is a user or not.
    game_db_name (str): The name of the game database.
    game_db_user (str): The username for the game database.
    game_db_pass (str): The password for the game database.
    game_db_url (str): The URL of the game database.
    
    Returns:
    AgentInfo: An instance of the AgentInfo model containing the first name, last name, and description of the agent.
    """
    res = agent_info_cache.get(agentID)
    if res != -1:
        return res
    # Connect to the DB
    results = None
    conn = psycopg2.connect(
        dbname=game_db_name,
        user=game_db_user,
        password=game_db_pass,
        host=game_db_url
        )
    try:
        # Build and execute the query
        cursor = conn.cursor()      
        query = f"""
        SELECT \"FirstName\", \"LastName\", \"Description\"
        FROM \"{"Users" if isUser else "Agents"}\""
        WHERE \"UserId\" = \'{agentID}\'
        """
        cursor.execute(query)
        results = cursor.fetchall()[0]
        cursor.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print("no success", error)
    finally:
        if cursor:
            cursor.close()
        if results:
            LRUCache.put(agentID, AgentInfo(results[0], results[1], results[2]))
            return AgentInfo(results[0], results[1], results[2])
