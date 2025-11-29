import os
import re
import math
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="EssayBlitz v4", page_icon="star", layout="centered")

# ────────────────────────── CSS ──────────────────────────
st.markdown("""
<style>
    .bigfont {font-size: 52px !important; font-weight: bold; text-align: center; margin: 20px;}
    .score-good {background: linear-gradient(90deg, #d4edda, #c3e6cb); padding: 16px; border-radius: 16px; margin: 12px 0; border-left: 6px solid #28a745; color: black !important;}
    .score-ok   {background: linear-gradient(90deg, #fff3cd, #ffeaa7); padding: 16px; border-radius: 16px; margin: 12px 0; border-left: 6px solid #ffc107; color: black !important;}
    .score-bad  {background: linear-gradient(90deg, #f8d7da, #f5c6cb); padding: 16px; border-radius: 16px; margin: 12px 0; border-left: 6px solid #dc3545; color: black !important;}
    .fix {background:#f0f2f6; padding:15px; border-radius:12px; margin:8px 0; color: black;}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;'>EssayBlitz v4</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; font-size:20px;'>Professional college essay feedback — free & beautiful</p>", unsafe_allow_html=True)

# ────────────────────────── API CONFIG ──────────────────────────
api_token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACEHUB_API_TOKEN") or os.getenv("OPENAI_API_KEY")

if not api_token:
    st.sidebar.header("API Key")
    st.sidebar.error("No API token found. Set HF_TOKEN or OPENAI_API_KEY in the environment.")
    st.stop()

client = OpenAI(api_key=api_token.strip(), base_url="https://router.huggingface.co/v1")

# ────────────────────────── INPUT UI ──────────────────────────
col1, col2 = st.columns([2, 1])

with col1:
    essay = st.text_area("Your full essay", height=380, placeholder="Paste your essay here… (minimum 80 words)")

with col2:
    custom_prompt = st.text_area("Exact prompt you’re answering", height=200,
                                 placeholder="e.g.\nPrompt 5: Discuss an accomplishment…")
    if not custom_prompt.strip():
        custom_prompt = "Free choice / no specific prompt"


# Score extraction helper
def extract_score(text):
    m = re.search(r"(\d+(?:\.\d+)?)\s*/\s*10", text)
    if m:
        return float(m.group(1))
    m = re.search(r"(\d+(?:\.\d+)?)", text)
    if m:
        return float(m.group(1))
    return None


# ────────────────────────── MAIN ACTION ──────────────────────────
if st.button("Get Professional Feedback", type="primary", use_container_width=True):
    if len(essay.strip()) < 80:
        st.warning("Essay too short — need at least 80 words")
        st.stop()

    word_count = len(essay.split())
    est_minutes = max(1, math.ceil(word_count / 200))

    with st.spinner("Top admissions officer is reading your essay…"):
        try:
            completion = client.chat.completions.create(
                model="HuggingFaceTB/SmolLM3-3B:hf-inference",
                temperature=0.6,
                max_tokens=1400,
                messages=[
                    {
                        "role": "system",
                        "content": """
You are a professional admissions officer.
Return ONLY the following structure:

★ OVERALL EVALUATION
Score: X/10 → [summary]

★ PROMPT CONNECTION
Score: X/10 → [evaluation]

★ CATEGORY BREAKDOWN
Impact: X/10 → [reason]
Authenticity: X/10 → [reason]
Storytelling: X/10 → [reason]
Clarity & Flow: X/10 → [reason]
Writing Quality: X/10 → [reason]

★ TOP 3 FIXES
1. ...
2. ...
3. ...

★ POLISHED SAMPLE PARAGRAPH
[improved paragraph]

★ FINAL NOTE
[1 encouraging sentence]
                        """
                    },
                    {"role": "user", "content": f"Prompt: {custom_prompt}\n\nEssay:\n{essay}"}
                ]
            )

            feedback = completion.choices[0].message.content.strip()

            # ────────────────────────── OUTPUT PROCESSING ──────────────────────────
            st.success("Feedback ready!")
            st.balloons()

            st.markdown(f"**Word count:** {word_count} words — **Estimated reading:** {est_minutes} min")
            st.caption("Feedback is automated; always check for originality.")

            lines = [line.rstrip() for line in feedback.split("\n")]

            # Display overall score
            overall_score = None
            for line in lines:
                if line.startswith("Score:") and "OVERALL" in "".join(lines[:5]):
                    val = extract_score(line)
                    if val:
                        overall_score = val
                        st.markdown(f"<div class='bigfont'>{val}/10</div>", unsafe_allow_html=True)
                    break

            # Iterate content
            i = 0
            while i < len(lines):
                line = lines[i].strip()

                # HEADERS
                if line.startswith("★ OVERALL EVALUATION"):
                    st.header("Overall Evaluation")
                    i += 1
                    continue

                if line.startswith("★ PROMPT CONNECTION"):
                    st.header("Prompt Connection")
                    i += 1
                    continue

                if line.startswith("★ CATEGORY BREAKDOWN"):
                    st.header("Category Breakdown")
                    i += 1
                    continue

                if line.startswith("★ TOP 3 FIXES"):
                    st.header("Top 3 Fixes")
                    i += 1
                    continue

                if line.startswith("★ POLISHED SAMPLE PARAGRAPH"):
                    st.header("Polished Sample Paragraph")
                    i += 1
                    continue

                if line.startswith("★ FINAL NOTE"):
                    st.header("Final Note")
                    i += 1
                    continue

                # CATEGORY SCORES
                if any(line.startswith(prefix) for prefix in ("Impact:", "Authenticity:", "Storytelling:", "Clarity", "Writing Quality")):
                    parts = line.split("→")
                    title = parts[0].strip()
                    rest = parts[1].strip() if len(parts) > 1 else ""

                    score_val = extract_score(title)
                    if score_val is None:
                        score_val = extract_score(rest)

                    if score_val is not None:
                        if score_val >= 9:
                            box = "score-good"
                        elif score_val >= 7:
                            box = "score-ok"
                        else:
                            box = "score-bad"
                        st.markdown(f"<div class='{box}'><b>{title}</b><br>{rest}</div>", unsafe_allow_html=True)
                    else:
                        st.write(line)

                    i += 1
                    continue

                # FIXES (numbered)
                if re.match(r"^\d+\.\s", line):
                    st.markdown(f"<div class='fix'>{line}</div>", unsafe_allow_html=True)
                    i += 1
                    continue

                # PARAGRAPH BLOCK
                if line and not line.startswith("★"):
                    st.write(line)

                i += 1

        except Exception as e:
            st.error("An API or parsing error occurred.")
            st.code(str(e))

st.markdown("---")
st.caption("Made with love | v4 – November 2025")
