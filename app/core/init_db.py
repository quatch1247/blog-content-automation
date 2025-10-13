from app.core.db import Base, engine
from app.models.pdf_models import RawPdf, SplitPost, RefinedPost

def init_db():
    Base.metadata.create_all(bind=engine)
