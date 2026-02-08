from utils.llm_client import ask_text
from modules.feedback import get_top_prompts


def _map_energy(val):
    if val <= 20: return "quiet, minimal, ambient, whisper-soft, ~60 BPM"
    if val <= 40: return "gentle, relaxed, easy-going, mellow, ~80 BPM"
    if val <= 60: return "moderate energy, steady, flowing, ~100 BPM"
    if val <= 80: return "energetic, driving, powerful, upbeat, ~120 BPM"
    return "intense, explosive, soaring, maximum energy, ~140 BPM"


def _map_style(val):
    if val <= 20: return "minimal, sparse, solo instrument, intimate bedroom recording"
    if val <= 40: return "indie pop, clean guitar, light drums, warm synth pads"
    if val <= 60: return "polished pop-rock, piano and strings, balanced mix, studio quality"
    if val <= 80: return "cinematic, orchestral swell, wide stereo, dramatic full strings"
    return "epic orchestral, massive choir, soaring brass, blockbuster soundtrack"


def _map_warmth(val):
    if val <= 20: return "deep bass, rich low-end, dark and moody tone"
    if val <= 40: return "warm, smooth, round tone, gentle reverb"
    if val <= 60: return "natural, balanced tone, clear and open"
    if val <= 80: return "bright, crisp, shimmering, airy highs"
    return "crystalline, sparkling, ultra-bright, electronic sheen"


def _map_arc(val):
    if val <= 20: return "steady, unchanging, ambient loop, constant, flat dynamics"
    if val <= 40: return "gentle variation, subtle breathing, light swell"
    if val <= 60: return "evolving, verse-chorus, moderate build"
    if val <= 80: return "building, rising intensity, crescendo, climax"
    return "starts quiet, massive build, explosive climax, drop"


def create_music_prompt(final_profile):
    """Convert a final_profile dict into a vivid MusicGen prompt string."""
    emotion = final_profile.get("emotion", "neutral")
    energy_desc = _map_energy(final_profile.get("energy", 50))
    style_desc = _map_style(final_profile.get("style", 50))
    warmth_desc = _map_warmth(final_profile.get("warmth", 50))
    arc_desc = _map_arc(final_profile.get("arc", 50))

    # Get top-rated past prompts for few-shot learning
    past_examples = get_top_prompts(emotion)
    few_shot = ""
    if past_examples:
        few_shot = "\n\nHere are prompts that scored well for similar emotions — use them as inspiration:\n"
        for ex in past_examples[:3]:
            few_shot += f'- "{ex}"\n'

    prompt = f"""You are a music director creating a prompt for an AI music generator.

Given this emotional profile:
- Emotion: {emotion}
- Energy: {final_profile.get("energy", 50)}/100 → {energy_desc}
- Style: {final_profile.get("style", 50)}/100 → {style_desc}
- Warmth: {final_profile.get("warmth", 50)}/100 → {warmth_desc}
- Arc: {final_profile.get("arc", 50)}/100 → {arc_desc}
{few_shot}
Write a vivid 2-3 sentence music generation prompt that blends ALL of these qualities naturally. Include specific instruments, tempo feel, production style, and structural arc.

The listener's dominant emotion is "{emotion}" — the music should honor that feeling.

Output ONLY the prompt text. No labels, no JSON, no explanation."""

    return ask_text(prompt)
