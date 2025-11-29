import os
import re
import math
import streamlit as st
from openai import OpenAI

st.set_page_config(
    page_title="EssayBlitz v4",
    page_icon="star",
    layout="centered"
)

# Fixed CSS — text is now BLACK inside colored boxes
st.markdown("""
<style>
.bigfont {font-size: 52px !important; font-weight: bold; text-align: center; margin: 20px;}
.score-good {background: linear-gradient(90deg, #d4edda, #c3e6cb); padding: 16px; border-radius: 16px; margin: 12px 0; border-left: 6px solid #28a745; color: black !important;}
.score-ok {background: linear-gradient(90deg, #fff3cd, #ffeaa7); padding: 16px; border-radius: 16px; margin: 12px 0; border-left: 6px solid #ffc107; color: black !important;}
.score-bad {background: linear-gradient(90deg, #f8d7da, #f5c6cb); padding: 16px; border-radius: 16px; margin: 12px 0; border-left: 6px solid #dc3545; color: black !important;}
.fix {background:#f0f2f6; padding:15px; border-radius:12px; margin:8px 0; color: black;}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;'>EssayBlitz v4</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; font-size:20px;'>Professional college essay feedback — free & beautiful</p>", unsafe_allow_html=True)

# ─── API CONFIG ───
api_token = (
    os.getenv("HF_TOKEN")
    or os.getenv("HUGGINGFACEHUB_API_TOKEN")
    or os.getenv("OPENAI_API_KEY")
)

if not api_token:
    st.sidebar.header("API Key")
    st.sidebar.error("No API token found in environment. Set HF_TOKEN or OPENAI_API_KEY in your deployment secrets.")
    st.stop()

client = OpenAI(
    api_key=api_token.strip(),
    base_url="https://router.huggingface.co/v1"
)

# ─── INPUTS ───
col1, col2 = st.columns([2, 1])

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

# Helper: extract score
def extract_score(text):
    m = re.search(r"(\d+(?:\.\d+)?)\s*/\s*10", text)
    if not m:
        m = re.search(r"^(\d+(?:\.\d+)?)(?!.*\d)", text)
    if m:
        try:
            return float(m.group(1))
        except Exception:
            return None
    m = re.search(r"(\d+(?:\.\d+)?)", text)
    if m:
        try:
            return float(m.group(1))
        except Exception:
            return None
    return None

# ─── BIG BUTTON ───
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
You are an admissions officer. Return ONLY this polished, concise, user-friendly format:

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
"""
                    },
                    {
                        "role": "user",
                        "content": f"Prompt: {custom_prompt}\n\nEssay:\n{essay}"
                    }
                ]
            )

            feedback = completion.choices[0].message.content.strip()

            st.success("Feedback ready!")
            st.balloons()

            st.markdown(
                f"**Word count:** {word_count} words — **Estimated reading time:** {est_minutes} minute(s)"
            )
            st.caption("Note: Feedback is automated and meant to guide improvement.")

            lines = [line.rstrip() for line in feedback.split("\n")]

            # OVERALL block
            overall_shown = False
            for line in lines:
                if line.strip().startswith("OVERALL:"):
                    score = line.split(":", 1)[1].strip()
                    st.markdown(f"<div class='bigfont'>{score}</div>", unsafe_allow_html=True)
                    overall_shown = True
                    break

            if not overall_shown:
                st.warning("OVERALL score not found in model output. Displaying raw feedback below.")

            i = 0
            while i < len(lines):
                line = lines[i].strip()

                if not line:
                    i += 1
                    continue

                if line.startswith("ON-TOPIC:"):
                    st.markdown(f"**{line}**")
                    i += 1
                    continue

                if any(line.startswith(prefix) for prefix in ("Impact:", "Prompt Fit:", "Authenticity:", "Storytelling:", "Clarity:")):
                    parts = line.split(":", 1)
                    title = parts[0].strip()
                    rest = parts[1].strip()
                    score_val = extract_score(rest)

                    if score_val is not None:
                        if score_val >= 9:
                            st.markdown(f"<div class='score-good'>{title}<br><b>{rest}</b></div>", unsafe_allow_html=True)
                        elif score_val >= 7:
                            st.markdown(f"<div class='score-ok'>{title}<br><b>{rest}</b></div>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<div class='score-bad'>{title}<br><b>{rest}</b></div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='fix'>{title}<br><b>{rest}</b></div>", unsafe_allow_html=True)

                    i += 1
                    continue

                if line == "3 QUICK FIXES":
                    st.markdown("**3 QUICK FIXES**")
                    i += 1
                    continue

                if re.match(r"^\d+\.\s+", line):
                    st.markdown(f"<div class='fix'>{line}</div>", unsafe_allow_html=True)
                    i += 1
                    continue

                if line.startswith("REWRITTEN PARAGRAPH:"):
                    para_lines = []
                    j = i + 1
                    while j < len(lines) and not lines[j].startswith("ONE SENTENCE OF ENCOURAGEMENT:"):
                        para_lines.append(lines[j])
                        j += 1
                    para = "\n".join(para_lines).strip()

                    if para:
                        st.markdown("**BEST PARAGRAPH REWRITTEN**")
                        st.markdown(
                            f"<div style='background:#e8f4fd; padding:18px; border-radius:14px; color:black;'>{para}</div>",
                            unsafe_allow_html=True
                        )
                    i = j
                    continue

                if line.startswith("ONE SENTENCE OF ENCOURAGEMENT:"):
                    enc = line.replace("ONE SENTENCE OF ENCOURAGEMENT:", "").strip()
                    if not enc and i + 1 < len(lines):
                        enc = lines[i + 1].strip()
                        i += 1

                    st.markdown(
                        f"<p style='text-align:center; font-size:20px; font-style:italic; color:#1e3799;'>{enc}</p>",
                        unsafe_allow_html=True
                    )
                    i += 1
                    continue

                # Fallback
                st.write(line)
                i += 1

        except Exception as e:
            st.error("An API or parsing error occurred. Check deployment secret and model output format.")
            st.code(str(e))

st.markdown("---")
st.caption("Made with love by a high-school senior | 100% free forever | v4 – November 2025")
