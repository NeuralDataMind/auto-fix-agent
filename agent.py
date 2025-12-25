import subprocess
import os
from groq import Groq

API_KEY = os.getenv("GROQ_API_KEY", "").strip() 

if not API_KEY:
    raise ValueError("API Key is missing or empty!")

client = Groq(api_key = API_KEY)

def run_tests():
    print(" running test...")
    result = subprocess.run(
        ["pytest", "test_code.py"],
        capture_output=True,
        text=True
    )
    return result.returncode, result.stdout, result.stderr

def read_file(filename):
    with open(filename, 'r') as f:
        return f.read()
    
def write_file(filename, content):
    with open(filename, 'w') as f:
        f.write(content)

def get_ai_fix(error_log, code_content):
    print(" analyzing error with AI...")
    
    truncated_log = error_log[-2000:] if len(error_log) > 2000 else error_log

    prompt = f"""
    You are an expert Python debugger. 
    Here is a Python file that failed its unit tests.
    
    FILE CONTENT:
    {code_content}
    
    ERROR LOG (Last 2000 chars):
    {truncated_log}
    
    TASK:
    Rewrite the 'broken_code.py' file to fix the error. 
    
    IMPORTANT GUIDELINES:
    1. Return ONLY the raw python code. 
    2. Do NOT use Markdown formatting (no ```python blocks).
    3. Do NOT provide explanations.
    """
    
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="llama-3.3-70b-versatile",
        max_tokens=1024, 
        temperature=0 
    )
    
    return chat_completion.choices[0].message.content

def main():
    return_code, stdout, stderr = run_tests()

    if return_code == 0:
        print(" Test passed! No fix needed.")
        return
    
    print(" Test Failed")
    print(f" Error Preview: {stdout[-300:]}") # Show last 300 char of error

    target_file = "broken_code.py"
    original_code = read_file(target_file)

    fixed_code = get_ai_fix(stdout, original_code)

    fixed_code = fixed_code.replace("```python", "").replace("```", "").strip()

    print(f" apply fix to {target_file}...")
    write_file(target_file, fixed_code)

    print(" verifying fix...")
    return_code, stdout, stderr = run_tests()

    if return_code == 0:
        print(" SUCCESS! The AI fixed the code.")
    else:
        print(" The AI tried, but the tests still failed.")

if __name__ == "__main__":
    main()