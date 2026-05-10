"""PDF processing utilities."""

from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional

import pdfplumber
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer


class PDF:
    """Utilities for reading, creating, merging, and splitting PDF files."""

    # ------------------------------------------------------------------
    # Reading
    # ------------------------------------------------------------------

    @staticmethod
    def extract_text(filepath: str, pages: Optional[List[int]] = None) -> str:
        """Extract text from a PDF file.

        Args:
            filepath: Path to the PDF file.
            pages:    Optional list of 0-based page indices to extract.
                      Defaults to all pages.

        Returns:
            Extracted text as a single string.
        """
        parts: List[str] = []
        with pdfplumber.open(filepath) as pdf:
            target_pages = (
                [pdf.pages[i] for i in pages] if pages else pdf.pages
            )
            for page in target_pages:
                text = page.extract_text() or ""
                parts.append(text)
        return "\n".join(parts)

    @staticmethod
    def get_page_count(filepath: str) -> int:
        """Return the total number of pages in a PDF.

        Args:
            filepath: Path to the PDF file.

        Returns:
            Number of pages.
        """
        with pdfplumber.open(filepath) as pdf:
            return len(pdf.pages)

    # ------------------------------------------------------------------
    # Writing / Generation
    # ------------------------------------------------------------------

    @staticmethod
    def create(
        filepath: str,
        content: str,
        title: Optional[str] = None,
        font_size: int = 12,
    ) -> str:
        """Create a PDF from plain text.

        Args:
            filepath:  Destination path for the .pdf file.
            content:   Body text (newlines are preserved as paragraph breaks).
            title:     Optional title rendered at the top.
            font_size: Body font size in points.

        Returns:
            Absolute path of the created file.
        """
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        doc = SimpleDocTemplate(str(filepath), pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        if title:
            story.append(Paragraph(title, styles["Title"]))
            story.append(Spacer(1, 12))

        body_style = styles["BodyText"]
        body_style.fontSize = font_size
        body_style.leading = font_size * 1.4

        for line in content.split("\n"):
            story.append(Paragraph(line or "&nbsp;", body_style))

        doc.build(story)
        return os.path.abspath(filepath)

    # ------------------------------------------------------------------
    # Merging / Splitting
    # ------------------------------------------------------------------

    @staticmethod
    def merge(input_files: List[str], output_path: str) -> str:
        """Merge multiple PDF files into one.

        Args:
            input_files: Ordered list of paths to source PDF files.
            output_path: Destination path for the merged PDF.

        Returns:
            Absolute path of the merged PDF.

        Raises:
            ImportError: If pypdf is not installed.
        """
        try:
            from pypdf import PdfWriter
        except ImportError as exc:
            raise ImportError(
                "pypdf is required for PDF merging. "
                "Install it with: pip install pypdf"
            ) from exc

        writer = PdfWriter()
        for path in input_files:
            writer.append(path)

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            writer.write(f)
        return os.path.abspath(output_path)

    @staticmethod
    def split(
        filepath: str,
        output_dir: Optional[str] = None,
        pages_per_file: int = 1,
    ) -> List[str]:
        """Split a PDF into smaller files.

        Args:
            filepath:       Path to the source PDF.
            output_dir:     Directory for output files. Defaults to the same
                            directory as *filepath*.
            pages_per_file: Number of pages per output file.

        Returns:
            List of absolute paths of the created files.

        Raises:
            ImportError: If pypdf is not installed.
        """
        try:
            from pypdf import PdfReader, PdfWriter
        except ImportError as exc:
            raise ImportError(
                "pypdf is required for PDF splitting. "
                "Install it with: pip install pypdf"
            ) from exc

        reader = PdfReader(filepath)
        total = len(reader.pages)
        stem = Path(filepath).stem
        out_dir = Path(output_dir) if output_dir else Path(filepath).parent
        out_dir.mkdir(parents=True, exist_ok=True)

        created: List[str] = []
        chunk = 0
        for start in range(0, total, pages_per_file):
            writer = PdfWriter()
            for page_idx in range(start, min(start + pages_per_file, total)):
                writer.add_page(reader.pages[page_idx])
            dest = out_dir / f"{stem}_part{chunk + 1}.pdf"
            with open(dest, "wb") as f:
                writer.write(f)
            created.append(os.path.abspath(str(dest)))
            chunk += 1

        return created
