import os
import time

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def write_newsletter(topic: str, grouped_stories: dict) -> dict:
    if not grouped_stories:
        return {
            "subject_line": f"Your Weekly {topic} Digest",
            "body": "No stories were found.",
        }

    try:
        sections_text = ""
        for theme, stories in grouped_stories.items():
            sections_text += f"\n\n## {theme}\n"
            for s in stories:
                sections_text += (
                    f"- **{s['title']}** | {s['published_date']}\n"
                    f"  {s['snippet']}\n"
                    f"  [Read →]({s['url']})\n"
                )

        prompt = f"""You are a top-tier newsletter writer.
Write a weekly newsletter for the topic: "{topic}".

{sections_text}

Instructions:
1. First line: SUBJECT: <catchy subject line>
2. Then full newsletter in markdown:
   - Warm 2-sentence intro
   - One section per theme (## headings)
   - 2-3 sentence editorial blurb per section
   - Include story links inline
   - Short friendly sign-off with call-to-action

Tone: Informative, conversational, slightly witty.
Length: 350-500 words."""

        time.sleep(3)
        response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        full_text = response.text.strip()

        lines = full_text.split("\n")
        subject_line = f"Your Weekly {topic} Digest"
        body_start = 0

        for i, line in enumerate(lines):
            if line.strip().upper().startswith("SUBJECT:"):
                subject_line = line.strip()[8:].strip()
                body_start = i + 1
                break

        body = "\n".join(lines[body_start:]).strip()
        return {"subject_line": subject_line, "body": body}

    except Exception as e:
        print(f"[Writer] Error: {e}")
        fallback_body = f"# Your Weekly {topic} Digest\n\n"
        for theme, stories in grouped_stories.items():
            fallback_body += f"## {theme}\n\n"
            for s in stories:
                fallback_body += f"- [{s['title']}]({s['url']})\n"
            fallback_body += "\n"
        return {
            "subject_line": f"Your Weekly {topic} Digest",
            "body": fallback_body,
        }