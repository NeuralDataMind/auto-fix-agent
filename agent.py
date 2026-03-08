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

def get_ai_fix(error_log, code_content):
    print(" analyzing error with AI...")
    
    truncated_log = error_log[-2000:] if len(error_log) > 2000 else error_log

    prompt = f"""
    You are an expert Python debugger. 
    Analyze the following failed unit test and provide the fully corrected Python file.
    
    FILE CONTENT:
    {code_content}
    
    ERROR LOG:
    {truncated_log}
    
    OUTPUT FORMAT INSTRUCTIONS:
    Output ONLY the raw, executable Python code. 
    Start immediately with the first line of code. 
    End immediately after the last line of code.
    No explanations. No markdown formatting. No backticks. Just code.
    """
    
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
        max_tokens=8000, 
        temperature=0 
    )
    
    return chat_completion.choices[0].message.content

def extract_core_error(error_log):
    """Extracts the bottom of the stack trace where the actual error and filename reside."""
    # Grab the last 1000 characters to ensure we capture the failure reason
    return error_log[-1000:] if len(error_log) > 1000 else error_log

def find_culprit_file(error_log):
    print(" Searching RAG memory for relevant files...")
    
    # 🚨 CRITICAL FIX: Truncate the log BEFORE sending to the embedding model
    core_error = extract_core_error(error_log)
    
    results = collection.query(
        query_texts=[core_error],
        n_results=1
    )
    
    if results['metadatas'] and results['metadatas'][0]:
        filename = results['metadatas'][0][0]['filename']
        print(f" identified culprit: {filename}")
        return filename
    
    return None

def main():
    return_code, stdout, stderr = run_tests()
    
    if return_code == 0:
        print(" Tests Passed! No fix needed.")
        return

    print(" Tests Failed!")
    
    # Combine outputs
    full_log = stdout + stderr
    
    # Pass to RAG
    culprit_file = find_culprit_file(full_log)
    
    if not culprit_file:
        print(" Could not find relevant file in memory.")
        return

    with open(culprit_file, 'r', encoding='utf-8') as f:
        original_code = f.read()
    
    # Get fix from LLM
    fixed_code = get_ai_fix(full_log, original_code)
    
    # Clean up formatting
    fixed_code = fixed_code.replace("```python", "").replace("```", "").strip()

    print(f" applying fix to {culprit_file}...")
    with open(culprit_file, 'w', encoding='utf-8') as f:
        f.write(fixed_code)
    
    print(" verifying fix...")
    return_code, stdout, stderr = run_tests()
    
    if return_code == 0:
        print(" SUCCESS! The AI fixed the code.")
    else:
        print(" The AI tried, but the tests still failed.")

if __name__ == "__main__":
    main()