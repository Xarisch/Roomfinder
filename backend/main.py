from fastapi import FastAPI, HTTPException

#own imports
from app.modules.router import router as Find_Router


app = FastAPI()


app.include_router(Find_Router)

@app.get("/hello")
def hello():
    return "hello world"