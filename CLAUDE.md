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
| UI | `app.py` | Streamlit app — columns for image/voice, sliders, A/B comparison, Plotly explainer |
| Text Analyzer | `modules/text_analyzer.py` | Gemini text emotion → {moods[], mood, energy, source} |
| Image Analyzer | `modules/image_analyzer.py` | Gemini vision → {caption, moods[], mood, energy, source} |
| Voice Analyzer | `modules/voice_analyzer.py` | Whisper transcription + Gemini mood → {transcript, moods[], mood, energy, source} |
| Emotion Fuser | `modules/emotion_fuser.py` | Merges multi-source moods into one profile, range-clamped by learned knowledge |
| Music Orchestrator | `modules/music_orchestrator.py` | Converts profile → vivid MusicGen prompt via Gemini |
| Music Generator | `modules/music_generator.py` | Batched MusicGen — generates 2 variations in one call |
| Explainer | `modules/explainer.py` | Gemini generates narrative + 5-step timeline, includes learning status |
| Feedback | `modules/feedback.py` | Ratings, A/B preference, reflection engine with learned rules |
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
