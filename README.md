# SimYou LLM Agent Microservice

## Introduction
Microservice for SimYou character dialouge. Utilizes OpenAI GPT 3 API.

## How to run

Create a `.env` file in the project directory. Add your OpenAI API key and the IP address of the Chroma DB as the following:

```
CHROMA_DB="1.23.45.678"
OPENAI_API_KEY="sk-EXAMPLE"
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
| PUT | /api/agents/ | Edit the attributes of an agent |
| DELETE | /api/agents/ | Delete an agent |
| POST | /api/agents/prompt | Prompt an agent |

