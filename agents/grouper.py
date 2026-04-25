"""
Agent 2: Grouping Agent
=======================
Input  : List of story dicts from Agent 1
Action : Uses Gemini LLM to cluster stories into 3–5 meaningful themes
Output : Dict mapping theme names to lists of story dicts
"""
import json
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def group_stories(stories: list[dict]) -> dict:
    if not stories:
        return {"General": []}
    try:
        stories_text = "\n".join(
            [
                f"[{i}] Title: {s['title']}\n    Snippet: {s['snippet']}"
                for i, s in enumerate(stories)
            ]
        )
        prompt = f"""You are a professional newsletter editor.
Analyse the stories below and group them into 3 to 5 distinct, meaningful themes
suitable for newsletter sections.
Stories:
{stories_text}
Rules:
- Every story index must appear in exactly one theme.
- Theme names should be short (2-5 words), punchy, and reader-friendly.
- Return ONLY valid JSON. No markdown fences. No extra text.
Format:
{{
  "Theme Name One": [0, 3, 5],
  "Theme Name Two": [1, 2],
  "Theme Name Three": [4, 6, 7]
}}"""
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        raw = response.text.strip().replace("```json", "").replace("```", "")
        theme_indices = json.loads(raw)
        grouped = {}
        for theme, indices in theme_indices.items():
            theme_stories = [stories[i] for i in indices if i < len(stories)]
            if theme_stories:
                grouped[theme] = theme_stories
        return grouped if grouped else {"All Stories": stories}
    except json.JSONDecodeError as e:
        print(f"[Grouper] JSON parse error: {e}")
        n = len(stories)
        third = max(1, n // 3)
        return {
            "Top Stories": stories[:third],
            "Industry News": stories[third : 2 * third],
            "Trending Now": stories[2 * third :],
        }
    except Exception as e:
        print(f"[Grouper] Error: {e}")
        return {"All Stories": stories}