"""
tools.py — tool concreti che leggono file reali dalla cartella docs/.
Nessuna dipendenza esterna.
"""
from __future__ import annotations

from pathlib import Path


ALLOWED_EXTENSIONS = (".txt", ".md")
DOCS_DIR = Path("C:/Users.../sentinel_agent/docs")


def list_documents() -> list[str]:
    """Restituisce i nomi dei file .txt e .md nella cartella docs/."""
    if not DOCS_DIR.exists():
        return []
    return sorted(
        p.name
        for p in DOCS_DIR.iterdir()
        if p.is_file() and p.suffix.lower() in ALLOWED_EXTENSIONS
    )


def read_document(filename: str) -> str:
    """Legge e restituisce il contenuto di un file in docs/."""
    # blocca path traversal (es. filename="../../etc/passwd")
    safe_path = (DOCS_DIR / Path(filename).name).resolve()
    docs_root = DOCS_DIR.resolve()

    if not str(safe_path).startswith(str(docs_root)):
        raise PermissionError(f"Accesso negato: '{filename}' fuori da docs/")
    if not safe_path.exists():
        raise FileNotFoundError(f"File non trovato: '{filename}'")
    if safe_path.suffix.lower() not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Estensione non consentita: '{safe_path.suffix}'")

    return safe_path.read_text(encoding="utf-8")
