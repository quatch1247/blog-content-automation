from sqlalchemy import Column, Integer, String, DateTime, Text
from app.core.db import Base
from datetime import datetime

class RawPdf(Base):
    __tablename__ = "raw_pdfs"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, index=True)
    path = Column(String)
    uploaded_at = Column(DateTime, default=datetime.utcnow)


class SplitPost(Base):
    __tablename__ = "split_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    path = Column(String)
    raw_pdf_id = Column(Integer)


class RefinedPost(Base):
    __tablename__ = "refined_posts"

    id = Column(Integer, primary_key=True, index=True)
    split_post_id = Column(Integer)
    json_path = Column(String)
    images_dir = Column(String)
    title = Column(String)
    author = Column(String)
    date = Column(DateTime)
    url = Column(String)
    summary = Column(Text)
    brief_summary = Column(Text)

