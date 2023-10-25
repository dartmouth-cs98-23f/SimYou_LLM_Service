# SimYou LLM Agent Microservice

## Introduction
Microservice for SimYou character dialouge. Utilizes OpenAI GPT 3 API.

## How to run

If you haven't already, download [Docker](https://docs.docker.com/get-docker/)

Build the docker image

`$ docker build -t myimage .`

Start the docker container

`$ docker run -d --name mycontainer -p 80:80 myimage`


## API Endpoints
| HTTP Verbs | Endpoints | Action |
| --- | --- | --- |
| POST | /api/agents/ | Create a new agent |
| PUT | /api/agents/ | Edit the attributes of an agent |
| DELETE | /api/agents/ | Delete an agent |
| POST | /api/agents/prompt | Prompt an agent |

