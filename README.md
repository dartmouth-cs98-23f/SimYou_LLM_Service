# SimYou LLM Agent Microservice

## Introduction
Microservice for SimYou character dialouge. Utilizes OpenAI GPT 3 API.

## How to run

If you haven't install virtualenv  

`$ pip install virtualenv`

Create the virtual environment  

`$ virtualenv env`

Activate the virtual environment  

`$ source ./env/bin/activate`

Install the requirements  

`$ pip install requirements.txt`

Run the service  

`$ uvicorn main:app --reload`

Create a .env file and set your OpenAI API key as follows:  

`OPENAI_API_KEY = "sk-EXAMPLEKEY"`

Note: If you get a ModuleNotFound error, it could be because your PYTHONPATH environment variable is not set. To set it, you can run the
below command in the base directory of the projcet:  

`$ export PYTHONPATH=$PWD`

## API Endpoints
| HTTP Verbs | Endpoints | Action |
| --- | --- | --- |
| POST | /api/agents/ | Create a new agent |
| PUT | /api/agents/ | Edit the attributes of an agent |
| DELETE | /api/agents/ | Delete an agent |
| POST | /api/agents/prompt | Prompt an agent |

