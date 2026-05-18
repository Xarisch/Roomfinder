from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

#own imports
from app.modules.router import router as Find_Router


app = FastAPI()


origins= [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(Find_Router)

@app.get("/hello")
def hello():
    return "hello world"