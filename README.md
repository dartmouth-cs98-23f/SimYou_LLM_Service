# SimYou AI Microservice

## Introduction
Microservice for SimYou generative AI. Utilizes OpenAI GPT and DALL-E to generate responses from characters and utilizes DALL-E
to generate images of characters and worlds.

## How Characters Work
### Generation
Users answer a series of questions about their character. These questions are compiled into a prompt which is used to prompt GPT to generate a summary of the character based on insights revealed by the survey. If the character is purely an AI, the user can also provide a summary of the sprite's description which we use to generate a sprite of the character.

### Personality
Prompts for AI character responses are built using three aspects:
1. Description of the character and the user that they are talking to
2. The converssation context -- the most recent conversation between the user and the character
3. The character's memory -- the most semantically similar memories to the current conversation stored in the character's memory

### Memory
Characters have a memory composed of summaries of past conversations. This is meant to simulate the character's ability to remember important details of past conversations and use them to inform future conversations. The memory is updated after every conversation and is used to inform the character's responses to future conversations.


## Repo Structure
### /api
Contains the FastAPI code for the microservice and all of the helper functionality for the endpoints.

### api/agents
Contains the endpoints that interact with agents. This includes the code for creating, updating, generating sprites, and prompting
agents in various ways.

### api/thumbnails
Contains the endpoint that generates thumbnails for worlds.

### api/prompts
Contains all prompts for interacting with the OpenAI API. This includes prompts for generating character descriptions, world
thumbnails, dialogue prompts, and more.

### api/helpers
Contains helper functions for API code. Mainly just a function that exponentionally backs off requests to the OpenAI API to
handle rate limiting.

### api/memory
Code that interfaces with the Chroma DB and game DB to store and retrieve character and world data.

### api/request_models
Contains Pydantic models for the request bodies of the API.

### api/response_models
Contains Pydantic models for the request bodies of the API.

## How to run

Create a `.env` file in the project directory. Add your OpenAI API key and the IP address of the Chroma DB as the following:

```
CHROMA_DB="1.23.45.678"
OPENAI_API_KEY="sk-EXAMPLE"
GAME_DB_ADDRESS="blah-blah-blah.com"
GAME_DB_PASS="password"
GAME_DB_USER="user"
```

If you haven't already, download [Docker](https://docs.docker.com/get-docker/)

Run
`docker-compose up -d --build`

Navigate to this [link](http://localhost:8000)

When finished, stop and remove the containers
`docker compose down`


## API Endpoints (not up to date)
| HTTP Verbs | Endpoints | Action |
| --- | --- | --- |
| POST | /api/agents/ | Create a new agent |
| DELETE | /api/agents/ | Delete an agent |
| POST | /api/agents/prompt | Prompt an agent |
| POST | /api/agents/question_agent | Prompt an agent to ask you a question |
| POST | /api/agents/endConservation | Notify agent that conversation is over so agent can summarize conversation and update their memory |
| POST | /api/agents/generate_agent | Given a list of survey questions and answers, generates an agent description |
| POST | /api/agents/generateAvatar | Generate a sprite that matches the description of an agent |
| POST | /api/agents/updateUserSummary | Update the user summary cache |
| POST | /api/thumbnails | Get a thumbnail for a given description |

