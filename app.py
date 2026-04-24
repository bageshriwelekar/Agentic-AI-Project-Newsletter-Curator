"""
Newsletter Curator — Main Streamlit Application
================================================
Multi-agent AI pipeline:
  Agent 1 (Researcher)  → Tavily Search → raw stories
  Agent 2 (Grouper)     → Gemini LLM   → themed clusters
  Agent 3 (Writer)      → Gemini LLM   → full newsletter
  Judge   (Evaluator)   → Gemini LLM   → quality scores
"""

import streamlit as st
from agents.researcher import research_stories
from agents.grouper import group_stories
from agents.writer import write_newsletter
from agents.judge import evaluate_newsletter

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="The Curator — Newsletter Intelligence",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=UnifrakturMaguntia&family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&family=IM+Fell+English:ital@0;1&family=Courier+Prime:ital,wght@0,400;0,700;1,400&display=swap');

/* ══════════════════════════════════════════════
   FOUNDATION — force parchment background + dark text EVERYWHERE in main
   ══════════════════════════════════════════════ */
html, body { background-color: #faf3e0 !important; color: #1c1410 !important; }

/* Every generic Streamlit wrapper in the main area */
.main, .main .block-container,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"] {
    background-color: #faf3e0 !important;
    color: #1c1410 !important;
}

/* Horizontal rule line texture */
.main .block-container {
    background-image: repeating-linear-gradient(
        0deg, transparent, transparent 27px,
        rgba(180,155,100,0.07) 27px, rgba(180,155,100,0.07) 28px
    ) !important;
    padding-top: 2rem !important;
}

/* ── GLOBAL TEXT: every element in main gets dark ink ── */
.main p, .main span, .main div, .main li, .main label,
.main strong, .main em, .main a, .main h1, .main h2, .main h3,
[data-testid="stMarkdownContainer"] *,
[data-testid="stText"] *,
[data-testid="stWrite"] *,
[data-testid="element-container"] p,
[data-testid="element-container"] span {
    color: #1c1410 !important;
}

