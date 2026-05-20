import os
import subprocess
from pathlib import Path

from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate


PERSIST_DIRECTORY = "./chroma_db"
COLLECTION_NAME = "codebase"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
LLM_MODEL = "llama-3.3-70b-versatile"

TOP_K = 3
MAX_ERROR_CHARS = 2000
TEST_COMMAND = ["pytest", "test_code.py"]


API_KEY = os.getenv("GROQ_API_KEY", "").strip()

if not API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY is missing. Set it locally or add it to GitHub repository secrets."
    )


embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

vector_store = Chroma(
    collection_name=COLLECTION_NAME,
    persist_directory=PERSIST_DIRECTORY,
    embedding_function=embeddings,
)

llm = ChatGroq(
    api_key=API_KEY,
    model=LLM_MODEL,
    temperature=0,
    max_tokens=8000,
)


def run_tests() -> tuple[int, str, str]:
    """
    Runs the test suite.

    Current prototype runs test_code.py directly.
    For a larger repo, change TEST_COMMAND to ["pytest"].
    """
    print("Running tests...")

    result = subprocess.run(
        TEST_COMMAND,
        capture_output=True,
        text=True,
    )

    return result.returncode, result.stdout, result.stderr


def extract_core_error(error_log: str) -> str:
    """
    Keep the most useful bottom section of the pytest failure log.

    The bottom of a traceback usually contains:
    - exception type
    - failing assertion
    - function name
    - file reference
    """
    if len(error_log) > MAX_ERROR_CHARS:
        return error_log[-MAX_ERROR_CHARS:]

    return error_log


def retrieve_relevant_chunks(error_log: str):
   # Retrieves top-k relevant code chunks from ChromaDB.

   
    print("Searching RAG memory for relevant code chunks...")

    core_error = extract_core_error(error_log)

    docs = vector_store.similarity_search(
        query=core_error,
        k=TOP_K,
    )

    if not docs:
        return []

    print("Top retrieval candidates:")

    for doc in docs:
        filename = doc.metadata.get("filename", "unknown")
        symbol = doc.metadata.get("symbol", "unknown")
        chunk_type = doc.metadata.get("chunk_type", "unknown")
        start_line = doc.metadata.get("start_line", "na")
        end_line = doc.metadata.get("end_line", "na")

        print(f"- {filename}::{symbol} [{chunk_type}] lines {start_line}-{end_line}")

    return docs


def choose_culprit_file(retrieved_docs) -> str | None:
   # Selects the file from the highest-ranked retrieved chunk.

    if not retrieved_docs:
        return None

    filename = retrieved_docs[0].metadata.get("filename")

    if not filename:
        return None

    return filename


def build_retrieved_context(retrieved_docs) -> str:
    # Converts retrieved LangChain Documents into compact prompt context.

    context_blocks = []

    for index, doc in enumerate(retrieved_docs, start=1):
        filename = doc.metadata.get("filename", "unknown")
        symbol = doc.metadata.get("symbol", "unknown")
        chunk_type = doc.metadata.get("chunk_type", "unknown")
        start_line = doc.metadata.get("start_line", "na")
        end_line = doc.metadata.get("end_line", "na")

        block = f"""
RETRIEVED CHUNK {index}
FILE: {filename}
SYMBOL: {symbol}
TYPE: {chunk_type}
LINES: {start_line}-{end_line}

{doc.page_content}
""".strip()

        context_blocks.append(block)

    return "\n\n---\n\n".join(context_blocks)


def get_ai_fix(error_log: str, full_file_content: str, retrieved_context: str) -> str:
#   Uses Groq through LangChain to generate the corrected Python file.

    print("Analyzing error with AI...")

    truncated_log = extract_core_error(error_log)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                (
                    "You are an expert Python debugger. "
                    "You fix failing Python code using pytest output and retrieved source context. "
                    "Return only raw executable Python code. "
                    "Do not include markdown, explanations, comments about the fix, or backticks."
                ),
            ),
            (
                "human",
                """
The test suite failed.

You are given:
1. Retrieved code chunks from the RAG system.
2. The full content of the selected target file.
3. The pytest error log.

Your task:
Return the fully corrected Python file.

Rules:
- Output only the complete corrected Python file.
- Do not output markdown.
- Do not output backticks.
- Do not explain the fix.
- Preserve unrelated working code.
- Make the smallest safe change that passes the tests.

RETRIEVED RAG CONTEXT:
{retrieved_context}

FULL TARGET FILE CONTENT:
{full_file_content}

ERROR LOG:
{error_log}
""",
            ),
        ]
    )

    chain = prompt | llm

    response = chain.invoke(
        {
            "retrieved_context": retrieved_context,
            "full_file_content": full_file_content,
            "error_log": truncated_log,
        }
    )

    return response.content


def clean_llm_code_output(raw_output: str) -> str:
    # Removes accidental markdown fences if the model ignores instructions.
    cleaned = raw_output.strip()

    if cleaned.startswith("```python"):
        cleaned = cleaned.removeprefix("```python").strip()

    if cleaned.startswith("```"):
        cleaned = cleaned.removeprefix("```").strip()

    if cleaned.endswith("```"):
        cleaned = cleaned.removesuffix("```").strip()

    return cleaned


def main() -> None:
    return_code, stdout, stderr = run_tests()

    if return_code == 0:
        print("Tests passed. No fix needed.")
        return

    print("Tests failed.")

    full_log = stdout + stderr

    retrieved_docs = retrieve_relevant_chunks(full_log)

    if not retrieved_docs:
        print("Could not find relevant code chunks in ChromaDB.")
        return

    culprit_file = choose_culprit_file(retrieved_docs)

    if not culprit_file:
        print("Could not identify culprit file from retrieved metadata.")
        return

    culprit_path = Path(culprit_file)

    if not culprit_path.exists():
        print(f"Retrieved file does not exist on disk: {culprit_file}")
        return

    print(f"Selected file for repair: {culprit_file}")

    with open(culprit_path, "r", encoding="utf-8") as file:
        original_code = file.read()

    retrieved_context = build_retrieved_context(retrieved_docs)

    fixed_code = get_ai_fix(
        error_log=full_log,
        full_file_content=original_code,
        retrieved_context=retrieved_context,
    )

    fixed_code = clean_llm_code_output(fixed_code)

    if not fixed_code:
        print("LLM returned empty output. Aborting.")
        return

    print(f"Applying fix to {culprit_file}...")

    with open(culprit_path, "w", encoding="utf-8") as file:
        file.write(fixed_code + "\n")

    print("Verifying fix...")

    return_code, stdout, stderr = run_tests()

    if return_code == 0:
        print("SUCCESS: The AI fixed the code.")
    else:
        print("The AI attempted a fix, but tests still failed.")
        print(stdout)
        print(stderr)


if __name__ == "__main__":
    main()
