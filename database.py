from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker, declarative_base
import hashlib

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
