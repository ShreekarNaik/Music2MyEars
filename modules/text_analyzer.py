from utils.llm_client import ask_json


def analyze_text(text):
    """Analyze text input and return mood dict."""
    prompt = f"""Analyze the following text for its emotional content.
Return ONLY a JSON object with these keys:
- summary: one sentence summary
- moods: a list of 1-3 emotion words detected (most dominant first)
- mood: the single most dominant mood (first item from moods)
- energy: float 0.0 to 1.0 (0=very calm, 1=very intense)

Example: "I'm sad but grateful for the memories" →
{{"summary": "Bittersweet reflection on past", "moods": ["melancholic", "grateful", "reflective"], "mood": "melancholic", "energy": 0.3}}

Text: "{text}"

Return ONLY valid JSON, no other text."""

    result = ask_json(prompt)
    result["source"] = "text"
    return result
