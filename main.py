from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def say_ok():
    return {"message": "ok"}
@app.get("/id")
async def say_id():
    return {"message": "first fastapi"}

