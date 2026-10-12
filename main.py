from fastapi import FastAPI
from bs4 import BeautifulSoup
import requests

def fetch_page(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36 Edg/154.0.0.0"
                               }
        response = requests.get(url, timeout=10)
        response.encoding = 'utf-8'
        return response.text
    except Exception as e:
        return f"Error: {e}"

def parse_page(html):
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.string.strip()

    text = soup.get_text(separator="\n",strip=True)

    return {"title":title,"content":text[:500]}
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

@app.get("/test-parse")
async def parse():
    html = fetch_page("http://www.baidu.com")
    return parse_page(html)

