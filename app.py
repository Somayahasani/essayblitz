import os
import re
import math
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="EssayBlitz v4", page_icon="⭐", layout="centered")

# ─── SOFT LIGHT/DARK THEME ───
theme = st.sidebar.radio("Theme", ["Light", "Dark"])

# Soft colors
if theme == "Light":
    bg_main = "#f5f5f7"         # soft grayish background
    card_bg = "#ffffff"          # white cards
    text_color = "#1a1a1a"       # dark gray text
    secondary_text = "#555555"
    shadow = "rgba(0,0,0,0.08)"
elif theme == "Dark":
    bg_main = "#1a1a1a"          # soft dark gray
    card_bg = "#252525"          # slightly lighter card
    text_color = "#eaeaea"       # light gray text
    secondary_text = "#aaaaaa"
    shadow = "rgba(0,0,0,0.4)"

# ─── GLOBAL CSS ───
st.markdown(f"""
<style>
body {{
    background-color: {bg_main};
    color: {text_color};
}}
h1 {{
    font-size: 60px !important;
    font-weight: 900 !important;
    background: linear-gradient(90deg, #4A00E0, #8E2DE2);
    -webkit-background-clip: text;
    color: transparent;
    text-align: center;
    margin-bottom: 0;
}}
h2 {{
    text-align:center;
    font-size:20px;
    color:{secondary_text};
    margin-top:0;
}}
.card {{
    padding:25px;
    border-radius:18px;
    background:{card_bg};
    box-shadow:0 4px 18px {shadow};
    margin-bottom:20px;
}}
textarea {{
    border-radius: 12px !important;
    border: 1px solid #dcdcdc !important;
    padding: 12px !important;
    font-size: 16px !important;
    background-color: {card_bg} !important;
    color: {text_color} !important;
}}
div.stButton>button:first-child {{
    background: linear-gradient(90deg, #6a11cb, #2575fc);
    color: white;
    border-radius: 10px;
    padding: 12px 0;
    font-size: 18px;
    border: none;
}}
div.stButton>button:first-child:hover {{
    box-shadow:0 0 12px rgba(37,117,252,0.7);
}}
.bigfont {{font-size: 52px !important; font-weight: bold; text-align: center; margin: 20px;}}
.score-good {{background: linear-gradient(90deg, #d4edda, #c3e6cb); padding:16px; border-radius:16px; margin:12px 0; border-left:6px solid #28a745; color:black !important;}}
.score-ok {{background: linear-gradient(90deg, #fff3cd, #ffeaa7); padding:16px; border-radius:16px; margin:12px 0; border-left:6px solid #ffc107; color:black !important;}}
.score-bad {{background: linear-gradient(90deg, #f8d7da, #f5c6cb); padding:16px; border-radius:16px; margin:12px 0; border-left:6px solid #dc3545; color:black !important;}}
.fix {{background:{bg_main}; padding:15px; border-radius:12px; margin:8px 0; color:{text_color};}}
</style>
""", unsafe_allow_html=True)

# ─── HEADER ───
st.markdown("<h1>EssayBlitz v4</h1>", unsafe_allow_html=True)
st.markdown("<h2>AI-powered essay feedback — fast, polished, professional</h2>", unsafe_allow_html=True)

# ─── API CONFIG ───
api_token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACEHUB_API_TOKEN") or os.getenv("OPENAI_API_KEY")
if not api_token:
    st.sidebar.header("API Key")
    st.sidebar.error("No API token found in environment. Set HF_TOKEN or OPENAI_API_KEY.")
    st.stop()

client = OpenAI(api_key=api_token.strip(), base_url="https://router.huggingface.co/v1")

# ─── INPUTS ───
with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    col1, col2 = st.columns([2,1])
    with col1:
        essay = st.text_area(
            "Your full essay",
            height=380,
            placeholder="Paste your essay here… (minimum 80 words)"
        )
    with col2:
        custom_prompt = st.text_area(
            "Exact prompt you’re answering",
            height=200,
            placeholder="e.g.\nPrompt 5: Discuss an accomplishment…\nor\nWhy Stanford?"
        )
        if not custom_prompt.strip():
            custom_prompt = "Free choice / no specific prompt"
    st.markdown("</div>", unsafe_allow_html=True)

# ─── HELPER FUNCTION ───
def extract_score(text):
    m = re.search(r"(\d+(?:\.\d+)?)\s*/\s*10", text)
    if not m:
        m = re.search(r"^(\d+(?:\.\d+)?)(?!.*\d)", text)
    if m:
        try: return float(m.group(1))
        except: return None
    m = re.search(r"(\d+(?:\.\d+)?)", text)
    if m:
        try: return float(m.group(1))
        except: return None
    return None

# ─── FEEDBACK BUTTON ───
if st.button("Get Professional Feedback", type="primary", use_container_width=True):
    if len(essay.strip()) < 80:
        st.warning("Essay too short — need at least 80 words")
        st.stop()
    word_count = len(essay.split())
    est_minutes = max(1, math.ceil(word_count / 200))
    st.sidebar.header("Essay Stats")
    st.sidebar.metric("Word Count", word_count)
    st.sidebar.metric("Reading Time", f"{est_minutes} min")
    
    with st.spinner("Top admissions officer is reading your essay…"):
        try:
            completion = client.chat.completions.create(
                model="HuggingFaceTB/SmolLM3-3B:hf-inference",
                temperature=0.6,
                max_tokens=1400,
                messages=[
                    {"role":"system","content":"""
You are a professional admissions officer. Return ONLY this polished, concise, user-friendly format:

★ OVERALL EVALUATION
Score: X/10 → [1 clear sentence summarizing overall impression]

★ PROMPT CONNECTION
Score: X/10 → [how well it answers the prompt]

★ CATEGORY BREAKDOWN
Impact: X/10 → [short reason]
Authenticity: X/10 → [short reason]
Storytelling: X/10 → [short reason]
Clarity & Flow: X/10 → [short reason]
Writing Quality: X/10 → [short reason]

★ TOP 3 FIXES
1. [short actionable fix]
2. [short actionable fix]
3. [short actionable fix]

★ POLISHED SAMPLE PARAGRAPH
[improved paragraph — clean and readable]

★ FINAL NOTE
[a single encouraging sentence]
"""}, 
                    {"role":"user","content":f"Prompt: {custom_prompt}\n\nEssay:\n{essay}"}
                ]
            )
            feedback = completion.choices[0].message.content.strip()
            st.success("Feedback ready!")
            st.balloons()
            st.markdown(f"**Word count:** {word_count} words — **Estimated reading time:** {est_minutes} min")
            st.caption("Note: Feedback is automated and meant to guide improvement.")
            
            lines = [line.rstrip() for line in feedback.split("\n")]
            for line in lines:
                st.markdown(f"<div class='fix'>{line}</div>", unsafe_allow_html=True)
            
        except Exception as e:
            st.error("An API or parsing error occurred.")
            st.code(str(e))

# ─── FOOTER ───
st.markdown(f"""
<p style='text-align:center; color:{secondary_text}; font-size:14px;'>
Made with ❤️ by a high-school senior — 100% free forever  
<br>v4 • November 2025
</p>
""", unsafe_allow_html=True)
