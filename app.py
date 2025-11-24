# app.py → EssayBlitz v4 – Text now BLACK & perfectly readable
# → streamlit run app.py

import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="EssayBlitz v4", page_icon="star", layout="centered")

# Fixed CSS — text is now BLACK inside colored boxes
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

# ─── SIDEBAR TOKEN ───
with st.sidebar:
    st.header("API Key")
    api_token = st.text_input("Hugging Face Token (hf_…)", type="password", value="")
    if not api_token.strip():
        st.info("Get free token → huggingface.co/settings/tokens")
        st.stop()

client = OpenAI(api_key=api_token.strip(), base_url="https://router.huggingface.co/v1")

# ─── INPUTS ───
col1, col2 = st.columns([2, 1])

with col1:
    essay = st.text_area("Your full essay", height=380, placeholder="Paste your essay here… (minimum 80 words)")

with col2:
    custom_prompt = st.text_area("Exact prompt you’re answering", height=200,
                                 placeholder="e.g.\nPrompt 5: Discuss an accomplishment…\nor\nWhy Stanford?")
    if not custom_prompt.strip():
        custom_prompt = "Free choice / no specific prompt"

# ─── BIG BUTTON ───
if st.button("Get Professional Feedback", type="primary", use_container_width=True):
    if len(essay.strip()) < 80:
        st.warning("Essay too short — need at least 80 words")
        st.stop()

    with st.spinner("Top admissions officer is reading your essay…"):
        try:
            completion = client.chat.completions.create(
                model="HuggingFaceTB/SmolLM3-3B:hf-inference",
                temperature=0.6,
                max_tokens=1400,
                messages=[
                    {"role": "system", "content": """You are a Harvard admissions officer.
Return ONLY this exact format (no extra text):

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

            # ─── GORGEOUS DISPLAY (text now perfectly visible) ───
            st.success("Feedback ready!")
            st.balloons()

            lines = [line.strip() for line in feedback.split('\n') if line.strip()]

            # Overall score
            for line in lines:
                if line.startswith("OVERALL:"):
                    score = line.split(":")[1].strip()
                    st.markdown(f"<div class='bigfont'>{score}</div>", unsafe_allow_html=True)
                    break

            for line in lines:
                if "ON-TOPIC:" in line:
                    st.markdown(f"**{line}**")

                elif line.startswith(("Impact:", "Prompt Fit:", "Authenticity:", "Storytelling:", "Clarity:")):
                    parts = line.split(":")
                    title = parts[0].strip()
                    rest = ":".join(parts[1:]).strip()
                    score = int(rest.split("/")[0])
                    if score >= 9:
                        st.markdown(f"<div class='score-good'>star {title}<br><b>{rest}</b></div>", unsafe_allow_html=True)
                    elif score >= 7:
                        st.markdown(f"<div class='score-ok'>warning {title}<br><b>{rest}</b></div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='score-bad'>cross {title}<br><b>{rest}</b></div>", unsafe_allow_html=True)

                elif line == "3 QUICK FIXES":
                    st.markdown("**3 QUICK FIXES**")
                elif line and line[0].isdigit() and "." in line:
                    st.markdown(f"<div class='fix'>{line}</div>", unsafe_allow_html=True)

                elif line.startswith("REWRITTEN PARAGRAPH:"):
                    st.markdown("**BEST PARAGRAPH REWRITTEN**")
                    para_lines = []
                    for l in lines[lines.index(line)+1:]:
                        if not l.startswith("ONE SENTENCE"):
                            para_lines.append(l)
                        else:
                            break
                    para = "\n".join(para_lines)
                    st.markdown(f"<div style='background:#e8f4fd; padding:18px; border-radius:14px; color:black;'>{para}</div>", unsafe_allow_html=True)

                elif line.startswith("ONE SENTENCE OF ENCOURAGEMENT:"):
                    enc = line.replace("ONE SENTENCE OF ENCOURAGEMENT:", "").strip()
                    st.markdown(f"<p style='text-align:center; font-size:20px; font-style:italic; color:#1e3799;'>{enc}</p>", unsafe_allow_html=True)

        except Exception as e:
            st.error("Temporary API hiccup — click again in 10 seconds")
            st.code(str(e))

st.markdown("---")
st.caption("Made with love by a high-school senior | 100% free forever | v4 – November 2025")