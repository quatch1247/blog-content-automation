from typing import List
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.pdf_models import RawPdf, SplitPost, RefinedPost


def create_raw_pdf(db: Session, filename: str, path: str) -> RawPdf:
    obj = RawPdf(filename=filename, path=path)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def create_split_post(db: Session, raw_pdf_id: int, filename: str, path: str) -> SplitPost:
    obj = SplitPost(
        raw_pdf_id=raw_pdf_id,
        filename=filename,
        path=path,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def create_refined_post(
    db: Session,
    split_post_id: int,
    json_path: str,
    images_dir: str,
    title: str,
    author: str,
    date: datetime,
    url: str
) -> RefinedPost:
    if not isinstance(date, datetime):
        raise TypeError(f"Expected 'date' to be datetime, got {type(date)}")

    obj = RefinedPost(
        split_post_id=split_post_id,
        json_path=json_path,
        images_dir=images_dir,
        title=title,
        author=author,
        date=date,
        url=url,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get_raw_pdf_count(db: Session) -> int:
    return db.query(RawPdf).count()


def get_all_refined_posts(db: Session) -> List[RefinedPost]:
    return db.query(RefinedPost).order_by(RefinedPost.id.desc()).all()


def get_refined_post_count(db: Session) -> int:
    return db.query(RefinedPost).count()


def get_refined_post_basic_by_id(db, post_id: int):
    post = db.query(RefinedPost).filter(RefinedPost.id == post_id).first()
    if not post:
        return None
    return {
        "id": post.id,
        "title": post.title,
        "author": post.author,
        "json_path": post.json_path
    }


def get_refined_post_basic_by_id(db, post_id: int):
    post = db.query(RefinedPost).filter(RefinedPost.id == post_id).first()
    if not post:
        return None
    return {
        "id": post.id,
        "title": post.title,
        "author": post.author,
        "json_path": post.json_path
    }
