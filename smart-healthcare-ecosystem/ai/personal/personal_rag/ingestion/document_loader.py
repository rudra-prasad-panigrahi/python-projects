from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader


SUPPORTED_EXTENSIONS = {
    ".txt",
    ".md",
    ".pdf",
}


def load_text_file(
    path: str | Path,
) -> str:
    return Path(path).read_text(
        encoding="utf-8",
        errors="replace",
    )


def load_pdf(
    path: str | Path,
) -> str:
    reader = PdfReader(
        str(path)
    )

    pages: list[str] = []

    for page in reader.pages:
        pages.append(
            page.extract_text() or ""
        )

    return "\n".join(pages)


def load_document(
    path: str | Path,
) -> str:
    file_path = Path(path)
    extension = file_path.suffix.lower()

    if extension == ".pdf":
        return load_pdf(file_path)

    if extension in {
        ".txt",
        ".md",
    }:
        return load_text_file(
            file_path
        )

    raise ValueError(
        f"Unsupported document type: {extension}"
    )