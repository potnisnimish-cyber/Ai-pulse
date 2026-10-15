import streamlit as st
import feedparser
import google.generativeai as genai
from datetime import datetime
import time
import os

# ============================================================
# ADD YOUR GEMINI API KEY HERE
# Get free key from: https://aistudio.google.com/app/apikey
# ============================================================
GEMINI_API_KEY = "PASTE_YOUR_GEMINI_API_KEY_HERE"
# ============================================================

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

FEEDS = [
    ("Google AI Blog", "https://blog.research.google/feeds/posts/default"),
    ("MIT Tech Review AI", "https://www.technologyreview.com/feed/"),
    ("Hugging Face Blog", "https://huggingface.co/blog/feed.xml"),
    ("OpenAI News", "https://openai.com/news/rss.xml"),
    ("VentureBeat AI", "https://venturebeat.com/category/ai/feed/"),
]

def fetch_articles(max_per_feed=3):
    articles = []
    for source_name, url in FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:max_per_feed]:
                articles.append({
                    "title": entry.get("title", "No Title"),
                    "link": entry.get("link", "#"),
                    "summary": entry.get("summary", entry.get("description", ""))[:500],
                    "published": entry.get("published", "Unknown date"),
                    "source": source_name,
                })
        except Exception:
            continue
    return articles

def ai_process(article):
    prompt = f"""
You are an AI newsletter editor for college students studying software engineering.

Article Title: {article['title']}
Source: {article['source']}
Content: {article['summary']}

Return EXACTLY in this format (no extra text):
HEADLINE: <rewritten catchy headline>
SUMMARY: <3 bullet points, each starting with •>
WHY_IT_MATTERS: <1 sentence explaining relevance to CS/AI students>
TAGS: <2-3 topic tags separated by commas>
READ_TIME: <estimated read time like "2 min read">
RELEVANCE: <score from 1-10 for student relevance>
"""
    try:
        response = model.generate_content(prompt)
        text = response.text
        result = {}
        for line in text.strip().split("\n"):
            if ":" in line:
                key, _, val = line.partition(":")
                result[key.strip()] = val.strip()
        result["original_link"] = article["link"]
        result["source"] = article["source"]
        result["published"] = article["published"]
        result["raw_title"] = article["title"]
        return result
    except Exception as e:
        return None

st.set_page_config(page_title="AI Pulse Newsletter", page_icon="📰", layout="wide")

st.markdown("""
<h1 style='text-align:center; color:#4F8BF9;'>📰 AI Pulse</h1>
<p style='text-align:center; color:gray;'>Automated Student Newsletter Generator — TCS Tech Day @ VESIT</p>
<hr>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Controls")
    edition = st.radio("Edition", ["Weekly", "Monthly"])
    min_relevance = st.slider("Min Relevance Score", 1, 10, 3)
    max_articles = st.slider("Max Articles in Newsletter", 3, 10, 5)
    generate_btn = st.button("🚀 Generate Newsletter", use_container_width=True)

if generate_btn:
    with st.spinner("📡 Fetching latest AI updates..."):
        raw_articles = fetch_articles(max_per_feed=3)

    st.info(f"✅ Fetched {len(raw_articles)} articles. Now processing with AI...")

    processed = []
    progress = st.progress(0)
    for i, art in enumerate(raw_articles):
        result = ai_process(art)
        if result:
            try:
                score = int(result.get("RELEVANCE", "0"))
            except:
                score = 0
            result["score"] = score
            if score >= min_relevance:
                processed.append(result)
        progress.progress((i + 1) / len(raw_articles))
        time.sleep(0.3)

    processed = sorted(processed, key=lambda x: x.get("score", 0), reverse=True)[:max_articles]
    st.success(f"🎯 {len(processed)} relevant articles selected!")
    st.markdown("---")
    st.session_state["articles"] = processed
    st.session_state["edition"] = edition

if "articles" in st.session_state:
    articles = st.session_state["articles"]
    edition = st.session_state.get("edition", "Weekly")

    st.subheader(f"📋 Review & Edit — {edition} Edition ({datetime.now().strftime('%B %Y')})")

    approved = []
    for i, art in enumerate(articles):
        with st.expander(f"[{art.get('RELEVANCE','?')}/10] {art.get('HEADLINE', art.get('raw_title','Article'))}", expanded=(i==0)):
            col1, col2 = st.columns([3, 1])
            with col1:
                include = st.checkbox("Include in newsletter", value=True, key=f"inc_{i}")
                headline = st.text_input("Headline", value=art.get("HEADLINE", ""), key=f"h_{i}")
                summary = st.text_area("Summary", value=art.get("SUMMARY", ""), height=100, key=f"s_{i}")
                why = st.text_input("Why it matters", value=art.get("WHY_IT_MATTERS", ""), key=f"w_{i}")
            with col2:
                st.metric("Relevance", f"{art.get('RELEVANCE','?')}/10")
                st.caption(f"🏷️ {art.get('TAGS','')}")
                st.caption(f"⏱️ {art.get('READ_TIME','')}")
                st.caption(f"📰 {art.get('source','')}")
                st.markdown(f"[🔗 Read Full Article]({art.get('original_link','#')})")

            if include:
                approved.append({**art, "HEADLINE": headline, "SUMMARY": summary, "WHY_IT_MATTERS": why})

    st.markdown("---")

    if approved:
        st.subheader("📄 Newsletter Preview")
        newsletter_md = f"# 📰 AI Pulse — {edition} Edition\n"
        newsletter_md += f"**{datetime.now().strftime('%B %d, %Y')}** | Curated for CS & AI Students @ VESIT\n\n---\n\n"

        for idx, art in enumerate(approved, 1):
            newsletter_md += f"## {idx}. {art.get('HEADLINE','')}\n"
            newsletter_md += f"*{art.get('TAGS','')} | {art.get('READ_TIME','')} | Source: {art.get('source','')}*\n\n"
            newsletter_md += f"{art.get('SUMMARY','')}\n\n"
            newsletter_md += f"> 💡 **Why it matters:** {art.get('WHY_IT_MATTERS','')}\n\n"
            newsletter_md += f"[Read Full Article →]({art.get('original_link','#')})\n\n---\n\n"

        newsletter_md += "*Generated by AI Pulse | TCS Tech Day @ VESIT*"

        st.markdown(newsletter_md)

        st.download_button(
            label="⬇️ Download Newsletter (Markdown)",
            data=newsletter_md,
            file_name=f"AI_Pulse_{edition}_{datetime.now().strftime('%Y_%m')}.md",
            mime="text/markdown",
            use_container_width=True
        )
    else:
        st.warning("No articles selected. Check at least one article above.")
