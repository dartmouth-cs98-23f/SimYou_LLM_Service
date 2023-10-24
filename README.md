# SimYou_LLM_Service

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
