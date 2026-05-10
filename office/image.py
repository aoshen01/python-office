"""Image processing utilities."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional, Tuple, Union

from PIL import Image as PILImage, ImageDraw, ImageFont


class Image:
    """Utilities for resizing, converting, and watermarking images."""

    # ------------------------------------------------------------------
    # Basic operations
    # ------------------------------------------------------------------

    @staticmethod
    def resize(
        filepath: str,
        width: int,
        height: int,
        output_path: Optional[str] = None,
        keep_aspect: bool = False,
    ) -> str:
        """Resize an image.

        Args:
            filepath:    Path to the source image.
            width:       Target width in pixels.
            height:      Target height in pixels.
            output_path: Destination path. Defaults to overwriting the source.
            keep_aspect: If True, resize proportionally so the image fits
                         within (width × height) while maintaining its aspect
                         ratio.

        Returns:
            Absolute path of the saved image.
        """
        img = PILImage.open(filepath)
        if keep_aspect:
            img.thumbnail((width, height), PILImage.LANCZOS)
        else:
            img = img.resize((width, height), PILImage.LANCZOS)

        dest = output_path or filepath
        Path(dest).parent.mkdir(parents=True, exist_ok=True)
        img.save(dest)
        return os.path.abspath(dest)

    @staticmethod
    def convert(
        filepath: str,
        target_format: str,
        output_path: Optional[str] = None,
    ) -> str:
        """Convert an image to a different format.

        Args:
            filepath:      Path to the source image.
            target_format: Target format string, e.g. ``"PNG"``, ``"JPEG"``,
                           ``"WEBP"``, ``"BMP"``.
            output_path:   Destination path. Defaults to same stem as source
                           with the new extension.

        Returns:
            Absolute path of the converted image.
        """
        img = PILImage.open(filepath)
        fmt = target_format.upper()
        ext = fmt.lower()
        if ext == "jpeg":
            ext = "jpg"

        dest = output_path or Path(filepath).with_suffix(f".{ext}")
        Path(dest).parent.mkdir(parents=True, exist_ok=True)

        if fmt == "JPEG" and img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        img.save(str(dest), format=fmt)
        return os.path.abspath(str(dest))

    # ------------------------------------------------------------------
    # Watermarking
    # ------------------------------------------------------------------

    @staticmethod
    def add_text_watermark(
        filepath: str,
        text: str,
        output_path: Optional[str] = None,
        opacity: int = 100,
        color: Tuple[int, int, int] = (200, 200, 200),
        font_size: int = 40,
        position: Union[str, Tuple[int, int]] = "center",
    ) -> str:
        """Add a text watermark to an image.

        Args:
            filepath:    Path to the source image.
            text:        Watermark text string.
            output_path: Destination path. Defaults to overwriting the source.
            opacity:     Watermark opacity (0–255).
            color:       RGB colour tuple for the watermark text.
            font_size:   Font size in points.
            position:    ``"center"``, ``"top-left"``, ``"top-right"``,
                         ``"bottom-left"``, ``"bottom-right"``, or an (x, y)
                         pixel tuple.

        Returns:
            Absolute path of the watermarked image.
        """
        img = PILImage.open(filepath).convert("RGBA")
        overlay = PILImage.new("RGBA", img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)

        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except (IOError, OSError):
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        w, h = img.size

        if position == "center":
            xy: Tuple[int, int] = ((w - text_w) // 2, (h - text_h) // 2)
        elif position == "top-left":
            xy = (10, 10)
        elif position == "top-right":
            xy = (w - text_w - 10, 10)
        elif position == "bottom-left":
            xy = (10, h - text_h - 10)
        elif position == "bottom-right":
            xy = (w - text_w - 10, h - text_h - 10)
        else:
            xy = tuple(position)  # type: ignore[assignment]

        fill = (*color, opacity)
        draw.text(xy, text, font=font, fill=fill)

        watermarked = PILImage.alpha_composite(img, overlay).convert("RGB")
        dest = output_path or filepath
        Path(dest).parent.mkdir(parents=True, exist_ok=True)
        watermarked.save(dest)
        return os.path.abspath(dest)

    @staticmethod
    def add_image_watermark(
        filepath: str,
        watermark_path: str,
        output_path: Optional[str] = None,
        opacity: int = 128,
        position: Union[str, Tuple[int, int]] = "bottom-right",
        scale: float = 0.25,
    ) -> str:
        """Overlay an image watermark on another image.

        Args:
            filepath:       Path to the source image.
            watermark_path: Path to the watermark image (must support RGBA).
            output_path:    Destination path. Defaults to overwriting the source.
            opacity:        Watermark opacity (0–255).
            position:       ``"center"``, ``"top-left"``, ``"top-right"``,
                            ``"bottom-left"``, ``"bottom-right"``, or (x, y).
            scale:          Watermark size as a fraction of the source width.

        Returns:
            Absolute path of the watermarked image.
        """
        base = PILImage.open(filepath).convert("RGBA")
        wm = PILImage.open(watermark_path).convert("RGBA")

        new_wm_w = int(base.width * scale)
        ratio = new_wm_w / wm.width
        new_wm_h = int(wm.height * ratio)
        wm = wm.resize((new_wm_w, new_wm_h), PILImage.LANCZOS)

        r, g, b, a = wm.split()
        a = a.point(lambda p: int(p * opacity / 255))
        wm.putalpha(a)

        bw, bh = base.size
        ww, wh = wm.size

        if position == "center":
            pos: Tuple[int, int] = ((bw - ww) // 2, (bh - wh) // 2)
        elif position == "top-left":
            pos = (10, 10)
        elif position == "top-right":
            pos = (bw - ww - 10, 10)
        elif position == "bottom-left":
            pos = (10, bh - wh - 10)
        elif position == "bottom-right":
            pos = (bw - ww - 10, bh - wh - 10)
        else:
            pos = tuple(position)  # type: ignore[assignment]

        base.paste(wm, pos, wm)
        result = base.convert("RGB")
        dest = output_path or filepath
        Path(dest).parent.mkdir(parents=True, exist_ok=True)
        result.save(dest)
        return os.path.abspath(dest)

    # ------------------------------------------------------------------
    # Thumbnails
    # ------------------------------------------------------------------

    @staticmethod
    def thumbnail(
        filepath: str,
        max_size: int = 256,
        output_path: Optional[str] = None,
    ) -> str:
        """Create a square-bound thumbnail preserving aspect ratio.

        Args:
            filepath:    Path to the source image.
            max_size:    Maximum dimension (width or height) of the thumbnail.
            output_path: Destination path. Defaults to ``<stem>_thumb.<ext>``.

        Returns:
            Absolute path of the thumbnail image.
        """
        img = PILImage.open(filepath)
        img.thumbnail((max_size, max_size), PILImage.LANCZOS)

        if output_path is None:
            p = Path(filepath)
            output_path = str(p.with_stem(p.stem + "_thumb"))

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        img.save(output_path)
        return os.path.abspath(output_path)
