import io
import markdown
from weasyprint import HTML
from fastapi import HTTPException
from contextlib import closing
from app.repositories import pdf_repository
from app.core.db import get_db_session

class SummaryService:
    @staticmethod
    def generate_summary_pdf(post_id: int) -> dict:
        with closing(get_db_session()) as db:
            md_text = pdf_repository.get_summary_markdown_by_post_id(db, post_id)
            if not md_text:
                raise HTTPException(status_code=404, detail="요약문이 존재하지 않습니다.")

        html_body = markdown.markdown(md_text)
        html = f"""
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');
                body {{
                    font-family: 'Noto Sans KR', 'Pretendard', 'Apple SD Gothic Neo', sans-serif;
                    background: #fafbfc;
                    color: #20232a;
                    margin: 0;
                    padding: 0;
                }}
                .container {{
                    max-width: 720px;
                    background: #fff;
                    margin: 40px auto 60px auto;
                    padding: 40px 36px 36px 36px;
                    border-radius: 18px;
                    box-shadow: 0 6px 32px rgba(0,0,0,0.08), 0 1.5px 4px rgba(0,0,0,0.07);
                }}
                h1 {{
                    font-size: 2.1em;
                    font-weight: 700;
                    letter-spacing: -1px;
                    margin-bottom: 10px;
                    border-bottom: 2.5px solid #2276ff10;
                    color: #1562bf;
                    padding-bottom: 8px;
                }}
                h2 {{
                    font-size: 1.3em;
                    color: #1a56a5;
                    margin-top: 38px;
                    margin-bottom: 8px;
                    border-bottom: 1.5px solid #a8c9e0;
                    padding-bottom: 5px;
                    font-weight: 700;
                }}
                h3, h4 {{
                    color: #294366;
                    margin-top: 20px;
                }}
                p {{
                    font-size: 1.05em;
                    line-height: 1.8;
                    margin: 12px 0 10px 0;
                    color: #232629;
                }}
                ul, ol {{
                    font-size: 1em;
                    margin: 8px 0 14px 22px;
                    padding-left: 1.2em;
                }}
                li {{
                    margin-bottom: 8px;
                }}
                .notice {{
                    background: #fffbe0;
                    color: #6e591c;
                    border-left: 5px solid #f4e048;
                    border-radius: 8px;
                    padding: 12px 18px 12px 18px;
                    margin: 18px 0 18px 0;
                    font-size: 1.02em;
                }}
                .deadline {{
                    background: #e8f2ff;
                    border-left: 5px solid #6fa8ff;
                    padding: 10px 18px;
                    margin: 20px 0;
                    border-radius: 8px;
                    font-weight: 500;
                    color: #114277;
                }}
                code, pre {{
                    background: #f4f4f4;
                    border-radius: 5px;
                    padding: 4px 8px;
                    font-size: 1em;
                }}
                table {{
                    border-collapse: collapse;
                    margin: 18px 0;
                    width: 100%;
                }}
                th, td {{
                    border: 1px solid #e2e8f0;
                    padding: 8px 14px;
                    font-size: 1em;
                }}
                th {{
                    background: #f4f8fb;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                {html_body}
            </div>
        </body>
        </html>
        """

        try:
            pdf_bytes = HTML(string=html).write_pdf()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"PDF 생성 중 오류 발생: {str(e)}")

        filename = f"summary_{post_id}.pdf"
        return {
            "pdf_bytes": pdf_bytes,
            "filename": filename,
        }
