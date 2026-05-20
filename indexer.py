import ast
import os
from typing import Any

from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document


# Directories that should never be scanned
IGNORE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    "chroma_db",
    "node_modules",
}


# Files that belong to the agent itself, not the target codebase
IGNORE_FILES = {
    "agent.py",
    "indexer.py",
}    #agent_v2_langgraph_prototype.py need to be add


PERSIST_DIRECTORY = "./chroma_db"
COLLECTION_NAME = "codebase"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


def should_index_file(file_name: str) -> bool:
    """
    Decide whether a Python file should be indexed.

    We index application source files and skip tests, agent files,
    indexer files, and non-Python files.
    """
    if not file_name.endswith(".py"):
        return False

    if file_name in IGNORE_FILES:
        return False

    if file_name.startswith("test_") or file_name.endswith("_test.py"):
        return False

    return True


def extract_ast_chunks(file_path: str, content: str) -> list[Document]:
    """
    Split Python source code into AST-aware chunks.

    Instead of storing one embedding for the whole file, this extracts
    top-level functions, async functions, and classes as separate documents.

    If the file cannot be parsed, it falls back to whole-file indexing.
    """
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return [
            Document(
                page_content=content,
                metadata={
                    "filename": file_path,
                    "symbol": "whole_file",
                    "chunk_type": "syntax_fallback",
                },
            )
        ]

    lines = content.splitlines()
    documents: list[Document] = []

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            start_line = node.lineno
            end_line = getattr(node, "end_lineno", node.lineno)

            chunk_text = "\n".join(lines[start_line - 1:end_line]).strip()

            if not chunk_text:
                continue

            documents.append(
                Document(
                    page_content=chunk_text,
                    metadata={
                        "filename": file_path,
                        "symbol": node.name,
                        "chunk_type": type(node).__name__,
                        "start_line": start_line,
                        "end_line": end_line,
                    },
                )
            )

    # If no top-level function/class exists, index the whole file
    if not documents and content.strip():
        documents.append(
            Document(
                page_content=content,
                metadata={
                    "filename": file_path,
                    "symbol": "whole_file",
                    "chunk_type": "whole_file_fallback",
                },
            )
        )

    return documents


def load_code_documents(root_dir: str = ".") -> list[Document]:
    """
    Walk the repository and convert Python files into LangChain Documents.
    """
    all_documents: list[Document] = []

    files_processed = 0
    chunks_processed = 0

    print("Scanning codebase...")

    for root, dirs, files in os.walk(root_dir):
        # Prevent os.walk from entering ignored directories
        dirs[:] = [directory for directory in dirs if directory not in IGNORE_DIRS]

        for file_name in files:
            if not should_index_file(file_name):
                continue

            file_path = os.path.join(root, file_name)

            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
            except UnicodeDecodeError:
                print(f"Skipped non-UTF8 file: {file_path}")
                continue

            documents = extract_ast_chunks(file_path, content)

            if not documents:
                continue

            all_documents.extend(documents)

            files_processed += 1
            chunks_processed += len(documents)

            print(f"Indexed: {file_path} ({len(documents)} chunks)")

    print(f"Prepared {files_processed} files as {chunks_processed} chunks.")
    return all_documents


def build_vector_store(documents: list[Document]) -> None:
    """
    Build and persist the Chroma vector database using LangChain.
    """
    if not documents:
        print("No valid Python source documents found to index.")
        return

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    # Stable IDs prevent duplicate records when re-indexing unchanged chunks
    ids = []
    for doc in documents:
        filename = doc.metadata.get("filename", "unknown")
        symbol = doc.metadata.get("symbol", "unknown")
        start_line = doc.metadata.get("start_line", "na")
        ids.append(f"{filename}::{symbol}::{start_line}")

    Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        ids=ids,
        collection_name=COLLECTION_NAME,
        persist_directory=PERSIST_DIRECTORY,
    )

    print(f"Successfully indexed {len(documents)} chunks into ChromaDB.")


def index_codebase(root_dir: str = ".") -> None:
    documents = load_code_documents(root_dir=root_dir)
    build_vector_store(documents)


if __name__ == "__main__":
    index_codebase()
