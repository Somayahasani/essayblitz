# app.py — EssayBlitz FINAL FRIENDLY VERSION (no sidebar, super readable & kind)
# Deploy on Render → works instantly

import streamlit as st
from openai import OpenAI
import os

st.set_page_config(page_title="EssayBlitz", page_icon="heart", layout="centered")

# Soft & friendly design
st.markdown("""
<style>
    .bigscore {font-size:62px !important; font-weight:bold; text-align:center; margin:30px 0; color:#2c3e50;}
    .box {padding:20px; border-radius:18px; margin:15px 0; box-shadow: 0 4px 12px rgba(0,0,0,0.1);}
    .good {background:#e8f5e9; border-left:6px solid #4caf50;}
    .ok   {background:#fff8e1; border-left:6px solid #ff9800;}
    .bad  {background:#ffebee; border-left:6px solid #f44336;}
    .highlight {background:#f0f8ff; padding:20px; border-radius:14px; margin:20px 0;}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:#2c3e50;'>EssayBlitz</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; font-size:23px; color:#555;'>Your friendly AI essay helper — honest, kind, and super clear feedback in seconds</p>", unsafe_allow_html=True)

# TOKEN FROM ENV VAR ONLY
api_token = os.getenv("HF_TOKEN")
if not api_token:
    st.error("Server missing key — ping the creator!")
    st.stop()

client = OpenAI(api_key=api_token, base_url="https://router.huggingface.co/v1")

# INPUTS
col1, col2 = st.columns([2,1])
with col1:
    essay = st.text_area("Your essay", height=380, placeholder="Just paste it here — no stress ❤️")
with col2:
    prompt = st.text_area("What prompt are you answering? (optional)", height=150,
                          placeholder="e.g. “Why us?”, Prompt 3, etc.\nLeave blank if not sure")

if not prompt.strip():
    prompt = "Free choice"

# FRIENDLY BUTTON
if st.button("Get kind feedback", type="primary", use_container_width=True):
    if len(essay.strip()) < 60:
        st.warning("Add a bit more — at least 60 words please")
    else:
        with st.spinner("Your essay is being read with care…"):
            try:
                resp = client.chat.completions.create(
                    model="HuggingFaceTB/SmolLM3-3B:hf-inference",
                    temperature=0.7,
                    max_tokens=1200,
                    messages=[
                        {"role": "system", "content": """You are a super kind, encouraging college mentor.
Give feedback in this exact, friendly format only:

OVERALL FEELING: X/10

HOW WELL IT MATCHES THE PROMPT: X/10 → one short sentence

SCORES (be gentle but honest)
Hook & Opening: X/10 → one reason
Your Real Voice: X/10 → one reason
Story & Flow: X/10 → one reason
Clarity & Polish: X/10 → one reason

3 SMALL THINGS TO MAKE IT EVEN BETTER
1.
2.
3.

ONE PARAGRAPH REWRITTEN (to show how strong it can be):
[improved paragraph only]

FINAL WORDS OF ENCOURAGEMENT:
one warm, uplifting sentence"""},
                        {"role": "user", "content": f"Prompt: {prompt}\n\nEssay:\n{essay}"}
                    ]
                )
                fb = resp.choices[0].message.content.strip()

                st.success("Here’s your feedback just for you!")
                st.balloons()

                # Super clean & friendly display
                lines = [l.strip() for l in fb.split('\n') if l.strip()]

                for line in lines:
                    if line.startswith("OVERALL FEELING:"):
                        score = line.split(":")[1].strip()
                        st.markdown(f"<div class='bigscore'>{score}</div>", unsafe_allow_html=True)

                    elif line.startswith("HOW WELL IT MATCHES"):
                        st.markdown(f"<div class='box good'>{line}</div>", unsafe_allow_html=True)

                    elif line.startswith(("Hook & Opening:", "Your Real Voice:", "Story & Flow:", "Clarity & Polish:")):
                        parts = line.split(":", 1)
                        title = parts[0]
                        rest = parts[1].strip()
                        score = int(rest.split("/")[0])
                        if score >= 9:
                            st.markdown(f"<div class='good'>{title}<br><b>{rest}</b></div>", unsafe_allow_html=True)
                        elif score >= 7:
                            st.markdown(f"<div class='ok'>{title}<br><b>{rest}</b></div>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<div class='bad'>{title}<br><b>{rest}</b></div>", unsafe_allow_html=True)

                    elif line == "3 SMALL THINGS TO MAKE IT EVEN BETTER":
                        st.markdown("**3 small things to make it even better**")
                    elif line and line[0].isdigit() and "." in line:
                        st.markdown(f"<div class='box'>{line}</div>", unsafe_allow_html=True)

                    elif line.startswith("ONE PARAGRAPH REWRITTEN"):
                        st.markdown("**Here’s one paragraph made even stronger**")
                        para = "\n".join([l for l in lines[lines.index(line)+1:] if not l.startswith("FINAL WORDS")])
                        st.markdown(f"<div class='highlight'>{para}</div>", unsafe_allow_html=True)

                    elif line.startswith("FINAL WORDS OF ENCOURAGEMENT:"):
                        enc = line.split(":", 1)[1].strip()
                        st.markdown(f"<p style='text-align:center; font-size:24px; color:#e91e63; font-weight:bold;'>{enc}</p>", unsafe_allow_html=True)

            except Exception as e:
                st.error("Tiny hiccup — just click again ❤️")
                st.code(str(e))

st.markdown("---")
st.caption("Made with lots of love by a high-school senior | Always free | 2025")
