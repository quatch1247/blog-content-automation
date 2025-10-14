from datetime import datetime
import markdown
from weasyprint import HTML
from fastapi import HTTPException
from contextlib import closing

from app.core.db import get_db_session
from app.repositories import pdf_repository
from app.utils.weekly_report_utils import generate_weekly_insight_report_markdown

class WeeklyReportService:
    @staticmethod
    def generate_weekly_report(start_date, end_date) -> dict:
        with closing(get_db_session()) as db:
            brief_summaries = pdf_repository.get_brief_summaries_by_date_range(db, start_date, end_date)
            if not brief_summaries:
                raise HTTPException(status_code=404, detail="리포트에 포함할 요약문이 없습니다.")

        md_text = generate_weekly_insight_report_markdown(
            brief_summaries=brief_summaries,
            start_date=start_date,
            end_date=end_date,
        )

        html_body = markdown.markdown(md_text, extensions=['tables', 'fenced_code'])

        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')
        year = datetime.now().year

        if start_str == end_str:
            date_range_str = f"{start_str}"
        else:
            date_range_str = f"{start_str} ~ {end_str}"

        report_desc = f"{date_range_str} 인사이트 리포트 자동 생성"
        
        html = f"""
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');
                body {{
                    font-family: 'Noto Sans KR', 'Pretendard', 'Apple SD Gothic Neo', sans-serif;
                    background: #f4f8fa;
                    color: #222;
                    margin: 0;
                    padding: 0;
                }}
                .report-wrapper {{
                    max-width: 800px;
                    background: #fff;
                    margin: 48px auto 60px auto;
                    padding: 52px 44px 48px 44px;
                    border-radius: 22px;
                    box-shadow: 0 8px 32px rgba(20, 50, 100, 0.10), 0 2px 8px rgba(0,0,0,0.07);
                }}
                .report-title {{
                    display: flex;
                    align-items: center;
                    font-size: 2.1em;
                    font-weight: 800;
                    color: #205baf;
                    margin-bottom: 10px;
                    letter-spacing: -1px;
                }}
                .report-desc {{
                    font-size: 1.17em;
                    color: #2b4572;
                    margin-bottom: 28px;
                    font-weight: 500;
                }}
                h1, h2, h3, h4 {{
                    font-family: 'Noto Sans KR', 'Pretendard', 'Apple SD Gothic Neo', sans-serif;
                    margin-top: 28px;
                    margin-bottom: 14px;
                    line-height: 1.22;
                }}
                h1 {{
                    font-size: 1.6em;
                    font-weight: 800;
                    border-bottom: 3px solid #1562bf30;
                    color: #195b94;
                    padding-bottom: 9px;
                    margin-bottom: 22px;
                }}
                h2 {{
                    font-size: 1.17em;
                    color: #236dbb;
                    font-weight: 700;
                    border-bottom: 2px solid #dde8f7;
                    padding-bottom: 5px;
                }}
                h3, h4 {{
                    color: #295c8f;
                    font-size: 1.08em;
                }}
                p, ul, ol {{
                    font-size: 1.09em;
                    line-height: 1.8;
                    margin: 12px 0 10px 0;
                }}
                ul, ol {{
                    margin-left: 1.5em;
                }}
                li {{
                    margin-bottom: 8px;
                }}
                blockquote {{
                    background: #f4f8fb;
                    border-left: 5px solid #4b93ff;
                    margin: 18px 0;
                    padding: 15px 25px;
                    border-radius: 9px;
                    color: #284775;
                    font-style: italic;
                }}
                table {{
                    border-collapse: collapse;
                    margin: 22px 0;
                    width: 100%;
                    font-size: 1em;
                }}
                th, td {{
                    border: 1.7px solid #d3e0ef;
                    padding: 9px 14px;
                    text-align: left;
                }}
                th {{
                    background: #e3eefb;
                    font-weight: 700;
                    color: #1a4d8f;
                }}
                code, pre {{
                    background: #f7f7f7;
                    border-radius: 5px;
                    padding: 4px 10px;
                    font-size: 0.97em;
                    color: #195b94;
                }}
                .report-footer {{
                    margin-top: 44px;
                    color: #999;
                    font-size: 0.97em;
                    text-align: right;
                }}
            </style>
        </head>
        <body>
            <div class="report-wrapper">
                <div class="report-title"> 콘텐츠 큐레이션 리포트</div>
                <div class="report-desc">{report_desc}</div>
                {html_body}
                <div class="report-footer">© {year} GUN. All rights reserved.</div>
            </div>
        </body>
        </html>
        """

        try:
            pdf_bytes = HTML(string=html).write_pdf()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"PDF 생성 중 오류 발생: {str(e)}")

        filename = f"weekly_report_{start_date}_{end_date}.pdf"
        return {
            "pdf_bytes": pdf_bytes,
            "filename": filename,
            "markdown": md_text,
        }
