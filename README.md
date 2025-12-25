# 🛡️ Auto-Fix Agent: Self-Healing CI/CD Pipeline

![Status](https://img.shields.io/badge/Status-Active-success)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![AI](https://img.shields.io/badge/Model-Llama3-orange)

## 🚀 Overview
**Auto-Fix Agent** is an autonomous DevOps tool that integrates into GitHub Actions to **self-heal broken builds**. 

When a unit test fails, the agent:
1.  **Intercepts** the error logs from the CI pipeline.
2.  **Analyzes** the root cause using **Llama 3** (via Groq LPUs).
3.  **Patches** the source code automatically.
4.  **Verifies** the fix with regression testing.
5.  **Pushes** the corrected code back to the repository.

## 🏗️ Architecture
The system follows a **ReAct (Reasoning + Acting)** workflow:
1.  **Detector:** A Python script runs `pytest` and captures `stderr` streams.
2.  **Reasoning Engine:** The error trace + source code is sent to the LLM with a strict JSON schema for code generation.
3.  **Actuator:** The system applies the patch and re-runs tests in an isolated environment.
4.  **GitOps:** If tests pass, the bot commits the changes as `AutoFix AI`.

## 🛠️ Tech Stack
* **Core:** Python 3.12, Pytest, Subprocess
* **AI/LLM:** Llama 3-70B, Groq API (Low Latency Inference)
* **CI/CD:** GitHub Actions (YAML Workflows)
* **Version Control:** Git Automation

## ⚡ Key Features
* **Zero-Touch Debugging:** fixes `IndexError`, `TypeError`, and logic bugs without human intervention.
* **Cost Optimized:** Implements token truncation and output limits to minimize API usage.
* **Security:** API keys are injected via GitHub Secrets; logs are sanitized to prevent leakage.

## 📸 Proof of Concept
*The agent automatically fixing a `TypeError` by implementing type-casting and error handling:*
![Fix Demo](https://github.com/NeuralDataMind/auto-fix-agent/blob/main/broken_code.py)
**
