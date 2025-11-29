import os
import re
import math
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="EssayBlitz v4", page_icon="⭐", layout="centered")

# ───────────────────────────── CSS ─────────────────────────────
st.markdown("""
<style>
.score-good {background:#d4edda;padding:15px;border-radius:10px;border-left:6px solid #28a745;margin:8px 0;}
.score-ok   {background:#fff3cd;padding:15px;border-radius:10px;border-left:6px solid #ffc107;margin:8px 0;}
.score-bad  {background:#f8d7da;padding:15px;border-radius:10px;border-left:6px solid #dc3545;margin:8px 0;}
.fix        {background:#f0f2f6;padding:12px;border-radius:10px;margin:8px 0;}
.bigscore   {font-size:46px;font-weight:bold;text-align:center;margin:20px;}
</style>
""", unsafe_allow_html=True)

st.title("EssayBlitz v4 — Stable JSON Edition")
st.caption("Professional college essay feedback — zero parsing errors")

# ───────────────────────────── API ─────────────────────────────
api_token = os.getenv("HF_TOKEN") or os.getenv("OPENAI_API_KEY")
if not api_token:
    st.error("No API Key found in environment.")
    st.stop()

client = OpenAI(api_key=api_token.strip(), base_url="https://router.huggingface.co/v1")

# ───────────────────────────── Input UI ─────────────────────────────
essay = st.text_area("Your essay", height=380)
prompt = st.text_area("Prompt (optional)", height=130)
if not prompt.strip():
    prompt = "No prompt provided"

# ───────────────────────────── JSON SAFE FORMAT ─────────────────────────────

SYSTEM_PROMPT_JSON = """
You are a professional admissions officer.
You MUST return ALL output ONLY as valid JSON.
No stars, no markdown, no explanation — ONLY raw JSON.

The JSON format MUST be:

{
  "overall_score": number,
  "overall_comment": "string",

  "prompt_score": number,
  "prompt_comment": "string",

  "categories": {
    "Impact": {"score": number, "reason": "string"},
    "Authenticity": {"score": number, "reason": "string"},
    "Storytelling": {"score": number, "reason": "string"},
    "Clarity": {"score": number, "reason": "string"},
    "WritingQuality": {"score": number, "reason": "string"}
  },

  "fixes": ["string", "string", "string"],

  "polished_paragraph": "string",
  "final_note": "string"
}

THIS FORMAT IS REQUIRED.
"""

# ───────────────────────────── Extraction Helper ─────────────────────────────
def classify(score):
    if score >= 9: return "score-good"
    if score >= 7: return "score-ok"
    return "score-bad"


# ───────────────────────────── Button Action ─────────────────────────────
if st.button("Get Feedback", use_container_width=True):

    if len(essay.strip()) < 80:
        st.warning("Essay too short — need at least 80 words.")
        st.stop()

    with st.spinner("Evaluating your essay…"):

        try:
            response = client.chat.completions.create(
                model="HuggingFaceTB/SmolLM3-3B:hf-inference",
                temperature=0.4,
                max_tokens=2000,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT_JSON},
                    {"role": "user", "content": f"Prompt: {prompt}\nEssay:\n{essay}"}
                ]
            )

            raw = response.choices[0].message.content

            # Parse JSON safely
            import json
            data = json.loads(raw)

        except Exception as e:
            st.error("Model returned invalid JSON. (The model may not support strict JSON reliably.)")
            st.code(str(e))
            st.stop()

        # ───────────────────────────── DISPLAY RESULTS ─────────────────────────────

        # BIG SCORE
        st.markdown(f"<div class='bigscore'>{data['overall_score']}/10</div>", unsafe_allow_html=True)
        st.write(data["overall_comment"])

        # PROMPT
        st.subheader("Prompt Connection")
        st.markdown(f"<div class='{classify(data['prompt_score'])}'><b>{data['prompt_score']}/10</b><br>{data['prompt_comment']}</div>", unsafe_allow_html=True)

        # CATEGORY BREAKDOWN
        st.subheader("Category Breakdown")
        for cat, info in data["categories"].items():
            st.markdown(
                f"<div class='{classify(info['score'])}'><b>{cat}: {info['score']}/10</b><br>{info['reason']}</div>",
                unsafe_allow_html=True
            )

        # FIXES
        st.subheader("Top 3 Fixes")
        for fix in data["fixes"]:
            st.markdown(f"<div class='fix'>{fix}</div>", unsafe_allow_html=True)

        # POLISHED PARAGRAPH
        st.subheader("Polished Sample Paragraph")
        st.write(data["polished_paragraph"])

        # FINAL NOTE
        st.subheader("Final Note")
        st.write(data["final_note"])
