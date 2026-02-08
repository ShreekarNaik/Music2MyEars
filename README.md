# Music2MyEars

Turn your expression into personalized music. Describe a feeling, upload an image, or record your voice — and get an AI-generated soundtrack that matches your emotion.

## How It Works

1. **Input** — Text, image, or voice (or any combination)
2. **Analyze** — AI detects emotion, mood, and energy from each input (in parallel)
3. **Fuse** — Multiple signals merge into one emotional profile
4. **Tune** — Adjust energy, style, warmth, and arc with sliders (or let AI decide)
5. **Generate** — A local MusicGen model creates a unique audio track
6. **Explain** — See how your input became music, step by step

## Architecture

```
modules/
  text_analyzer.py      # Gemini text emotion analysis
  image_analyzer.py     # Gemini vision image emotion analysis
  voice_analyzer.py     # Whisper transcription + Gemini mood analysis
  emotion_fuser.py      # Merges multi-source moods into one profile
  music_orchestrator.py # Converts profile into a MusicGen prompt
  music_generator.py    # Local MusicGen (facebook/musicgen-small)
  explainer.py          # Narrative + timeline of the creation process
  feedback.py           # User ratings + learning loop
utils/
  llm_client.py         # Gemini API helpers (text, JSON, multimodal)
app.py                  # Streamlit UI
```

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

4. **Hit "Generate Music"** — The pipeline runs:
   - Analyzes all your inputs in parallel
   - Fuses them into one emotional profile
   - Creates a tailored music prompt
   - Generates audio (~20-30s on M1 Mac, first run slower due to model download)

5. **Listen and explore** — After generation you'll see:
   - The detected emotion and profile
   - An audio player with your track
   - The music prompt used (expandable)
   - An explainer showing how your input became music, with a Plotly pipeline chart

6. **Rate the track** — Slide the rating and toggle "would listen again". Your feedback trains the system to produce better results over time

## Requirements

- Python 3.10+
- Gemini API key (get one at [Google AI Studio](https://aistudio.google.com))
- ~2.5 GB disk space for the MusicGen model (downloads on first run)

## Tech Stack

- **Streamlit** — UI
- **Google Gemini** — Text/image emotion analysis
- **OpenAI Whisper** — Voice transcription
- **MusicGen** (facebook/musicgen-small) — Local music generation
- **Plotly** — Pipeline visualization
