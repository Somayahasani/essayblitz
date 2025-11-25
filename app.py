# app.py — EssayBlitz v5 FINAL (Public, No API-key-free version)
# Deployed on Render → https://essayblitz-1.onrender.com

import streamlit as st
from openai import OpenAI
import os

# ────────────────────── PAGE SETUP ──────────────────────
st.set_page_config(page_title="EssayBlitz", page_icon="rocket", layout="centered")

# Beautiful CSS
st.markdown("""
<style>
    .bigfont {font-size: 56px !important; font-weight: bold; text-align: center; margin: 30px 0;}
    .score-good {background: linear-gradient(90deg, #d4edda, #c3e6cb); padding: 18px; border-radius: 16px; margin: 12px 0; border-left: 8px solid #28a745; color: black;}
    .score-ok   {background: linear-gradient(90deg, #fff3cd, #ffeaa7); padding: 18px; border-radius: 16px; margin: 12px 0; border-left: 8px solid #ffc107; color: black;}
    .score-bad  {background: linear-gradient(90deg, #f8d7da, #f5c6cb); padding: 18px; border-radius: 16px; margin: 12px 0; border-left: 8px solid #dc3545; color: black;}
    .fix {background:#f0f2f6; padding:16px; border-radius:12px; margin:10px 0; color:black;}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;'>EssayBlitz</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; font-size:22px;'>Free professional college essay feedback — in 5 seconds</p>", unsafe_allow_html=True)

# ────────────────────── GET TOKEN (ENV VAR FIRST) ──────────────────────
api_token = os.getenv("HF_TOKEN")  # ← Render automatically provides this

# Optional sidebar only for LOCAL testing (will be hidden on public)
with st.sidebar:
    st.caption("Local dev only")
    st.text_input("HF Token", type="password", value="", disabled=True)

if not api_token:
    st.error("Missing HF_TOKEN — add it in Render → Environment Variables")
    st.stop()

client = OpenAI(api_key=api_token, base_url="https://router.huggingface.co/v1")

# ────────────────────── INPUTS ──────────────────────
col1, col2 = st.columns([2, 1])
with col1:
    essay = st.text_area("Your full essay", height=380, placeholder="Paste your essay here…")
with col2:
    custom_prompt = st.text_area("Exact prompt you're answering", height=200,
                                 placeholder="e.g. Prompt 5, Why Stanford?, etc.\nLeave empty = free choice")

if not custom_prompt.strip():
    custom_prompt = "Free choice / no specific prompt"

# ────────────────────── GRADING BUTTON ──────────────────────
if st.button("Get Professional Feedback →", type="primary", use_container_width=True):
    if len(essay.strip()) < 80:
        st.warning("Please write at least 80 words")
    else:
        with st.spinner("Harvard admissions officer is reading…"):
            try:
                completion = client.chat.completions.create(
                    model="HuggingFaceTB/SmolLM3-3B:hf-inference",
                    temperature=0.6,
                    max_tokens=1400,
                    messages=[
                        {"role": "system", "content": """You are a Harvard admissions officer.
Return ONLY this exact format:

OVERALL: X/10

ON-TOPIC: X/10 → [1 sentence]

SCORES
Impact: X/10 → [reason]
Prompt Fit: X/10 → [reason]
Authenticity: X/10 → [reason]
Storytelling: X/10 → [reason]
Clarity: X/10 → [reason]

3 QUICK FIXES
1. 
2. 
3. 

REWRITTEN PARAGRAPH:
[only the improved paragraph]

ONE SENTENCE OF ENCOURAGEMENT:"""},

                        {"role": "user", "content": f"Prompt: {custom_prompt}\n\nEssay:\n{essay}"}
                    ]
                )
                feedback = completion.choices[0].message.content.strip()

                st.success("Feedback ready!")
                st.balloons()

                # ─── DISPLAY ───
                lines = [l.strip() for l in feedback.split('\n') if l.strip()]

                for line in lines:
                    if line.startswith("OVERALL:"):
                        score = line.split(":")[1].strip()
                        st.markdown(f"<div class='bigfont'>{score}</div>", unsafe_allow_html=True)

                    elif "ON-TOPIC:" in line:
                        st.markdown(f"**{line}**")

                    elif line.startswith(("Impact:", "Prompt Fit:", "Authenticity:", "Storytelling:", "Clarity:")):
                        parts = line.split(":", 1)
                        title = parts[0].strip()
                        rest = parts[1].strip()
                        score_num = int(rest.split("/")[0])
                        if score_num >= 9:
                            st.markdown(f"<div class='score-good'>star {title}<br><b>{rest}</b></div>", unsafe_allow_html=True)
                        elif score_num >= 7:
                            st.markdown(f"<div class='score-ok'>warning {title}<br><b>{rest}</b></div>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<div class='score-bad'>cross {title}<br><b>{rest}</b></div>", unsafe_allow_html=True)

                    elif line == "3 QUICK FIXES":
                        st.markdown("**3 QUICK FIXES**")
                    elif line and line[0].isdigit() and "." in line:
                        st.markdown(f"<div class='fix'>{line}</div>", unsafe_allow_html=True)

                    elif line.startswith("REWRITTEN PARAGRAPH:"):
                        st.markdown("**BEST PARAGRAPH REWRITTEN**")
                        para = "\n".join([l for l in lines[lines.index(line)+1:] if not l.startswith("ONE SENTENCE")])
                        st.markdown(f"<div style='background:#e8f4fd;padding:20px;border-radius:14px;color:black;'>{para}</div>", unsafe_allow_html=True)

                    elif line.startswith("ONE SENTENCE OF ENCOURAGEMENT:"):
                        enc = line.split(":", 1)[1].strip()
                        st.markdown(f"<p style='text-align:center;font-size:21px;font-style:italic;color:#2c3e50;'>{enc}</p>", unsafe_allow_html=True)

            except Exception as e:
                st.error("Temporary API hiccup — try again in 10 seconds")
                st.code(str(e))

st.markdown("---")
st.caption("Made with love by a high-school senior | 100% free forever | November 2025")
