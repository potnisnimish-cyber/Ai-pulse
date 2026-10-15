# 📰 AI Pulse — Automated Student Newsletter Generator

> Built at **TCS Tech Day @ VESIT** | P7 Problem Statement

## What it does
AI Pulse automatically collects the latest AI & tech news from approved sources, filters them for student relevance using Gemini AI, and generates a clean, editable weekly/monthly newsletter.

## Features
- 📡 Fetches articles from 5 approved RSS sources (Google AI, MIT Tech Review, HuggingFace, OpenAI, VentureBeat)
- 🤖 AI summarizes each article into 3 bullet points
- 🎯 Relevance scoring for CS/AI students
- ✏️ Editable review interface — approve or remove articles
- 📄 Downloadable newsletter in Markdown format

## Tech Stack
- Python + Streamlit (UI)
- Google Gemini 1.5 Flash (AI summarization)
- feedparser (RSS fetching)

## Setup Instructions

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/ai-pulse.git
cd ai-pulse
```

### 2. Install dependencies
```bash
pip install streamlit feedparser google-generativeai
```

### 3. Add your Gemini API Key
Open `app.py` and replace line 10:
```python
GEMINI_API_KEY = "PASTE_YOUR_GEMINI_API_KEY_HERE"
```
Get a free key at: https://aistudio.google.com/app/apikey

### 4. Run the app
```bash
streamlit run app.py
```

## How to Use
1. Open the app in browser
2. Set edition (Weekly/Monthly) and relevance score in sidebar
3. Click **Generate Newsletter**
4. Review and edit articles
5. Download the final newsletter

## Team
Built at TCS Tech Day Hackathon @ VESIT
