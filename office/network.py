"""Network tools: QR code generation and basic web-content scraping."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse

import qrcode
from qrcode.image.styledpil import StyledPilImage
import requests
from bs4 import BeautifulSoup


class Network:
    """QR code generation and web-content scraping utilities."""

    # ------------------------------------------------------------------
    # QR code
    # ------------------------------------------------------------------

    @staticmethod
    def generate_qrcode(
        data: str,
        output_path: str = "qrcode.png",
        box_size: int = 10,
        border: int = 4,
        fill_color: str = "black",
        back_color: str = "white",
    ) -> str:
        """Generate a QR code image from a string.

        Args:
            data:        The text / URL to encode.
            output_path: Destination path for the PNG image.
            box_size:    Pixel size of each QR module box.
            border:      Width of the quiet-zone border in modules.
            fill_color:  Foreground colour (CSS name or hex string).
            back_color:  Background colour.

        Returns:
            Absolute path of the generated QR image.
        """
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=box_size,
            border=border,
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color=fill_color, back_color=back_color)
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        img.save(output_path)
        return os.path.abspath(output_path)

    # ------------------------------------------------------------------
    # Web scraping
    # ------------------------------------------------------------------

    @staticmethod
    def fetch_page(
        url: str,
        timeout: int = 10,
        headers: Optional[Dict[str, str]] = None,
    ) -> str:
        """Fetch a web page and return its raw HTML.

        Args:
            url:     Target URL.
            timeout: HTTP request timeout in seconds.
            headers: Optional dict of extra HTTP headers.

        Returns:
            Raw HTML string.

        Raises:
            requests.HTTPError: On non-2xx HTTP responses.
        """
        default_headers = {
            "User-Agent": (
                "Mozilla/5.0 (compatible; python-office/0.1; "
                "+https://github.com/aoshen01/python-office)"
            )
        }
        if headers:
            default_headers.update(headers)
        resp = requests.get(url, timeout=timeout, headers=default_headers)
        resp.raise_for_status()
        return resp.text

    @staticmethod
    def extract_text_from_url(
        url: str,
        timeout: int = 10,
        headers: Optional[Dict[str, str]] = None,
    ) -> str:
        """Fetch a web page and return its visible text content.

        Args:
            url:     Target URL.
            timeout: HTTP request timeout in seconds.
            headers: Optional dict of extra HTTP headers.

        Returns:
            Visible plain-text content of the page.
        """
        html = Network.fetch_page(url, timeout=timeout, headers=headers)
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        return soup.get_text(separator="\n", strip=True)

    @staticmethod
    def extract_links(
        url: str,
        timeout: int = 10,
        headers: Optional[Dict[str, str]] = None,
        same_domain_only: bool = False,
    ) -> List[str]:
        """Extract all hyperlinks from a web page.

        Args:
            url:              Target URL.
            timeout:          HTTP request timeout in seconds.
            headers:          Optional dict of extra HTTP headers.
            same_domain_only: If True, return only links on the same domain.

        Returns:
            List of absolute URL strings.
        """
        html = Network.fetch_page(url, timeout=timeout, headers=headers)
        soup = BeautifulSoup(html, "html.parser")
        base_domain = urlparse(url).netloc
        links: List[str] = []

        for tag in soup.find_all("a", href=True):
            href = tag["href"]
            absolute = urljoin(url, href)
            if same_domain_only and urlparse(absolute).netloc != base_domain:
                continue
            links.append(absolute)

        return links

    @staticmethod
    def scrape_table(
        url: str,
        table_index: int = 0,
        timeout: int = 10,
        headers: Optional[Dict[str, str]] = None,
    ) -> List[List[str]]:
        """Scrape an HTML table and return its data as a 2-D list.

        Args:
            url:         Target URL.
            table_index: 0-based index of the table on the page.
            timeout:     HTTP request timeout in seconds.
            headers:     Optional dict of extra HTTP headers.

        Returns:
            2-D list of string cell values.

        Raises:
            IndexError: If fewer tables than *table_index* exist on the page.
        """
        html = Network.fetch_page(url, timeout=timeout, headers=headers)
        soup = BeautifulSoup(html, "html.parser")
        tables = soup.find_all("table")
        table = tables[table_index]
        rows: List[List[str]] = []
        for tr in table.find_all("tr"):
            cells = [td.get_text(strip=True) for td in tr.find_all(["th", "td"])]
            if cells:
                rows.append(cells)
        return rows
