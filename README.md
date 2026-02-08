# Music2MyEars

Turn your expression into personalized music. Describe a feeling, upload an image, or record your voice — and get an AI-generated soundtrack that matches your emotion.

## How It Works

1. **Input** — Text, image, or voice (or any combination)
2. **Analyze** — AI detects multiple emotions from each input (in parallel)
3. **Fuse** — All emotion signals blend into one profile, guided by learned knowledge
4. **Tune** — Adjust energy, style, warmth, and arc with sliders (or let AI decide)
5. **Generate** — MusicGen creates two A/B variations in a single batched call
6. **Compare** — Listen to both versions, pick your favorite
7. **Explain** — See how your input became music, step by step
8. **Learn** — Your feedback trains the system to produce better results over time

## Architecture

```
modules/
  text_analyzer.py      # Gemini text → multi-emotion analysis
  image_analyzer.py     # Gemini vision → image emotion analysis
  voice_analyzer.py     # Whisper transcription + Gemini mood analysis
  emotion_fuser.py      # Blends multi-source moods, range-clamped by learned knowledge
  music_orchestrator.py # Converts profile into a vivid MusicGen prompt
  music_generator.py    # Batched MusicGen — 2 variations in one forward pass
  explainer.py          # Narrative + timeline with learning status
  feedback.py           # Ratings, A/B preference, reflection engine
utils/
  llm_client.py         # Gemini API helpers (text, JSON, multimodal)
app.py                  # Streamlit UI
```

## Key Features

- **Multi-emotion detection** — Detects 1-3 emotions per input (e.g. "sad + hopeful + reflective"), blends them into slider values
- **A/B comparison** — Two music variations generated in parallel, side-by-side playback with preference selection
- **Duration control** — Choose 5s, 10s, or 20s track length
- **Reflection engine** — Every 5 ratings, AI analyzes all feedback to extract prompt rules, per-emotion slider ranges, and parameter insights
- **"What I've learned" panel** — Shows discovered rules, emotion-specific knowledge, and anti-patterns
- **Range-clamping** — Learned knowledge nudges AI values toward proven ranges without overwriting contextual judgment
- **User feedback notes** — Free-text feedback field (e.g. "Too slow for the energy I wanted")
- **Download buttons** — Save your generated tracks as WAV files
- **Multimodal parallel analysis** — Text, image, and voice analyzed simultaneously via ThreadPoolExecutor
- **Learning stats** — After submitting feedback, see reflection count, active rules, and countdown to next learning cycle

## Setup

```bash
# Clone the repo
git clone https://github.com/geethdv-18/Music2MyEars.git
cd Music2MyEars

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install ffmpeg (required for Whisper voice transcription)
brew install ffmpeg

# Configure API key
cp .env.example .env
# Edit .env and add your Gemini API key

# Run the app
streamlit run app.py
```

## How to Use

1. **Open the app** — Run `streamlit run app.py` and open `http://localhost:8501` in your browser

2. **Provide input** (use one or combine all three):
   - **Text** — Type how you're feeling, describe a memory, a scene, anything
   - **Image** — Upload a photo that captures a mood (sunset, city, old photo, etc.)
   - **Voice** — Hit the record button, speak your feelings, then stop when done. Your speech is transcribed and shown in the text box below

3. **Tweak the sliders** (optional) — Expand "Advanced Options" to adjust:
   - **Energy** — Calm ambient to high-intensity
   - **Style** — Minimal/sparse to epic orchestral
   - **Warmth** — Deep and moody to bright and sparkling
   - **Arc** — Steady loop to dramatic build-up

4. **Pick a duration** — Choose 5s, 10s, or 20s for your track

5. **Hit "Generate Music"** — The pipeline runs:
   - Analyzes all your inputs in parallel (detects multiple emotions)
   - Fuses them into one emotional profile (guided by past learning)
   - Creates a tailored music prompt
   - Generates two A/B variations (~30s on M1 Mac, first run slower due to model download)

5. **Listen and compare** — After generation you'll see:
   - All detected emotions (e.g. "nostalgic + hopeful")
   - Two audio players (Version A and B) with download buttons
   - A preference selector (A / B / No preference)
   - The music prompt used (expandable)
   - An explainer showing how your input became music, with a Plotly pipeline chart

7. **Rate and teach** — Rate the track, toggle "would listen again", pick your preferred version, and optionally leave a note. Every 5 ratings the system reflects on all feedback to improve future generations. Check the "What I've learned" panel to see discovered rules.

## Feedback Learning Loop

The system gets smarter with every rating you give. Here's how it works:

