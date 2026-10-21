from langchain_classic.chains.natbot.crawler import Crawler

from scheduler import crawl_onw,scheduler
from fastapi import FastAPI
from crawl import parse_page,fetch_page
from database import save_document,Session,Document
from pydantic import BaseModel
from apscheduler.schedulers.background import BackgroundScheduler

# 请求体模型
class CrawlerRequest(BaseModel):
    url: str

class BatchCrawlerRequest(BaseModel):
    urls: list[str]

# FastAPI
app = FastAPI()

@app.on_event("startup")
def start_scheduler():
    scheduler.add_job(crawl_onw,'interval',minutes=10,id = "crawl_onw",max_instances=1)
    scheduler.start()

@app.get("/test-fetch")
async def test_fetch():
    html = fetch_page("http://www.baidu.com")
    return {"length": len(html), "preview": html[:200]}

@app.get("/test-parse")
async def test_parse():
    html = fetch_page("http://www.baidu.com")
    return parse_page(html)

@app.get("/test-save")
def test_save():
    html = fetch_page("http://www.baidu.com")
    parsed = parse_page(html)
    return save_document("http://www.baidu.com", parsed["title"], parsed["content"])

@app.post("/crawl")
async def crawl(req: CrawlerRequest):
    html = fetch_page(req.url)
    if html.startswith("Error"):
        return {"status": "error", "message": html}
    parsed = parse_page(html)
    return save_document(req.url, parsed["title"], parsed["content"])

@app.get("/documents")
async def documents(skip: int = 0, limit: int = 100,order: str = "desc"):
    db = Session()
    try:
        query = db.query(Document)
        if order == "desc":
            query = query.order_by(Document.id.desc())
        else:
            query = query.order_by(Document.id.asc())

        docs = query.offset(skip).limit(limit).all()
        return {
            "total": db.query(Document).count(),
            "items": [
                {"id": d.id, "url": d.url, "title": d.title, "content": d.content}
                for d in docs
            ]
        }
    finally:
        db.close()

@app.get("/search")
async def search(keyword: str, skip: int = 0, limit: int = 100):
    db = Session()
    try:
        query = db.query(Document).filter(Document.title.like(f"%{keyword}%"))

        total = query.count()
        docs = query.offset(skip).limit(limit).all()

        return {
            "keyword": keyword,
            "total": total,
            "items": [
                {"id": d.id, "url": d.url, "title": d.title}

            for d in docs
            ]

        }
    finally:
        db.close()

@app.post("/crawl/batch")
async def crawl_batch(req: BatchCrawlerRequest):
    results = []
    for url in req.urls:
        html = fetch_page(url)

        if html.startswith("Error"):
            results.append({"url":url,"status": "error", "message": html})
            continue

        parsed = parse_page(html)

        save_res = save_document(url, parsed["title"], parsed["content"])

        results.append({"url": url, "result": save_res})

    return {"total": len(results), "details": results}




