from fastapi import FastAPI

import requests

def fetch_page(url):
    try:
        response = requests.get(url, timeout=10)
        response.encoding = 'utf-8'
        return response.text
    except Exception as e:
        return f"Error: {e}"

app = FastAPI()

@app.get("/test-fetch")
async def fetch():
    html = fetch_page("http://www.baidu.com")
    return {"length": len(html),"preview":html[:200]}


@app.get("/")
async def say_ok():
    return {"message": "ok"}
@app.get("/id")
async def say_id():
    return {"message": "first fastapi"}

