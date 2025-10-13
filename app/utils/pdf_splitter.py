import os
from typing import List
from PyPDF2 import PdfReader, PdfWriter
from app.schemas.upload import SplitFileInfo


def split_pdf_by_ranges(pdf_path: str, output_dir: str, post_ranges: List[tuple[str, int, int]]) -> List[SplitFileInfo]:
    reader = PdfReader(pdf_path)
    os.makedirs(output_dir, exist_ok=True)

    split_file_infos: List[SplitFileInfo] = []

    for post_id, start, end in post_ranges:
        writer = PdfWriter()
        for i in range(start - 1, end):
            writer.add_page(reader.pages[i])

        short_id = post_id.split("/")[-1][-7:]
        filename = f"{start:03d}-{end:03d}_{short_id}.pdf"
        output_path = os.path.join(output_dir, filename)

        with open(output_path, "wb") as f_out:
            writer.write(f_out)

        split_file_infos.append(
            SplitFileInfo(
                post_id=post_id,
                range=f"{start}-{end}",
                file=output_path
            )
        )

    return split_file_infos
