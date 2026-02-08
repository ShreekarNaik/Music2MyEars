from utils.llm_client import ask_json
from modules.feedback import get_learned_defaults


def fuse_emotions(mood_list):
    """Merge mood signals into one ai_profile with 4 slider dimensions."""
    sources = [m.get("source", "unknown") for m in mood_list]

    mood_descriptions = "\n".join(
        f"- Source: {m.get('source')}, Moods: {m.get('moods', [m.get('mood')])}, Energy: {m.get('energy')}"
        for m in mood_list
    )

    prompt = f"""You are an emotion analyst for a music generation system.

Given these mood signals from user inputs:
{mood_descriptions}

Produce ONE unified emotional profile as JSON:
{{
  "emotions": ["<list of 1-3 detected emotions, most dominant first>"],
  "emotion": "<single most dominant emotion>",
  "energy": <0-100 integer>,
  "style": <0-100 integer, 0=minimal sparse, 100=cinematic epic>,
  "warmth": <0-100 integer, 0=deep dark moody, 100=bright sparkling>,
  "arc": <0-100 integer, 0=steady constant, 100=big dramatic build>
}}

Rules:
- Blend ALL detected emotions into the slider values, not just the dominant one
- "sad but hopeful" → moderate energy (hope lifts it), warm style, gentle build arc
- "angry and frustrated" → high energy, bright/harsh warmth, big build
- "peaceful and grateful" → low energy, warm, steady arc
- The slider values should reflect the MIX of emotions, not just the dominant one
- Base values on the actual emotional content, not random guesses

Return ONLY the JSON object."""

    result = ask_json(prompt)
    result["sources"] = sources

    # Apply learned defaults — blend with Gemini's values instead of overwriting
    learned = get_learned_defaults(result.get("emotion", ""))
    if learned:
        for key in ["energy", "style", "warmth", "arc"]:
            if key in learned and key in result:
                result[key] = round((result[key] + learned[key]) / 2)

    return result
