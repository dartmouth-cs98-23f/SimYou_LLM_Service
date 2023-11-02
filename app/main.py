from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.agents import agents

app = FastAPI()
app.include_router(agents)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
