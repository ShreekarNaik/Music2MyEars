from utils.llm_client import ask_text
from modules.feedback import (
    get_top_prompts,
    get_negative_examples,
    get_emotion_profile,
    get_learned_rules,
)


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


def _build_knowledge_context(emotion):
    """Assemble learned knowledge for injection into prompt generation."""
    sections = []

    # Positive examples (few-shot)
    top_prompts = get_top_prompts(emotion)
    if top_prompts:
        sections.append(
            "Prompts that scored well for this emotion — use as inspiration:\n"
            + "\n".join(f'- "{p}"' for p in top_prompts[:3])
        )

    # Negative examples (anti-patterns)
    bad_prompts = get_negative_examples(emotion)
    if bad_prompts:
        sections.append(
            "Prompts that scored POORLY — AVOID these patterns:\n"
            + "\n".join(f'- "{p}"' for p in bad_prompts[:3])
        )

    # Per-emotion principles from reflection
    emo_profile = get_emotion_profile(emotion)
    if emo_profile:
        principles = emo_profile.get("prompt_principles", [])
        if principles:
            sections.append(
                f"Learned principles for \"{emotion}\":\n"
                + "\n".join(f"- {p}" for p in principles[:3])
            )
        anti = emo_profile.get("anti_patterns", [])
        if anti:
            sections.append(
                f"Anti-patterns for \"{emotion}\" (avoid these):\n"
                + "\n".join(f"- {a}" for a in anti[:3])
            )

    # Global rules from reflection
    rules = get_learned_rules()
    global_rules = rules.get("global_rules", {})
    pos = global_rules.get("positive", [])
    neg = global_rules.get("negative", [])
    if pos:
        sections.append(
            "General rules for good music prompts:\n"
            + "\n".join(f"- {r}" for r in pos[:3])
        )
    if neg:
        sections.append(
            "General patterns to avoid:\n"
            + "\n".join(f"- {r}" for r in neg[:3])
        )

    return "\n\n".join(sections)


def create_music_prompt(final_profile):
    """Convert a final_profile dict into a vivid MusicGen prompt string."""
    emotion = final_profile.get("emotion", "neutral")
    energy_desc = _map_energy(final_profile.get("energy", 50))
    style_desc = _map_style(final_profile.get("style", 50))
    warmth_desc = _map_warmth(final_profile.get("warmth", 50))
    arc_desc = _map_arc(final_profile.get("arc", 50))

    # Build knowledge context from feedback loop
    knowledge = _build_knowledge_context(emotion)
    knowledge_block = f"\n\n{knowledge}" if knowledge else ""

    prompt = f"""You are a music director creating a prompt for an AI music generator.

Given this emotional profile:
- Emotion: {emotion}
- Energy: {final_profile.get("energy", 50)}/100 → {energy_desc}
- Style: {final_profile.get("style", 50)}/100 → {style_desc}
- Warmth: {final_profile.get("warmth", 50)}/100 → {warmth_desc}
- Arc: {final_profile.get("arc", 50)}/100 → {arc_desc}
{knowledge_block}
Write a vivid 2-3 sentence music generation prompt that blends ALL of these qualities naturally. Include specific instruments, tempo feel, production style, and structural arc.

The listener's dominant emotion is "{emotion}" — the music should honor that feeling.

Output ONLY the prompt text. No labels, no JSON, no explanation."""

    return ask_text(prompt)
