"""File-system automation utilities."""

from __future__ import annotations

import os
import re
import shutil
from pathlib import Path
from typing import Callable, Dict, List, Optional


class File:
    """Utilities for file and directory operations, including batch renaming."""

    # ------------------------------------------------------------------
    # Listing
    # ------------------------------------------------------------------

    @staticmethod
    def list_files(
        directory: str,
        extensions: Optional[List[str]] = None,
        recursive: bool = False,
    ) -> List[str]:
        """List files in a directory, optionally filtered by extension.

        Args:
            directory:  Root directory to search.
            extensions: Optional list of extensions to include, e.g.
                        ``[".txt", ".pdf"]``. Case-insensitive.
            recursive:  If True, search sub-directories as well.

        Returns:
            Sorted list of absolute file paths.
        """
        root = Path(directory)
        if recursive:
            all_files = (p for p in root.rglob("*") if p.is_file())
        else:
            all_files = (p for p in root.iterdir() if p.is_file())

        if extensions:
            exts = {e.lower() if e.startswith(".") else f".{e.lower()}"
                    for e in extensions}
            all_files = (p for p in all_files if p.suffix.lower() in exts)

        return sorted(str(p.resolve()) for p in all_files)

    # ------------------------------------------------------------------
    # Batch rename
    # ------------------------------------------------------------------

    @staticmethod
    def batch_rename(
        directory: str,
        pattern: str,
        replacement: str,
        extensions: Optional[List[str]] = None,
        dry_run: bool = False,
    ) -> Dict[str, str]:
        """Batch-rename files by replacing a regex pattern in their names.

        Args:
            directory:   Directory containing the files to rename.
            pattern:     Regular expression pattern to match in filenames.
            replacement: Replacement string (supports back-references).
            extensions:  Optional list of extensions to target.
            dry_run:     If True, return the mapping without renaming anything.

        Returns:
            Dict mapping old absolute paths to new absolute paths.
        """
        files = File.list_files(directory, extensions=extensions)
        mapping: Dict[str, str] = {}

        for old_path_str in files:
            old_path = Path(old_path_str)
            new_name = re.sub(pattern, replacement, old_path.name)
            if new_name == old_path.name:
                continue
            new_path = old_path.parent / new_name
            mapping[old_path_str] = str(new_path.resolve())
            if not dry_run:
                old_path.rename(new_path)

        return mapping

    @staticmethod
    def batch_rename_numbered(
        directory: str,
        prefix: str = "file",
        start: int = 1,
        extensions: Optional[List[str]] = None,
        dry_run: bool = False,
    ) -> Dict[str, str]:
        """Rename all files in a directory to ``<prefix><n>.<ext>`` form.

        Args:
            directory:  Directory containing the files to rename.
            prefix:     Name prefix before the number.
            start:      Starting integer.
            extensions: Optional list of extensions to target.
            dry_run:    If True, return the mapping without renaming.

        Returns:
            Dict mapping old absolute paths to new absolute paths.
        """
        files = File.list_files(directory, extensions=extensions)
        mapping: Dict[str, str] = {}

        for idx, old_path_str in enumerate(files, start=start):
            old_path = Path(old_path_str)
            new_name = f"{prefix}{idx}{old_path.suffix}"
            new_path = old_path.parent / new_name
            mapping[old_path_str] = str(new_path.resolve())
            if not dry_run:
                old_path.rename(new_path)

        return mapping

    # ------------------------------------------------------------------
    # Copy / Move
    # ------------------------------------------------------------------

    @staticmethod
    def copy(src: str, dest: str) -> str:
        """Copy a file to a new location.

        Args:
            src:  Source file path.
            dest: Destination path (file or directory).

        Returns:
            Absolute path of the copied file.
        """
        dest_path = Path(dest)
        if dest_path.is_dir():
            dest_path = dest_path / Path(src).name
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, str(dest_path))
        return os.path.abspath(str(dest_path))

    @staticmethod
    def move(src: str, dest: str) -> str:
        """Move a file to a new location.

        Args:
            src:  Source file path.
            dest: Destination path (file or directory).

        Returns:
            Absolute path of the moved file.
        """
        dest_path = Path(dest)
        if dest_path.is_dir():
            dest_path = dest_path / Path(src).name
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(src, str(dest_path))
        return os.path.abspath(str(dest_path))

    # ------------------------------------------------------------------
    # Size helpers
    # ------------------------------------------------------------------

    @staticmethod
    def get_size(path: str, unit: str = "bytes") -> float:
        """Return the size of a file or directory.

        Args:
            path: File or directory path.
            unit: One of ``"bytes"``, ``"kb"``, ``"mb"``, ``"gb"``.

        Returns:
            Size as a float in the requested unit.
        """
        p = Path(path)
        if p.is_file():
            total = p.stat().st_size
        else:
            total = sum(f.stat().st_size for f in p.rglob("*") if f.is_file())

        divisors = {"bytes": 1, "kb": 1024, "mb": 1024**2, "gb": 1024**3}
        return total / divisors.get(unit.lower(), 1)
