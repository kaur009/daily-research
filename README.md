# 🤖 Daily AI Research Assistant
![Build Status](https://github.com/Muszic/daily-research/actions/workflows/daily_update.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.9-blue?logo=python&logoColor=white)
![AI Model](https://img.shields.io/badge/AI-Gemini%202.5%20Flash-magenta?logo=google&logoColor=white)
![Status](https://img.shields.io/badge/Status-Active%20Researcher-success)

**A fully autonomous AI agent that tracks, reads, and summarizes Computer Science research papers every day.**

---

### 🚀 How It Works
This repository is maintained by a Python bot that runs on a daily schedule via **GitHub Actions**. 
No human intervention is required.

1.  **🔍 Scout:** The bot queries the **ArXiv API** for the latest trending papers in Computer Vision, NLP, Robotics, and AI.
2.  **📥 Acquire:** It downloads the raw PDF of the selected paper.
3.  **🧠 Analyze:** It passes the text to **Google's Gemini 2.5 Flash** (via the `google-genai` SDK) to generate a structured research note.
4.  **📝 Publish:** The bot commits a new Markdown file to the `papers/` directory.

### 🛠️ Tech Stack
* **Core Logic:** Python 3.9
* **Automation:** GitHub Actions (Cron Job)
* **Intelligence:** Google Gemini 2.5 Flash
* **Data Source:** ArXiv Open API
* **PDF Parsing:** `pypdf`

---
*This repository is an example of CI/CD automation and applied LLM engineering.*
