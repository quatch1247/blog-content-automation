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