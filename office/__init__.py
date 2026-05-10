"""
python-office: A powerful open-source Python toolkit for everyday office automation.

Modules:
    word    — Word document processing (create, read, convert)
    excel   — Excel spreadsheet processing (read, write, convert)
    pdf     — PDF processing (extract text, merge, split)
    image   — Image processing (watermark, resize, convert)
    network — Network tools (QR code generation, web scraping)
    file    — File automation (batch rename, directory listing)
    email   — Email sending (single message and batch)
"""

from office.word import Word
from office.excel import Excel
from office.pdf import PDF
from office.image import Image
from office.network import Network
from office.file import File
from office.email_utils import Email

__version__ = "0.1.0"
__all__ = ["Word", "Excel", "PDF", "Image", "Network", "File", "Email"]
