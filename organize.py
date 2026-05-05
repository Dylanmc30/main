#!/usr/bin/env python3
"""Organize files in a directory into subfolders by file type."""

import argparse
import shutil
from pathlib import Path

CATEGORIES = {
    "Images":     {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico", ".tiff"},
    "Videos":     {".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv", ".webm", ".m4v"},
    "Audio":      {".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma"},
    "Documents":  {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".odt", ".ods"},
    "Text":       {".txt", ".md", ".csv", ".json", ".xml", ".yaml", ".yml", ".toml", ".ini", ".log"},
    "Code":       {".py", ".js", ".ts", ".html", ".css", ".java", ".c", ".cpp", ".h", ".go", ".rs", ".rb", ".php", ".sh"},
    "Archives":   {".zip", ".tar", ".gz", ".bz2", ".xz", ".7z", ".rar"},
    "Executables":{".exe", ".msi", ".deb", ".rpm", ".dmg", ".AppImage"},
}


def get_category(suffix: str) -> str:
    suffix = suffix.lower()
    for category, extensions in CATEGORIES.items():
        if suffix in extensions:
            return category
    return "Other"


def organize(directory: Path, dry_run: bool) -> None:
    files = [f for f in directory.iterdir() if f.is_file()]

    if not files:
        print("No files found.")
        return

    moves: list[tuple[Path, Path]] = []
    for file in files:
        category = get_category(file.suffix)
        destination = directory / category / file.name
        if destination == file:
            continue
        moves.append((file, destination))

    if not moves:
        print("Everything is already organized.")
        return

    for src, dst in moves:
        print(f"  {'[dry run] ' if dry_run else ''}{'→'} {dst.relative_to(directory)}")
        if not dry_run:
            dst.parent.mkdir(exist_ok=True)
            # Avoid overwriting: append a counter if the destination exists
            counter = 1
            original_dst = dst
            while dst.exists():
                dst = original_dst.with_stem(f"{original_dst.stem}_{counter}")
                counter += 1
            shutil.move(str(src), dst)

    print(f"\n{'Would move' if dry_run else 'Moved'} {len(moves)} file(s).")


def main() -> None:
    parser = argparse.ArgumentParser(description="Organize files into subfolders by type.")
    parser.add_argument("directory", nargs="?", default=".", help="Directory to organize (default: current directory)")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without moving files")
    args = parser.parse_args()

    directory = Path(args.directory).resolve()
    if not directory.is_dir():
        parser.error(f"Not a directory: {directory}")

    print(f"Organizing: {directory}" + (" (dry run)" if args.dry_run else ""))
    organize(directory, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
