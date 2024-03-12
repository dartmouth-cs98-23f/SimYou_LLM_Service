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

Create a `.env` file in the project directory. Add your OpenAI API key and the rest of the keys as the following:

```
CHROMA_DB="1.23.45.678"
OPENAI_API_KEY="sk-EXAMPLE"
GAME_DB_ADDRESS="blah-blah-blah.com"
GAME_DB_PASS="password"
GAME_DB_USER="user"
GAME_DB_NAME="simudb-prod"
AWS_ACCESS_KEY_ID="AKIA4MTWLE6QBV6GTJUG"
AWS_SECRET_ACCESS_KEY="p0kkAPUw7W/uWhl1SDPNKEH1dkIp9e9eDdmYAwg0"
```

If you haven't already, download [Docker](https://docs.docker.com/get-docker/)

Run
`docker-compose up -d --build`

Navigate to this [link](http://localhost:8000)

When finished, stop and remove the containers
`docker compose down`

