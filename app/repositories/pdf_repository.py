from datetime import datetime, time
from typing import List, Optional
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.models.pdf_models import RawPdf, SplitPost, RefinedPost


def create_raw_pdf(db: Session, filename: str, path: str) -> RawPdf:
    obj = RawPdf(filename=filename, path=path)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def create_split_post(db: Session, raw_pdf_id: int, filename: str, path: str) -> SplitPost:
    obj = SplitPost(raw_pdf_id=raw_pdf_id, filename=filename, path=path)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def create_refined_post(
    db: Session,
    split_post_id: int,
    json_path: str,
    images_dir: str,
    title: Optional[str],
    author: Optional[str],
    date: Optional[datetime],
    url: Optional[str],
    summary: Optional[str] = None,
    brief_summary: Optional[str] = None,
) -> RefinedPost:
    if date is not None and not isinstance(date, datetime):
        raise TypeError(f"Expected 'date' to be datetime or None, got {type(date)}")
    
    obj = RefinedPost(
        split_post_id=split_post_id,
        json_path=json_path,
        images_dir=images_dir,
        title=title,
        author=author,
        date=date,
        url=url,
        summary=summary,
        brief_summary=brief_summary,
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


def get_refined_post_basic_by_id(db: Session, post_id: int):
    post = db.query(RefinedPost).filter(RefinedPost.id == post_id).first()
    if not post:
        return None
    return {
        "id": post.id,
        "title": post.title,
        "author": post.author,
        "json_path": post.json_path,
    }


def truncate_raw_pdfs(db: Session):
    db.execute(text("TRUNCATE TABLE raw_pdfs RESTART IDENTITY CASCADE;"))
    db.commit()


def truncate_split_posts(db: Session):
    db.execute(text("TRUNCATE TABLE split_posts RESTART IDENTITY CASCADE;"))
    db.commit()


def truncate_refined_posts(db: Session):
    db.execute(text("TRUNCATE TABLE refined_posts RESTART IDENTITY CASCADE;"))
    db.commit()


def get_summary_markdown_by_post_id(db: Session, post_id: int) -> Optional[str]:
    post = db.query(RefinedPost).filter(RefinedPost.id == post_id).first()
    if not post or not post.summary:
        return None
    return post.summary


def get_brief_summaries_by_date_range(
    db: Session,
    start_date: datetime,
    end_date: datetime
) -> List[Optional[str]]:
    if isinstance(end_date, datetime):
        if end_date.time() == time(0, 0, 0):
            end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
    else:
        end_date = datetime.combine(end_date, time(23, 59, 59, 999999))

    results = (
        db.query(RefinedPost.brief_summary)
        .filter(
            RefinedPost.date >= start_date,
            RefinedPost.date <= end_date
        )
        .order_by(RefinedPost.date.asc())
        .all()
    )
    return [row[0] for row in results if row[0] is not None]