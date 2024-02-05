from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.agents import agents
from .api.thumbnails import thumbnails

app = FastAPI()
app.include_router(agents)
app.include_router(thumbnails)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)