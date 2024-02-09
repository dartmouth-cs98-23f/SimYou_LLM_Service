from types import List

async def get_recent_messages(conversationID: str, responderID: str, num_popped = 10) -> List[str]:
    '''
    NOTE - ideally this function returns an ordered list of [(speaker, contents)]
    where the first entry in the list is the least recent and the last entry is the
    most recent, and where if speaker = person responding, then the speaker should
    be listed as "You"
    '''

    return ["fee", "fi", "fo", "fum"]