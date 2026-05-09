from fastapi import FastAPI, HTTPException

#own imports



app = FastAPI()

@app.get("/hello")
def hello():
    return "hello world"