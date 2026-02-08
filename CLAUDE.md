# CLAUDE.md — Project Context for Claude Code Sessions

## What This Project Is
Music2MyEars — a Streamlit app that turns text, images, and voice into AI-generated music based on detected emotions. Built for the HackNation VC Track challenge.

## Tech Stack
- **Streamlit** — UI (app.py)
- **Google Gemini 2.0 Flash** — Text/image emotion analysis, prompt generation, reflection engine
- **OpenAI Whisper (base)** — Voice-to-text transcription
- **MusicGen (facebook/musicgen-small)** — Local music generation via transformers
- **Plotly** — Pipeline visualization chart
- **ffmpeg** — Required system dependency for Whisper

## Module Map

| Module | File | Does |
|--------|------|------|
| UI | `app.py` | Streamlit app — columns for image/voice, duration picker, sliders, A/B comparison, "What I've learned" panel, user notes, Plotly explainer |
| Text Analyzer | `modules/text_analyzer.py` | Gemini text emotion → {moods[], mood, energy, source} |
| Image Analyzer | `modules/image_analyzer.py` | Gemini vision → {caption, moods[], mood, energy, source} |
| Voice Analyzer | `modules/voice_analyzer.py` | Whisper transcription + Gemini mood → {transcript, moods[], mood, energy, source} |
| Emotion Fuser | `modules/emotion_fuser.py` | Merges multi-source moods into one profile, range-clamped by learned knowledge |
| Music Orchestrator | `modules/music_orchestrator.py` | Converts profile → vivid MusicGen prompt via Gemini |
| Music Generator | `modules/music_generator.py` | Batched MusicGen — generates 2 variations in one call |
| Explainer | `modules/explainer.py` | Gemini generates narrative + 5-step timeline, includes learning status |
| Feedback | `modules/feedback.py` | Ratings, A/B preference, user notes, gen params, reflection engine with learned rules |
| LLM Client | `utils/llm_client.py` | Gemini helpers: ask_json(), ask_json_with_image(), ask_text() |

## Key Patterns
- **Multi-emotion detection** — All analyzers return 1-3 emotions per input, fuser blends them
- **Singleton model loading** — MusicGen and Whisper models loaded once, reused across requests
- **Parallel analysis** — ThreadPoolExecutor runs text/image/voice analyzers simultaneously
- **Batched generation** — MusicGen generates 2 A/B variations in a single forward pass
- **JSON fence stripping** — `_strip_json_fences()` in llm_client.py handles Gemini's markdown wrapping
- **Reflection engine** — Every 5 ratings, Gemini analyzes feedback to extract:
  - Global prompt rules (positive/negative patterns)
  - Per-emotion slider ranges and prompt templates
  - MusicGen parameter correlation
- **Range-clamping** — Fuser nudges AI values toward learned ranges (70/30 blend) instead of overwriting
- **A/B preference** — Users pick preferred version, stored in feedback for future learning
- **Duration control** — 5s/10s/20s via DURATION_TOKENS mapping to max_new_tokens (250/500/1000)
- **"What I've learned" panel** — Displays global rules (positive/negative), per-emotion knowledge after reflections
- **User notes** — Free-text feedback field stored alongside ratings for richer reflection input
- **Gen params tracking** — Temperature, guidance_scale, max_new_tokens saved per session for parameter correlation
- **Learning stats display** — Shows reflection count, active rules, emotions learned, countdown to next cycle

## Feedback Learning Loop — Data Flow

```
save_feedback() → data/feedback.json (append)
       ↓ (every 5 new ratings)
_maybe_trigger_reflection() → run_reflection()
       ↓
  Phase A: _format_entries_for_reflection() → Gemini → global_rules {positive[], negative[]}
  Phase B: per emotion (needs 2+ entries) → Gemini → emotion_profiles {preferred_params, prompt_principles, anti_patterns}
  Phase C: _compute_param_insights() → correlate gen_params with ratings → param_insights
       ↓
  data/learned_rules.json (overwrite)
       ↓ (consumed on next generation)
  emotion_fuser.py → _range_clamp() uses emotion_profiles[emotion].preferred_params
  emotion_fuser.py → get_learned_defaults() fallback averages high-rated sessions
  music_orchestrator.py → _build_knowledge_context() injects:
    - get_top_prompts(emotion) → few-shot positive examples
    - get_negative_examples(emotion) → anti-patterns
    - get_emotion_profile(emotion) → principles + anti_patterns
    - get_learned_rules() → global positive/negative rules
  explainer.py → mentions reflection_count + learned principles in narrative
```

### Proven Impact (from 13 test sessions)
- Sessions 1-5 (no learning): avg 3.2/5 — prompts used vague genre labels, "looping/unchanging" language
- Reflection #1 at session 5: extracted "name specific instruments", "avoid looping", happy profile (energy=70, warmth=70-80)
- Sessions 6-13 (with learning): avg 4.3/5 — prompts use specific instruments, learned slider ranges, few-shot examples
- "excited" went from 2/5 to 5/5 after global rules stopped conflicting descriptors
- Key mechanisms: few-shot prompt injection (top_prompts), anti-pattern avoidance (negative_examples), range-clamping (emotion_profiles)

### Key Constants
- `REFLECTION_THRESHOLD = 5` — ratings between reflection cycles
- Range-clamping blend: 70% toward learned boundary, 30% AI value (when outside range)
- Top/negative prompts: max 3 examples injected per category
- Emotion profiles need 2+ sessions per emotion to be created

## Git Worktree Setup
This project uses git worktrees for parallel Claude Code sessions:

| Directory | Branch | Scope |
|-----------|--------|-------|
| `Music2myears/` | `master` | Main app, UI, integration |
| `Music2myears-analyzers/` | `feature/analyzers` | text_analyzer, image_analyzer, voice_analyzer |
| `Music2myears-music/` | `feature/music-engine` | music_orchestrator, music_generator |
| `Music2myears-feedback/` | `feature/feedback-loop` | feedback, explainer, emotion_fuser |

**Rule: each worktree only edits its own modules.** Merge via PR into master.

## Data Files (gitignored)
- `data/feedback.json` — User ratings, profiles, prompts, A/B preferences
- `data/learned_rules.json` — Reflection output: global rules, emotion profiles, param insights

## Environment
- API key in `.env` (never commit) — needs `GEMINI_API_KEY`
- Python venv at `venv/` (gitignored)
- MusicGen model cached at `~/.cache/huggingface/`
- Whisper model cached at `~/.cache/whisper/`
- ffmpeg required (`brew install ffmpeg`)

## Running Locally
```bash
source venv/bin/activate
streamlit run app.py
```
First run downloads MusicGen (~2.5GB). Generation takes ~20-30s on M1 Mac.

## Known Decisions
- MusicGen runs locally because HuggingFace Inference API is dead (410 Gone as of Feb 2026)
- Voice input uses `st_audiorec` for in-browser recording with start/stop buttons
- Style/warmth mappings were diversified to avoid lo-fi bias in generated music
- A/B generation uses batched inference (single forward pass) for speed
- Reflection engine threshold set to 5 ratings before first learning cycle
