# 🛡️ Auto-Fix Agent: RAG-Powered Self-Healing CI/CD

![Status](https://img.shields.io/badge/Status-Active-success)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![AI](https://img.shields.io/badge/Model-Llama3-orange)
![RAG](https://img.shields.io/badge/RAG-ChromaDB-green)

## 🚀 Overview
**Auto-Fix Agent** is an autonomous AI Engineer that lives inside your GitHub Actions pipeline. Unlike standard coding assistants that wait for prompts, this agent **proactively intercepts build failures**, analyzes the root cause, and pushes fixes automatically.

It uses **Retrieval Augmented Generation (RAG)** to scan the repository, identify the specific file causing the error (even if not explicitly named in the logs), and applies semantic patches using **Llama 3**.

## 🧠 How It Works (The Architecture)

The system operates on a "Loop of Reasoning" whenever a developer pushes code:

1.  **🚨 Interception:** The GitHub Action detects a failed `pytest` run and captures the `stderr` trace.
2.  **🔍 Retrieval (The Brain):**
    * The agent uses **Sentence Transformers** to convert the error log into a vector embedding.
    * It queries **ChromaDB** (Vector Database) to find the most relevant source code file responsible for the crash.
3.  **🤖 Reasoning:**
    * The retrieved code + error context is sent to **Llama 3-70B** (via Groq).
    * The LLM generates a syntax-valid Python patch.
4.  **🧪 Verification:**
    * The agent applies the fix and re-runs the tests in a sandboxed environment.
    * If tests pass, it pushes a commit to the `main` branch.

## ⚡ Key Features
* **Context-Aware Debugging:** Uses Vector Search to find bugs across the codebase, not just in hardcoded files.
* **Zero-Touch Automation:** Fixes `IndexError`, `TypeError`, and logic bugs without human intervention.
* **Self-Cleaning Infrastructure:** Automatically builds and wipes the vector memory (`chroma_db`) on every run to ensure fresh context.
* **Defensive Coding:** The AI implements `try-except` blocks and type checks to prevent future crashes.

## 🛠️ Tech Stack
* **Core:** Python 3.12, Pytest, GitPython
* **AI & LLM:** Llama 3 (Groq API), LangChain concepts
* **RAG & Memory:** ChromaDB, Sentence-Transformers (`all-MiniLM-L6-v2`)
* **DevOps:** GitHub Actions, Docker (via Runner)

## 📦 Setup & Usage

### 1. Fork & Clone
```bash
git clone [https://github.com/YOUR_USERNAME/auto-fix-agent.git](https://github.com/YOUR_USERNAME/auto-fix-agent.git)
cd auto-fix-agent

```

### 2. Install Dependencies

```bash
pip install -r requirements.txt

```

### 3. Set Up API Key

You need a [Groq API Key](https://console.groq.com/).

* **Locally:** Set `GROQ_API_KEY` in your environment variables.
* **GitHub:** Add `GROQ_API_KEY` to Repository Secrets.

### 4. Run Manually (Local Mode)

To test the agent on your local machine:

```bash
# 1. Build the memory
python indexer.py

# 2. Run the agent (requires a broken test)
python agent.py

```

## 📸 Proof of Concept

*The agent automatically detecting a `TypeError`, searching ChromaDB for the culprit file, and pushing a defensive fix:*

> **Commit Message:** `🤖 AI Auto-Fix: Resolved Unit Test Failures`

---

*Built by Mallikarjun using GenAI and Grit.*

```

### **Why this README wins:**
1.  **Architecture Section:** It explains *how* it works (recruiters love "ReAct" and "RAG" keywords).
2.  **Badges:** It looks like a maintained open-source tool.
3.  **Focus on "Proactive":** It highlights that this tool works *automatically*, which is the definition of "Indispensable" (your original requirement).

**Update the file, commit, and push. You are now fully ready to showcase this.**
Would you like to move on to the next project (Graph Fraud Detection)?

```