/* STATUS BOXES: cream background, dark text */
[data-testid="stStatus"],
[data-testid="stStatus"] > div,
[data-testid="stStatusBody"],
[data-testid="stVerticalBlockBorderWrapper"],
[data-testid="stVerticalBlockBorderWrapper"] > div {
    background-color: #fffdf5 !important;
    color: #1c1410 !important;
}
[data-testid="stStatus"] * { color: #1c1410 !important; }
[data-testid="stVerticalBlockBorderWrapper"] * { color: #1c1410 !important; }

/* Status header row keep its own styled bg */
[data-testid="stStatus"] > div:first-child { background-color: #f0e8d0 !important; }

/* FIX garbage beck/arror text: the status widget icon span uses a material icon ligature
   that renders as garbage text when our custom fonts are applied. Reset font to system. */
[data-testid="stStatus"] > div:first-child span { font-family: sans-serif !important; }
[data-testid="stStatus"] > div:first-child button { font-family: sans-serif !important; }
[data-testid="stStatus"] > div:first-child > div:first-child > span:first-child { display: none !important; }

/* ── INVESTIGATE BUTTON — explicit visible styling ── */
.stButton > button {
    background-color: #1c1410 !important;
    color: #f0e8d0 !important;
    border: 2px solid #c4a96b !important;
    border-radius: 2px !important;
    padding: 0.55rem 1.5rem !important;
    font-family: 'Courier Prime', monospace !important;
    font-size: 0.88rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
    transition: all 0.2s ease !important;
    box-shadow: 3px 3px 0 #a0420e !important;
}
.stButton > button p,
.stButton > button span,
.stButton > button div {
    color: #f0e8d0 !important;
}
.stButton > button:hover {
    background-color: #a0420e !important;
    color: #f0e8d0 !important;
    transform: translate(-1px,-1px) !important;
    box-shadow: 4px 4px 0 #1c1410 !important;
}
.stButton > button:hover p,
.stButton > button:hover span,
.stButton > button:hover div { color: #f0e8d0 !important; }
/* Primary button (Investigate) same treatment */
.stButton > button[kind="primary"],
[data-testid="baseButton-primary"] {
    background-color: #1c1410 !important;
    color: #f0e8d0 !important;
}
[data-testid="baseButton-primary"] p,
[data-testid="baseButton-primary"] span,
[data-testid="baseButton-primary"] div { color: #f0e8d0 !important; }

/* ── TEXT INPUT ── */
.stTextInput input {
    background: #fffdf5 !important;
    border: 1px solid #c4a96b !important;
    border-radius: 1px !important;
    color: #1c1410 !important;
    font-family: 'Courier Prime', monospace !important;
    font-size: 1rem !important;
    padding: 0.6rem 1rem !important;
}
.stTextInput input::placeholder { color: #7a6e62 !important; font-style: italic; }
.stTextInput input:focus { border-color: #a0420e !important; outline: none !important; }

/* ── HEADINGS ── */
h1 { font-family:'UnifrakturMaguntia',cursive !important; font-size:3.2rem !important; color:#7a2200 !important; line-height:1.1 !important; text-shadow:3px 3px 0 rgba(160,66,14,0.28), 1px 1px 0 rgba(196,154,14,0.35); }
h2 { font-family:'IM Fell English',serif !important; font-style:italic !important; color:#8b3200 !important; border-bottom:2px solid #c4a96b !important; padding-bottom:0.3rem !important; }
h3 { font-family:'IM Fell English',serif !important; color:#3a1a00 !important; }

/* ── PROGRESS BAR ── */
.stProgress > div > div { background: #f0e8d0 !important; border:1px solid #c4a96b !important; border-radius:1px !important; }
.stProgress > div > div > div { background: linear-gradient(90deg,#a0420e,#c49a0e) !important; border-radius:1px !important; }

/* ── ALERT ── */
.stAlert { background: #f0e8d0 !important; border:1px solid #c4a96b !important; border-radius:2px !important; color:#1c1410 !important; }

/* ── EXPANDER ── */
[data-testid="stExpander"] { background:#fffdf5 !important; border:1px solid #c4a96b !important; border-radius:2px !important; }
[data-testid="stExpander"] summary { font-family:'IM Fell English',serif !important; color:#a0420e !important; font-style:italic !important; }
[data-testid="stExpander"] summary span { font-family:'IM Fell English',serif !important; color:#a0420e !important; font-style:italic !important; }
[data-testid="stExpander"] * { color: #1c1410 !important; }
/* FIX arro/arrow garbage in expander: icon span uses material icon ligature, reset to system font and hide */
[data-testid="stExpander"] summary svg,
[data-testid="stExpander"] summary > div > span:first-child,
[data-testid="stExpander"] summary > span:first-child { font-family: sans-serif !important; }
[data-testid="stExpander"] details > summary > div > span:not(:last-child):not([class*="label"]) { font-family: sans-serif !important; font-size: 0 !important; }

/* ── METRICS ── */
[data-testid="stMetric"] { background:#f0e8d0 !important; border:1px solid #c4a96b !important; border-radius:2px !important; padding:0.5rem !important; }
[data-testid="stMetricValue"] { color:#a0420e !important; font-family:'Libre Baskerville',serif !important; font-weight:700 !important; }
[data-testid="stMetricLabel"] { color:#5a4e42 !important; font-family:'Courier Prime',monospace !important; font-size:0.75rem !important; text-transform:uppercase !important; }

/* ── DOWNLOAD BUTTONS ── */
[data-testid="stDownloadButton"] > button { background:#f0e8d0 !important; color:#1c1410 !important; border:1px solid #c4a96b !important; border-radius:2px !important; font-family:'Courier Prime',monospace !important; }
[data-testid="stDownloadButton"] > button:hover { background:#1c1410 !important; color:#f0e8d0 !important; }

/* ── HIDE sidebar collapse button / back-arrow / chevron garbage ── */
[data-testid="collapsedControl"] { display: none !important; }
[data-testid="stSidebarCollapseButton"] { display: none !important; visibility: hidden !important; }
[data-testid="stSidebarCollapseButton"] > div,
[data-testid="stSidebarCollapseButton"] span,
[data-testid="stSidebarCollapseButton"] svg { display: none !important; }
button[aria-label="Close sidebar"],
button[aria-label="Open sidebar"],
button[aria-label="Collapse sidebar"] { display: none !important; }
.st-emotion-cache-1egp75f, .st-emotion-cache-czk5ss { display: none !important; }

/* ── SIDEBAR (intentionally dark — newspaper back page) ── */
section[data-testid="stSidebar"] {
    background: #1c1410 !important;
    background-image:
        radial-gradient(circle at 20% 80%, rgba(139,58,26,0.18) 0%, transparent 60%),
        radial-gradient(circle at 80% 20%, rgba(184,134,11,0.12) 0%, transparent 55%) !important;
    border-right: 3px double #c4a96b !important;
}
/* Sidebar text: light on dark intentionally */
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div,
section[data-testid="stSidebar"] label { color: #f0e8d0 !important; font-family:'Courier Prime',monospace !important; }
section[data-testid="stSidebar"] strong { color: #c4a96b !important; }
section[data-testid="stSidebar"] hr { border-color: #c4a96b !important; opacity:0.35 !important; }
section[data-testid="stSidebar"] .stSlider > div > div > div { background: #a0420e !important; }

/* ── MISC ── */
hr { border-color: #c4a96b !important; opacity:0.5 !important; }
.stCaption, .stCaption p, small { font-family:'Courier Prime',monospace !important; color:#5a4e42 !important; font-size:0.78rem !important; }

/* ══ CUSTOM COMPONENTS ══ */
.newspaper-masthead {
    text-align:center; padding:1.4rem 0 1.1rem;
    border-top:5px double #1c1410; border-bottom:5px double #1c1410;
    margin-bottom:1.5rem;
    background: linear-gradient(180deg, #fffef8 0%, #faf3e0 100%);
    box-shadow: 0 2px 16px rgba(140,90,20,0.12);
}
.masthead-dateline { font-family:'Courier Prime',monospace; font-size:0.75rem; letter-spacing:0.14em; text-transform:uppercase; color:#5a4e42; margin:0.4rem 0; }
.masthead-title { font-family:'UnifrakturMaguntia',cursive; font-size:4.2rem; line-height:1; color:#8b2800; text-shadow:3px 3px 0 rgba(160,66,14,0.3), 1px 1px 0 rgba(196,154,14,0.38); margin:0.3rem 0; }
.masthead-subtitle { font-family:'IM Fell English',serif; font-style:italic; font-size:1.05rem; color:#5a4e42; letter-spacing:0.08em; }
.masthead-price { font-family:'Courier Prime',monospace; font-size:0.72rem; color:#5a4e42; margin-top:0.4rem; letter-spacing:0.1em; text-transform:uppercase; }

.agent-step { background:#2a1f18; border:1px solid #c4a96b; border-left:4px solid #a0420e; padding:0.55rem 0.9rem; margin:0.35rem 0; font-family:'Courier Prime',monospace; font-size:0.82rem; border-radius:0 2px 2px 0; color:#f5e8d0 !important; }
.agent-step * { color:#f5e8d0 !important; }
.agent-step .sn { font-weight:700; color:#f0c060 !important; margin-right:0.3rem; }

.score-panel { border:2px double #c4a96b; border-radius:2px; padding:1.5rem; text-align:center; background:#2e1e14; background-image:radial-gradient(circle at 50% 50%,rgba(196,169,107,0.18) 0%,transparent 70%); margin-bottom:1rem; box-shadow:4px 4px 0 rgba(28,20,16,0.35); }
.score-label { font-family:'Courier Prime',monospace; font-size:0.7rem; letter-spacing:0.18em; text-transform:uppercase; color:#f0d878 !important; margin-bottom:0.4rem; }
.score-num { font-family:'UnifrakturMaguntia',cursive; font-size:4rem; line-height:1; margin:0.2rem 0; color:#ffe566 !important; text-shadow: 0 0 24px rgba(255,220,60,0.7), 0 0 8px rgba(255,180,40,0.5), 2px 2px 0 rgba(0,0,0,0.7); }
.score-denom { font-family:'Courier Prime',monospace; font-size:0.78rem; color:#e8d080 !important; }
.score-panel * { color: #f0d878 !important; }

.newsletter-body-wrap { background:#fffdf5; border:1px solid #c4a96b; border-top:3px double #1c1410; padding:1.8rem 2.2rem; font-size:0.95rem; line-height:1.85; box-shadow:4px 4px 0 rgba(28,20,16,0.1); font-family:'Libre Baskerville',serif; margin-top:0.5rem; color:#1c1410; }
.newsletter-body-wrap p, .newsletter-body-wrap span, .newsletter-body-wrap li { color:#1c1410 !important; }

.decorative-rule { display:flex; align-items:center; gap:0.6rem; margin:1rem 0; color:#c4a96b; font-size:1rem; }
.decorative-rule::before,.decorative-rule::after { content:''; flex:1; border-top:1px solid #c4a96b; }
</style>
""",
    unsafe_allow_html=True,
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
<div style="text-align:center;padding:1rem 0 0.5rem;">
    <div style="font-size:2.8rem;margin-bottom:0.3rem;">🔍</div>
    <div style="font-family:'IM Fell English',serif;font-size:1.25rem;color:#c4a96b;font-style:italic;">The Intelligence Desk</div>
    <div style="font-family:'Courier Prime',monospace;font-size:0.66rem;letter-spacing:0.14em;text-transform:uppercase;color:#6b5f52;margin-top:0.3rem;">◆ Configuration Bureau ◆</div>
</div>
<hr style="border-color:#c4a96b;opacity:0.3;margin:0.5rem 0 1rem;">
""", unsafe_allow_html=True)

    num_stories = st.slider("Stories to Fetch", min_value=6, max_value=18, value=12, step=3)

    st.markdown("""
<hr style="border-color:#c4a96b;opacity:0.25;margin:1rem 0;">
<div style="font-family:'IM Fell English',serif;font-size:1.05rem;color:#c4a96b;font-style:italic;margin-bottom:0.7rem;">◆ The Investigative Pipeline</div>
<div class="agent-step"><span class="sn">I.</span>🔍 Story Researcher<br><span style="font-size:0.72rem;color:#c8a87a;">Dispatches queries via Tavily</span></div>
<div class="agent-step"><span class="sn">II.</span>🗂 Grouping Agent<br><span style="font-size:0.72rem;color:#c8a87a;">Clusters into themed dossiers</span></div>
<div class="agent-step"><span class="sn">III.</span>✍ Newsletter Writer<br><span style="font-size:0.72rem;color:#c8a87a;">Composes the final edition</span></div>
<div class="agent-step"><span class="sn">IV.</span>⚖ Quality Judge<br><span style="font-size:0.72rem;color:#c8a87a;">Evaluates &amp; scores the work</span></div>
<hr style="border-color:#c4a96b;opacity:0.25;margin:1rem 0;">
<div style="font-family:'IM Fell English',serif;font-size:1.05rem;color:#c4a96b;font-style:italic;margin-bottom:0.6rem;">◆ Equipment Used</div>
<div style="font-family:'Courier Prime',monospace;font-size:0.78rem;line-height:2.0;color:#e0d0b8;">
▸ LLM &nbsp;&nbsp;&nbsp;&nbsp;· Gemini 1.5 Flash<br>
▸ Search &nbsp;· Tavily API<br>
▸ UI &nbsp;&nbsp;&nbsp;&nbsp;· Streamlit<br>
▸ Deploy &nbsp;· Railway
</div>
<hr style="border-color:#c4a96b;opacity:0.25;margin:1rem 0;">
<div style="font-family:'Courier Prime',monospace;font-size:0.68rem;color:#a09080;text-align:center;line-height:1.8;">
Semester IV · B.E. ECE<br>Agentic AI Project
</div>
""", unsafe_allow_html=True)

# ── Masthead ──────────────────────────────────────────────────────────────────
from datetime import datetime
today = datetime.now().strftime("%A, %d %B %Y").upper()

st.markdown(f"""
<div class="newspaper-masthead">
    <div class="masthead-dateline">✦ &nbsp; {today} &nbsp; ✦ &nbsp; · · · &nbsp; Established 2025 &nbsp; · · · &nbsp; Vol. I</div>
    <div style="border-top:2px solid #1c1410;opacity:0.5;margin:0.4rem 0;"></div>
    <div class="masthead-title">The Curator</div>
    <div style="border-top:2px solid #1c1410;opacity:0.5;margin:0.4rem 0;"></div>
    <div class="masthead-subtitle">Intelligence Dispatches &nbsp;·&nbsp; Multi-Agent Research &amp; Composition Bureau</div>
    <div class="masthead-price">🔍 &nbsp; Powered by Tavily Search &amp; Gemini 1.5 Flash &nbsp;·&nbsp; Price: One Good Query</div>
</div>
""", unsafe_allow_html=True)

# ── Input ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="decorative-rule">🔍&nbsp; Submit Your Inquiry &nbsp;🔍</div>', unsafe_allow_html=True)

col_input, col_btn = st.columns([4, 1])
with col_input:
    topic = st.text_input(
        "Topic:",
        placeholder="e.g.  Artificial Intelligence  ·  Climate Tech  ·  Space Exploration  ·  Web3",
        label_visibility="collapsed",
    )
with col_btn:
    generate = st.button("⬥ Investigate", type="primary", use_container_width=True)

st.markdown("<hr style='border-color:#c4a96b;opacity:0.4;margin:0.8rem 0;'>", unsafe_allow_html=True)

# ── Pipeline ──────────────────────────────────────────────────────────────────
if generate and topic.strip():
    topic = topic.strip()

    st.markdown(f"""
<div style="font-family:'IM Fell English',serif;font-style:italic;font-size:1.05rem;
     color:#8b3a1a;background:#e8dfc8;border:1px solid #c4a96b;
     padding:0.65rem 1.2rem;border-radius:2px;margin:0.5rem 0 1rem;">
    🔍 &nbsp; Now investigating: <strong>"{topic}"</strong> — Dispatching agents to the field…
</div>
""", unsafe_allow_html=True)

    progress_bar = st.progress(0, text="Opening case file…")

    with st.status("🔍 Agent I — Story Researcher · Querying Tavily…", expanded=True) as s1:
        stories = research_stories(topic, num_stories)
        st.write(f"✅ Recovered **{len(stories)} dispatches** across 3 intelligence queries")
        if stories:
            st.write(f"First lead: *{stories[0]['title']}*")
        s1.update(label=f"✅ Agent I complete — {len(stories)} stories recovered", state="complete")

    progress_bar.progress(30, text="Grouping intelligence…")

    with st.status("🗂 Agent II — Grouping Agent · Clustering into dossiers…", expanded=True) as s2:
        grouped = group_stories(stories)
        theme_names = list(grouped.keys())
        st.write(f"✅ Filed into **{len(theme_names)} dossiers**: {' · '.join(theme_names)}")
        s2.update(label=f"✅ Agent II complete — {len(theme_names)} dossiers assembled", state="complete")

    progress_bar.progress(55, text="Composing edition…")

    with st.status("✍ Agent III — Newsletter Writer · Composing the edition…", expanded=True) as s3:
        newsletter = write_newsletter(topic, grouped)
        word_count = len(newsletter["body"].split())
        st.write(f"✅ Edition drafted — **{word_count} words** committed to press")
        st.write(f"Headline: *{newsletter['subject_line']}*")
        s3.update(label="✅ Agent III complete — Edition ready for press", state="complete")

    progress_bar.progress(80, text="Quality examination…")

    with st.status("⚖ LLM Judge · Examining quality under the lens…", expanded=True) as sj:
        evaluation = evaluate_newsletter(newsletter["body"], topic)
        score = evaluation.get("overall_score", "N/A")
        st.write(f"✅ Examination complete — Verdict: **{score}/10** {evaluation.get('verdict_emoji', '')}")
        sj.update(label=f"✅ Judge complete — {score}/10", state="complete")

    progress_bar.progress(100, text="Case closed.")

    st.markdown("""
<div style="background:#e8f5e1;border:1px solid #6a9a4a;border-radius:2px;
     padding:0.65rem 1.2rem;font-family:'IM Fell English',serif;font-style:italic;
     font-size:1.0rem;color:#3a6a25;margin:0.5rem 0 1.2rem;">
    ✦ &nbsp; The investigation is complete. Your edition has been composed and examined.
</div>
""", unsafe_allow_html=True)

    st.markdown("<hr style='border-color:#c4a96b;opacity:0.5;'>", unsafe_allow_html=True)

    left_col, right_col = st.columns([3, 2])

    with left_col:
        st.markdown("## 📰 Your Edition")

        subject = newsletter['subject_line']
        st.markdown(f"""
<div style="background:#e8dfc8;border:1px solid #c4a96b;border-left:4px solid #8b3a1a;
     padding:0.75rem 1.2rem;border-radius:0 2px 2px 0;margin-bottom:0.6rem;
     font-family:'Courier Prime',monospace;">
    <span style="font-size:0.66rem;letter-spacing:0.14em;text-transform:uppercase;color:#6b5f52;">✉ Subject Headline</span><br>
    <span style="font-family:'IM Fell English',serif;font-size:1.1rem;font-style:italic;color:#1c1410;">{subject}</span>
</div>
""", unsafe_allow_html=True)

        newsletter_body_html = newsletter["body"].replace('\n', '<br>')
        st.markdown(f'<div class="newsletter-body-wrap">{newsletter["body"]}</div>', unsafe_allow_html=True)

        st.markdown("<div style='height:0.7rem'></div>", unsafe_allow_html=True)
        dl1, dl2 = st.columns(2)
        with dl1:
            st.download_button(
                label="⬇ Download · Markdown",
                data=newsletter["body"],
                file_name=f"newsletter_{topic.replace(' ', '_').lower()}.md",
                mime="text/markdown",
                use_container_width=True,
            )
        with dl2:
            full_text = f"Subject: {newsletter['subject_line']}\n\n{newsletter['body']}"
            st.download_button(
                label="⬇ Download · Plain Text",
                data=full_text,
                file_name=f"newsletter_{topic.replace(' ', '_').lower()}.txt",
                mime="text/plain",
                use_container_width=True,
            )

    with right_col:
        st.markdown("## ⚖ The Judge's Verdict")

        score_val = evaluation.get("overall_score", 0)
        try:
            score_num = float(score_val)
            score_color = "#5a9a3a" if score_num >= 7 else "#c47a20" if score_num >= 5 else "#b03a2a"
        except (ValueError, TypeError):
            score_color = "#8b7355"

        verdict_emoji = evaluation.get('verdict_emoji', '⚖')
        st.markdown(f"""
<div class="score-panel">
    <div class="score-label">⚖ &nbsp; Overall Verdict &nbsp; ⚖</div>
    <div class="score-num" style="color:{score_color};">{score_val}</div>
    <div class="score-denom">out of 10 possible marks</div>
    <div style="font-size:1.6rem;margin-top:0.5rem;">{verdict_emoji}</div>
</div>
""", unsafe_allow_html=True)

        if evaluation.get("strengths"):
            st.markdown(f"""
<div style="background:#e4f5d8;border:1px solid #6a9a4a;border-radius:2px;
     padding:0.75rem 1rem;margin:0.5rem 0;font-family:'Courier Prime',monospace;font-size:0.85rem;color:#1c2e10;">
    <strong style="color:#2d6010;font-size:0.88rem;">💪 Strengths noted:</strong><br>
    <span style="color:#1c2e10;line-height:1.7;">{evaluation['strengths']}</span>
</div>
""", unsafe_allow_html=True)

        if evaluation.get("improvements"):
            st.markdown(f"""
<div style="background:#fdf0d8;border:1px solid #c4a96b;border-radius:2px;
     padding:0.75rem 1rem;margin:0.5rem 0;font-family:'Courier Prime',monospace;font-size:0.85rem;color:#3a2200;">
    <strong style="color:#7a3e00;font-size:0.88rem;">🎯 Recommendations:</strong><br>
    <span style="color:#3a2200;line-height:1.7;">{evaluation['improvements']}</span>
</div>
""", unsafe_allow_html=True)

        st.markdown('<div class="decorative-rule" style="font-size:0.78rem;margin:0.8rem 0;color:#c4a96b;">Section Examination</div>', unsafe_allow_html=True)

        for section in evaluation.get("sections", []):
            with st.expander(f"📄 {section.get('section_name', 'Section')}"):
                m1, m2, m3 = st.columns(3)
                m1.metric("Accuracy", f"{section.get('accuracy', '-')}/5")
                m2.metric("Engagement", f"{section.get('engagement', '-')}/5")
                m3.metric("Clarity", f"{section.get('clarity', '-')}/5")
                sec_score = section.get("section_score", "")
                if sec_score:
                    st.progress(float(sec_score) / 10, text=f"Section score: {sec_score}/10")
                st.caption(f"💬 {section.get('feedback', '')}")

        if evaluation.get("summary"):
            st.markdown(f"""
<div style="background:#e8dfc8;border:1px solid #c4a96b;border-radius:2px;
     padding:0.65rem 1rem;font-family:'Courier Prime',monospace;font-size:0.8rem;
     font-style:italic;color:#4a3f35;margin-top:0.5rem;">
    📋 {evaluation['summary']}
</div>
""", unsafe_allow_html=True)

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        st.markdown("## 🔍 Source Dossiers")
        for theme, theme_stories in grouped.items():
            with st.expander(f"◆ {theme} &nbsp;({len(theme_stories)} dispatches)"):
                for s in theme_stories:
                    st.markdown(f"**{s['title']}**")
                    st.caption(s["snippet"])
                    st.markdown(f"[Read full dispatch →]({s['url']})")
                    st.markdown("<hr style='border-color:#c4a96b;opacity:0.3;margin:0.5rem 0;'>", unsafe_allow_html=True)

elif generate and not topic.strip():
    st.markdown("""
<div style="background:#fdf3e3;border:1px solid #c4a96b;border-left:4px solid #8b3a1a;
     padding:0.65rem 1.2rem;border-radius:0 2px 2px 0;
     font-family:'Courier Prime',monospace;font-size:0.86rem;">
    ⚠ &nbsp;<strong>No inquiry submitted.</strong> The bureau requires a topic before dispatching agents.
</div>
""", unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<hr style="border-color:#c4a96b;opacity:0.5;margin:2rem 0 0.8rem;">
<div style="text-align:center;font-family:'Courier Prime',monospace;font-size:0.7rem;
     color:#8b7355;letter-spacing:0.08em;padding-bottom:1rem;">
    ✦ &nbsp; The Curator Intelligence Bureau &nbsp;·&nbsp; Semester IV · B.E. ECE &nbsp;·&nbsp;
    Streamlit &nbsp;·&nbsp; Tavily &nbsp;·&nbsp; Gemini 1.5 Flash &nbsp; ✦
</div>
""", unsafe_allow_html=True)
