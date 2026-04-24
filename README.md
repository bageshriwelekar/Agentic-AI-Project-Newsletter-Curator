# 📰 Newsletter Curator Agent

> A multi-agent AI system that researches, groups, writes, and evaluates a weekly newsletter on any topic — fully automated.

**Live Demo:** [your-railway-url-here]

---

## 🎯 Problem Statement

Busy professionals, students, and content creators waste hours every week manually finding, filtering, and summarising the internet's top stories on their chosen niche. There is no automated way to get a polished, themed, publication-ready newsletter draft with zero manual effort.

**Who:** Anyone who wants a curated weekly digest on a specific topic.  
**Need:** Auto-generate a formatted newsletter from the web's latest stories.  
**Why Agentic:** A single chatbot can't search the web, make thematic decisions, write editorial copy, AND self-evaluate quality in a coordinated pipeline. This requires multiple specialised agents working in sequence.

---

## 🤖 Agent Architecture

### Agent 1 — Story Researcher
| | |
|---|---|
| **Input** | User topic string + desired story count |
| **Action** | Calls Tavily Search API with 3 query variants; deduplicates results |
| **Output** | `List[dict]` — `{title, url, snippet, published_date}` |

### Agent 2 — Grouping Agent
| | |
|---|---|
| **Input** | Raw story list from Agent 1 |
| **Action** | Sends stories to Gemini LLM; asks it to cluster into 3–5 themes |
| **Output** | `Dict[str, List[dict]]` — `{theme_name: [story, story, ...]}` |

### Agent 3 — Newsletter Writer
| | |
|---|---|
| **Input** | Topic + grouped stories dict from Agent 2 |
| **Action** | Gemini drafts a full newsletter: subject line, intro, section blurbs, CTA |
| **Output** | `Dict` — `{subject_line: str, body: str (markdown)}` |

### LLM-as-Judge
| | |
|---|---|
| **Input** | Newsletter body from Agent 3 |
| **Action** | Gemini evaluates each section on Accuracy/Engagement/Clarity rubric |
| **Output** | `Dict` — scores, per-section feedback, overall rating |

---

## 🏗️ Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Streamlit UI                            │
│              User enters topic → clicks Generate            │
└─────────────────────────┬───────────────────────────────────┘
                          │ topic string
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              Agent 1: Story Researcher                      │
│   3 × Tavily Search queries → deduplicate → top 12 stories  │
│   Tool: Tavily Search API                                   │
└─────────────────────────┬───────────────────────────────────┘
                          │ List[story dicts]
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              Agent 2: Grouping Agent                        │
│   Gemini LLM → clusters stories into 3–5 named themes      │
│   Tool: Gemini 1.5 Flash                                    │
└─────────────────────────┬───────────────────────────────────┘
                          │ Dict{theme: [stories]}
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              Agent 3: Newsletter Writer                     │
│   Gemini LLM → drafts subject line + full markdown body    │
│   Tool: Gemini 1.5 Flash                                    │
└─────────────────────────┬───────────────────────────────────┘
                          │ {subject_line, body}
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              LLM-as-Judge Evaluator                         │
│   Gemini LLM → scores Accuracy / Engagement / Clarity      │
│   Returns: overall score, section scores, feedback          │
└─────────────────────────┬───────────────────────────────────┘
                          │ evaluation dict
                          ▼
┌─────────────────────────────────────────────────────────────┐
│   Streamlit UI — displays newsletter + scores to user       │
│   Download buttons: .md and .txt export                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11+ |
| UI | Streamlit |
| Search Tool | Tavily Search API |
| LLM | Gemini 1.5 Flash (Google AI Studio) |
| Deployment | Railway |
| Video | Loom |

---

## 🚀 Run Locally

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/newsletter-curator.git
cd newsletter-curator
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up API keys
```bash
cp .env.example .env
# Edit .env and add your keys:
# TAVILY_API_KEY=tvly-...
# GEMINI_API_KEY=AIza...
```

Get your keys:
- **Tavily**: [tavily.com](https://tavily.com) → Sign Up → API Keys
- **Gemini**: [aistudio.google.com](https://aistudio.google.com) → Get API Key

### 4. Run
```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

---

## ☁️ Deploy to Railway

1. Push this repo to GitHub
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
3. Select this repository
4. Add environment variables in Railway dashboard:
   - `TAVILY_API_KEY` = your key
   - `GEMINI_API_KEY` = your key
5. Deploy → Railway auto-detects `railway.toml` and runs the app

---

## 📁 Project Structure

```
newsletter-curator/
├── agents/
│   ├── __init__.py
│   ├── researcher.py    # Agent 1 — Tavily search
│   ├── grouper.py       # Agent 2 — Gemini theme clustering
│   ├── writer.py        # Agent 3 — Gemini newsletter draft
│   └── judge.py         # LLM-as-Judge — quality evaluation
├── app.py               # Streamlit UI + pipeline orchestration
├── requirements.txt
├── railway.toml         # Railway deployment config
├── Procfile
├── .env.example
├── .gitignore
└── README.md
```

---

## 📊 Evaluation Rubric (LLM-as-Judge)

| Criterion | Scale | Description |
|---|---|---|
| Accuracy | 1–5 | Facts correct, no hallucinations, sources credible |
| Engagement | 1–5 | Compelling writing, reader wants to keep reading |
| Clarity | 1–5 | Well-structured, easy to understand, no unnecessary jargon |
| Overall | /10 | Weighted composite of all sections |

---

## 👥 Team

| Role | Responsibility |
|---|---|
| **Role A — Architect & Integrator** | Problem definition, task decomposition, architecture diagram, API integrations |
| **Role B — Builder & Deployer** | Agent implementation, LLM-as-Judge, Streamlit UI, Railway deployment, Loom video |

---

## 🎬 Demo Video

[Watch on Loom](https://loom.com/your-video-link)

---

*Semester IV · B.E. Electronics & Communication · Introduction to Agentic AI Systems*
