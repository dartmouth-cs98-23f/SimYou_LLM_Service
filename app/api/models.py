import pydantic
from typing import List


# Agent info object
class AgentInfo:
    firstName: str
    lastName: str
    description: str

    def __init__(self, firstName, lastName, description):
        self.firstName = firstName
        self.lastName = lastName
        self.description = description



