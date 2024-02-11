import psycopg2
from models import AgentInfo

# Helper method to get the info for an agent with id agentID
async def get_agent_info(agentID, game_db_name, game_db_user, game_db_pass, game_db_url) -> AgentInfo:
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
        SELECT \"FirstName\", \"LastName\", \"Description\"
        FROM \"Users\"
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
            return AgentInfo(results[0], results[1], results[2])
