import json
import os
import time

from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def evaluate_newsletter(newsletter_body: str, topic: str = "") -> dict:
    if not newsletter_body or len(newsletter_body) < 50:
        return {
            "overall_score": 0,
            "sections": [],
            "summary": "Newsletter body was empty or too short to evaluate.",
            "verdict_emoji": "❌ Needs Work",
        }

    try:
        prompt = f"""You are a strict but fair newsletter quality evaluator.

Topic: "{topic}"

Evaluate the newsletter below against this rubric for EACH section (## headings):

RUBRIC:
- accuracy   (1-5): Are facts presented correctly?
- engagement (1-5): Is it compelling?
- clarity    (1-5): Is it well-structured?

Newsletter:
{newsletter_body}

Return ONLY valid JSON. No markdown. No extra text:
{{
  "overall_score": 8.2,
  "verdict": "Strong",
  "sections": [
    {{
      "section_name": "Exact theme heading",
      "accuracy": 4,
      "engagement": 5,
      "clarity": 4,
      "section_score": 8.7,
      "feedback": "One actionable sentence."
    }}
  ],
  "strengths": "One sentence about what the newsletter does well.",
  "improvements": "One sentence about what could be improved.",
  "summary": "Two-sentence overall assessment."
}}"""

        time.sleep(5)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        raw = response.text.strip().replace("```json", "").replace("```", "")

        evaluation = json.loads(raw)

        score = float(evaluation.get("overall_score", 0))
        if score >= 8:
            evaluation["verdict_emoji"] = "🏆 Excellent"
        elif score >= 6:
            evaluation["verdict_emoji"] = "✅ Good"
        elif score >= 4:
            evaluation["verdict_emoji"] = "⚠️ Average"
        else:
            evaluation["verdict_emoji"] = "❌ Needs Work"

        return evaluation

    except json.JSONDecodeError:
        return {
            "overall_score": "N/A",
            "sections": [],
            "summary": "Evaluation could not be parsed.",
            "verdict_emoji": "⚠️ Parse Error",
            "strengths": "",
            "improvements": "",
        }

    except Exception as e:
        return {
            "overall_score": "N/A",
            "sections": [],
            "summary": f"Evaluation failed: {str(e)}",
            "verdict_emoji": "⚠️ Error",
            "strengths": "",
            "improvements": "",
        }