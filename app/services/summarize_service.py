import io
import markdown
from weasyprint import HTML
from fastapi import HTTPException
from app.repositories import pdf_repository
from app.core.db import get_db_session

class SummaryService:
    @staticmethod
    def generate_summary_pdf(post_id: int) -> dict:
        db = get_db_session()
        try:
            md_text = pdf_repository.get_summary_markdown_by_post_id(db, post_id)
            if not md_text:
                raise HTTPException(status_code=404, detail="요약문이 존재하지 않습니다.")
        finally:
            db.close()

        html_body = markdown.markdown(md_text)
        html = f"<html><body>{html_body}</body></html>"

        pdf_bytes = HTML(string=html).write_pdf()
        filename = f"post_{post_id}_summary.pdf"

        return {"pdf_bytes": pdf_bytes, "filename": filename}
