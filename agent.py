import subprocess
import os
import chromadb
from chromadb.utils import embedding_functions
from groq import Groq

API_KEY = os.getenv("GROQ_API_KEY", "").strip()
if not API_KEY:
    print(" Warning: GROQ_API_KEY not found in environment. using hardcoded placeholder.") 

client = Groq(api_key=API_KEY)

chroma_client = chromadb.PersistentClient(path="./chroma_db")
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
collection = chroma_client.get_collection(name="codebase", embedding_function=sentence_transformer_ef)

def run_tests():
    print(" running tests...")
    result = subprocess.run(
        ["pytest", "test_code.py"], 
        capture_output=True, 
        text=True
    )
    return result.returncode, result.stdout, result.stderr

def find_culprit_file(error_log):
    print(" Searching RAG memory for relevant files...")
    
    results = collection.query(
        query_texts=[error_log],
        n_results=1
    )
    
    if results['metadatas'] and results['metadatas'][0]:
        filename = results['metadatas'][0][0]['filename']
        print(f" identified culprit: {filename}")
        return filename
    
    return None

def get_ai_fix(error_log, code_content):
    print(" analyzing error with AI...")
    
    truncated_log = error_log[-2000:] if len(error_log) > 2000 else error_log

    prompt = f"""
    You are an expert Python debugger. 
    Here is a Python file that failed its unit tests.
    
    FILE CONTENT:
    {code_content}
    
    ERROR LOG:
    {truncated_log}
    
    TASK:
    Rewrite the ENTIRE file to fix the error.
    
    IMPORTANT GUIDELINES:
    1. Return ONLY the raw python code. 
    2. Do NOT use Markdown formatting (no ```python blocks).
    3. Do NOT provide explanations.
    """
    
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
        max_tokens=1024, 
        temperature=0 
    )
    
    return chat_completion.choices[0].message.content

def main():
    return_code, stdout, stderr = run_tests()
    
    if return_code == 0:
        print(" Tests Passed! No fix needed.")
        return

    print(" Tests Failed!")
    
    # 2. RAG Retrieval (The New Part)
    # Instead of hardcoding 'broken_code.py', we find it dynamically
    culprit_file = find_culprit_file(stdout + stderr)
    
    if not culprit_file:
        print(" Could not find relevant file in memory.")
        return

    # 3. Read the file
    with open(culprit_file, 'r') as f:
        original_code = f.read()
    
    # 4. Get the Fix
    fixed_code = get_ai_fix(stdout, original_code)
    
    # Clean up formatting
    fixed_code = fixed_code.replace("```python", "").replace("```", "").strip()

    # 5. Apply the Fix
    print(f" applying fix to {culprit_file}...")
    with open(culprit_file, 'w') as f:
        f.write(fixed_code)
    
    # 6. Verify
    print(" verifying fix...")
    return_code, stdout, stderr = run_tests()
    
    if return_code == 0:
        print(" SUCCESS! The AI fixed the code.")
    else:
        print(" The AI tried, but the tests still failed.")

if __name__ == "__main__":
    main()