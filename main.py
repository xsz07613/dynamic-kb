from fastapi import FastAPI
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from pydantic import BaseModel
import requests
import hashlib
import re

# 数据库连接
engine = create_engine("sqlite:///./knowledge.db", echo=False)
Session = sessionmaker(bind=engine)
Base = declarative_base()

# Document 表（只定义一次）
class Document(Base):
    __tablename__ = "document"
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(500), unique=True, nullable=False)
    title = Column(String(500))
    content = Column(Text)
    content_hash = Column(String(64))

Base.metadata.create_all(engine)

# 请求体模型
class CrawlerRequest(BaseModel):
    url: str

# 存数据
def save_document(url, title, content):
    db = Session()
    try:
        new_hash = hashlib.md5(content.encode("utf-8")).hexdigest()
        existing = db.query(Document).filter(Document.url == url).first()

        if existing:
            if existing.content_hash == new_hash:
                return {"status": "exists", "id": existing.id}
            else:
                existing.title = title
                existing.content = content
                existing.content_hash = new_hash
                db.commit()                          # ← 必须提交
                return {"status": "updated", "id": existing.id}

        doc = Document(url=url, title=title, content=content, content_hash=new_hash)
        db.add(doc)
        db.commit()
        return {"status": "created", "id": doc.id}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        db.close()

# 抓网页
def fetch_page(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36 Edg/154.0.0.0"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        return response.text
    except Exception as e:
        return f"Error: {e}"

# 解析网页
def parse_page(html):
    soup = BeautifulSoup(html, "lxml")
    title = soup.title.string.strip() if soup.title and soup.title.string else "无标题"

    # 删掉 script 和 style 标签
    for tag in soup.find_all(["script", "style"]):
        tag.decompose()

    text = soup.get_text(separator="\n", strip=True)

    # 正则过滤残留的标签文本
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL)
    # 删掉纯CSS样式的行（如 body{color:#333} 这种）
    text = re.sub(r'[a-zA-Z0-9\s\.\#\-\_,:;\(\)]+\{[^{}]*\}', '', text)
    # 清掉多余空白
    text = re.sub(r'\n+', '\n', text).strip()

    return {"title": title, "content": text[:500]}

# FastAPI
app = FastAPI()

@app.get("/")
async def say_ok():
    return {"message": "ok"}

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
async def documents(skip: int = 0, limit: int = 100):
    db = Session()
    try:
        docs = db.query(Document).offset(skip).limit(limit).all()
        return {
            "total": db.query(Document).count(),
            "items": [
                {"id": d.id, "url": d.url, "title": d.title, "content": d.content}
                for d in docs
            ]
        }
    finally:
        db.close()