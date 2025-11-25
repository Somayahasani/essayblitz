# app.py — EssayBlitz FINAL PUBLIC VERSION (no sidebar, perfect feedback)
# Deploy on Render → works instantly

import streamlit as st
from openai import OpenAI
import os

st.set_page_config(page_title="EssayBlitz", page_icon="rocket", layout="centered")

# Beautiful design
st.markdown("""
<style>
    .bigfont {font-size:56px !important; font-weight:bold; text-align:center; margin:30px 0;}
    .good {background:#d4edda; padding:18px; border-radius:16px; margin:12px 0; border-left:8px solid #28a745; color:black;}
    .ok   {background:#fff3cd; padding:18px; border-radius:16px; margin:12px 0; border-left:8px solid #ffc107; color:black;}
    .bad  {background:#f8d7da; padding:18px; border-radius:16px; margin:12px 0; border-left:8px solid #dc3545; color:black;}
    .fix  {background:#f0f2f0; padding:16px; border-radius:12px; margin:10px 0;}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;'>EssayBlitz</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; font-size:22px;'>Free Harvard-level college essay feedback</p>", unsafe_allow_html=True)

# TOKEN FROM ENVIRONMENT ONLY — NO SIDEBAR
api_token = os.getenv("HF_TOKEN")

if not api_token:
    st.error("Server error — contact developer")
    st.stop()

client = OpenAI(api_key=api_token, base_url="https://router.huggingface.co/v1")

# INPUTS
col1, col2 = st.columns([2,1])
with col1:
    essay = st.text_area("Your full essay", height=380, placeholder="Paste your essay here…")
with col2:
    prompt = st.text_area("Prompt you're answering (optional)", height=200,
                          placeholder="e.g. Prompt 5, Why Stanford?, etc.")

if not prompt.strip():
    prompt = "Free choice"

# BUTTON
if st.button("Get Feedback →", type="primary", use_container_width=True):
    ):
    if len(essay.strip()) < 80:
        st.warning("Need at least 80 words")
    else:
        with st.spinner("Reading your essay…"):
            try:
                resp = client.chat.completions.create(
                    model="HuggingFaceTB/SmolLM3-3B:hf-inference",
                    temperature=0.6,
                    max_tokens=1200,
                    messages=[
                        {"role": "system", "content": """You are a Harvard admissions officer.
Return feedback in this exact order, nothing else:

OVERALL SCORE: X/10

ON-TOPIC SCORE: X/10 → one short sentence

Impact: X/10 → one reason
Prompt Fit: X/10 → one reason
Authenticity: X/10 → one reason
Storytelling: X/10 → one reason
Clarity & Style: X/10 → one reason

3 QUICK FIXES:
1.
2.
3.

REWRITTEN PARAGRAPH:
[improved paragraph only]

ENCOURAGEMENT: one positive sentence"""},
                        {"role": "user", "content": f"Prompt: {prompt}\n\nEssay:\n{essay}"}
                    ]
                )
                fb = resp.choices[0].message.content.strip()

                st.success("Feedback ready!")
                st.balloons()

                # Simple, safe display (no complex parsing)
                st.markdown(f"### {fb.replace('OVERALL SCORE', '**OVERALL SCORE**').replace('ON-TOPIC SCORE', '**ON-TOPIC SCORE**').replace('3 QUICK FIXES', '**3 QUICK FIXES**').replace('REWRITTEN PARAGRAPH', '**REWRITTEN PARAGRAPH**').replace('ENCOURAGEMENT', '**ENCOURAGEMENT**')}", unsafe_allow_html=True)

            except Exception as e:
                st.error("Temporary issue — click again in 10 seconds")
                st.code(str(e))

st.caption("Made with ❤️ by a high-school senior | 100% free forever | 2025")
