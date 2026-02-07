MUSIC2MYEARS — BUILD SPEC (Hackathon)

Goal:
Turn human expression into personalized music with a wow experience.

Inputs:
- image (optional)
- text (optional)
- voice (optional)
Rule: at least one input required

Outputs:
- generated audio soundtrack
- explanation: why this music fits the input
- visualization: emotion/energy timeline
- feedback stored: rating + replay intent

Pipeline:
1) Intake inputs (any combo)
2) Per-input understanding:
   - image → caption + mood
   - text → summary + mood
   - voice → transcription + tone
3) Emotion fusion → one emotional profile (emotion, energy, arc, style)
4) Music orchestration → structured plan (tempo, instruments, sections)
5) Music generation (MusicGen) + 1–2 variations
6) Show explanation + timeline
7) Collect feedback and adjust next prompt