### The Cycle
```
You rate a track (1-5) → Stored in data/feedback.json
                              ↓
               Every 5 ratings → Reflection Engine triggers
                              ↓
          Phase A: Gemini analyzes ALL feedback to find
                   global prompt patterns (what works vs. what to avoid)
                              ↓
          Phase B: Per-emotion analysis — for each emotion with 2+ sessions,
                   extracts preferred slider ranges, prompt principles,
                   anti-patterns, and best prompt templates
                              ↓
          Phase C: Parameter correlation — correlates MusicGen settings
                   (temperature, guidance_scale) with ratings
                              ↓
               Results saved to data/learned_rules.json
                              ↓
          Next generation uses learned knowledge:
          • Emotion Fuser range-clamps sliders to proven ranges (70/30 blend)
          • Orchestrator injects best-rated prompts as examples
          • Orchestrator avoids patterns from low-rated sessions
          • Explainer mentions how past learning influenced the output
```

### What It Learns (example after 10 sessions)
- **Global rules**: "Specify multiple instruments instead of genre labels", "Avoid looping/unchanging elements"
- **Happy profile**: Energy 70, Warmth 70-80, use bright/upbeat elements, avoid minor keys
- **Sad profile**: Energy 20, Warmth 30-40, use minor key + clean guitar, avoid high energy

### Range-Clamping (not blind overwriting)
When the system learns that "happy" works best at energy 60-80, it doesn't force energy to 70. If the AI detects energy=75 from your input, it keeps it (within range). If the AI says energy=30, it nudges it toward 60 (nearest boundary) with a 70/30 blend: `0.3 × 30 + 0.7 × 60 = 51`. This preserves the AI's contextual judgment while benefiting from past learning.

### Real Example: How It Improved Over 13 Sessions

Here's what actually happened during testing:

**Before learning (Sessions 1-5, no learned rules):**

| Session | Emotion | Prompt style | Rating |
|---------|---------|-------------|--------|
| 1 | peaceful | "unchanging indie pop loop...whisper-soft light drums" | 2/5 |
| 3 | sad | "ambient indie pop loop...light brushed drums" | 3/5 |
| 5 | excited | "orchestral piece...bright shimmering brass" | 2/5 |

Problems: prompts used vague genre labels ("indie pop loop"), repetitive words ("unchanging", "looping"), and conflicting descriptors.

**Reflection #1 triggers after Session 5** — Gemini analyzes all 5 sessions and discovers:
- "Looping/unchanging" language correlates with low ratings
- Naming specific instruments (piano, strings) correlates with high ratings
- Sessions 2 and 4 (rated 5/5 and 4/5) used "driving piano chords", "powerful brass", "crisp production"

**After learning (Sessions 6-13, with learned rules active):**

| Session | Emotion | What changed | Rating |
|---------|---------|-------------|--------|
| 6 | happy | Orchestrator injected Session 2's prompt as a positive example. Fuser clamped energy to 70 (learned range). | 4/5 |
| 10 | happy | Same emotion, now with 4 data points. Prompt: "driving pop-rock...powerful piano chords, uplifting strings, crisp studio-quality production" | 5/5 |
| 11 | joyful | System applied happy-adjacent rules. "driving percussion, soaring strings, crystalline synth melody, verse-chorus structure" | 5/5 |
| 13 | excited | Previously 2/5 — now "explosive orchestral...massive choir, soaring brass fanfares, shimmering strings" | 5/5 |

**What drove the improvement:**

1. **Few-shot injection** — The orchestrator fed Session 2's high-rated prompt ("energetic pop-rock at 120 BPM, driving piano chords") into Gemini as a positive example, so new prompts followed the same pattern
2. **Anti-pattern avoidance** — Session 1's low-rated "unchanging loop" prompt was injected as a negative example, so Gemini avoided "looping" language
3. **Range-clamping** — Happy sessions consistently scored well at energy=70, warmth=70-80, so the fuser locked new happy sessions into that range instead of guessing
4. **Global rules** — "Specify multiple instruments instead of genre labels" applied across all emotions, improving even first-time emotions like "joyful"

**Net result:** Average rating went from **3.2/5** (sessions 1-5) to **4.3/5** (sessions 6-13).

### Viewing What's Been Learned
- **"What I've learned" panel** on the main page shows discovered rules and emotion-specific knowledge
- **Learning stats** appear after submitting feedback: reflection count, active rules, countdown to next cycle
- **Raw data** in `data/learned_rules.json` for full inspection

## Requirements

- Python 3.10+
- ffmpeg (`brew install ffmpeg`)
- Gemini API key (get one at [Google AI Studio](https://aistudio.google.com))
- ~2.5 GB disk space for the MusicGen model (downloads on first run)

## Tech Stack

- **Streamlit** — UI
- **Google Gemini 2.0 Flash** — Text/image emotion analysis, reflection engine
- **OpenAI Whisper** — Voice transcription
- **MusicGen** (facebook/musicgen-small) — Local music generation
- **Plotly** — Pipeline visualization
