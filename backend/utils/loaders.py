from pathlib import Path
from typing import List
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.documents import Document
import docx2txt


def load_documents(file_paths: List[str]):
    """Load documents from multiple file formats (PDF, DOCX, TXT)."""
    documents = []

    for file_path in file_paths:
        path = Path(file_path)

        if not path.exists():
            raise ValueError(f"File not found: {file_path}")

        if path.suffix.lower() == ".pdf":
            loader = PyPDFLoader(file_path)
            docs = loader.load()

        elif path.suffix.lower() == ".docx":
            content = docx2txt.process(file_path)
            if not content.strip():
                raise ValueError(f"Empty content in file: {file_path}")
            docs = [Document(page_content=content, metadata={"source": file_path})]

        elif path.suffix.lower() == ".txt":
            loader = TextLoader(file_path, encoding="utf-8")
            docs = loader.load()

        else:
            raise ValueError(
                f"Unsupported file format: {path.suffix}. Supported: PDF, DOCX, TXT"
            )

        if not docs or not any(doc.page_content.strip() for doc in docs):
            raise ValueError(f"Empty content in file: {file_path}")

        documents.extend(docs)

    return documents
