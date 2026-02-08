from concurrent.futures import ThreadPoolExecutor, as_completed
import streamlit as st
import plotly.graph_objects as go
from modules.text_analyzer import analyze_text
from modules.image_analyzer import analyze_image
from modules.voice_analyzer import analyze_voice, transcribe_audio
from modules.emotion_fuser import fuse_emotions
from modules.music_orchestrator import create_music_prompt
from modules.music_generator import generate_music
from modules.explainer import explain_music
from modules.feedback import save_feedback, get_feedback_summary, get_learned_rules
from st_audiorec import st_audiorec

st.set_page_config(page_title="Music2MyEars", page_icon="🎵", layout="centered")

st.title("Music2MyEars")
st.caption("Turn your expression into personalized music")

# --- INPUT SECTION ---
text_input = st.text_area(
    "What's on your mind?",
    placeholder="Describe a feeling, a memory, a scene... anything.",
    height=100,
)

col_image, col_voice = st.columns(2)

with col_image:
    image_file = st.file_uploader(
        "Upload an image",
        type=["png", "jpg", "jpeg", "webp"],
    )
    if image_file:
        st.image(image_file, use_container_width=True)

with col_voice:
    st.write("Record your feelings")
    voice_bytes_recorded = st_audiorec()

    # Initialize transcript in session state
    if "voice_transcript" not in st.session_state:
        st.session_state["voice_transcript"] = ""

    # Transcribe when new audio is recorded
    if voice_bytes_recorded:
        st.audio(voice_bytes_recorded, format="audio/wav")
        with st.spinner("Transcribing..."):
            transcript = transcribe_audio(voice_bytes_recorded)
        st.session_state["voice_transcript"] = transcript if transcript else ""
        if not transcript:
            st.warning("Couldn't pick up any words. Try again?")

    # Show transcript
    st.text_area(
        "What we heard",
        value=st.session_state["voice_transcript"],
        height=80,
        disabled=True,
        placeholder="Your speech will appear here...",
    )

    # Reset button
    if st.button("Reset recording"):
        st.session_state["voice_transcript"] = ""
        st.rerun()

# --- DURATION ---
DURATION_TOKENS = {"5 sec": 250, "10 sec": 500, "20 sec": 1000}
duration = st.radio("Duration", list(DURATION_TOKENS.keys()), index=0, horizontal=True)

# --- ADVANCED OPTIONS ---
with st.expander("Advanced Options", expanded=False):
    st.caption("Defaults are set by AI after analysis. Move sliders to override.")
    defaults = st.session_state.get("ai_profile", {})
    col1, col2 = st.columns(2)
    with col1:
        slider_energy = st.slider("Energy", 0, 100, defaults.get("energy", 50))
        slider_style = st.slider("Style: Lo-fi ↔ Cinematic", 0, 100, defaults.get("style", 50))
    with col2:
        slider_warmth = st.slider("Warmth: Warm ↔ Bright", 0, 100, defaults.get("warmth", 50))
        slider_arc = st.slider("Arc: Steady ↔ Big Build", 0, 100, defaults.get("arc", 50))

# --- WHAT I'VE LEARNED ---
rules = get_learned_rules()
if rules.get("reflection_count", 0) > 0:
    with st.expander("What I've learned", expanded=False):
        global_pos = rules.get("global_rules", {}).get("positive", [])
        global_neg = rules.get("global_rules", {}).get("negative", [])
        emotion_profiles = rules.get("emotion_profiles", {})

        if global_pos:
            st.markdown("**What works well:**")
            for r in global_pos:
                st.markdown(f"- {r}")
        if global_neg:
            st.markdown("**What to avoid:**")
            for r in global_neg:
                st.markdown(f"- {r}")
        if emotion_profiles:
            st.markdown(f"**Emotions with specific knowledge:** {', '.join(emotion_profiles.keys())}")
            for emo, profile in emotion_profiles.items():
                principles = profile.get("prompt_principles", [])
                if principles:
                    st.markdown(f"*{emo}*: {'; '.join(principles[:2])}")

        st.caption(f"Based on {rules.get('reflection_count', 0)} reflection(s) analyzing {rules.get('entries_analyzed', 0)} sessions")

# --- GENERATE ---
if st.button("Generate Music", type="primary", use_container_width=True):
    has_text = bool(text_input and text_input.strip())
    has_image = image_file is not None
    has_voice = voice_bytes_recorded is not None

    if not (has_text or has_image or has_voice):
        st.error("Please provide at least one input (text, image, or voice).")
        st.stop()

    # Read file bytes upfront (before threads)
    image_bytes = image_file.getvalue() if has_image else None
    voice_bytes = voice_bytes_recorded if has_voice else None

    # Step A: Analyze inputs in parallel
    mood_list = []
    with st.spinner("Analyzing your inputs..."):
        tasks = {}
        with ThreadPoolExecutor() as executor:
            if has_text:
                tasks[executor.submit(analyze_text, text_input.strip())] = "text"
            if has_image:
                tasks[executor.submit(analyze_image, image_bytes)] = "image"
            if has_voice:
                tasks[executor.submit(analyze_voice, voice_bytes)] = "voice"
            for future in as_completed(tasks):
                mood_list.append(future.result())

    # Step B: Fuse emotions
    with st.spinner("Building emotional profile..."):
        ai_profile = fuse_emotions(mood_list)

    st.session_state["ai_profile"] = ai_profile

    # Step C: Apply slider overrides
    final_profile = dict(ai_profile)
    overrides = []
    slider_vals = {"energy": slider_energy, "style": slider_style, "warmth": slider_warmth, "arc": slider_arc}

    for dim, slider_val in slider_vals.items():
        ai_val = ai_profile.get(dim, 50)
        if slider_val != defaults.get(dim, 50):
            final_profile[dim] = slider_val
            overrides.append(dim)
        else:
            final_profile[dim] = ai_val

    final_profile["overrides"] = overrides

    # Step D: Orchestrate + Generate
    with st.spinner("Composing your soundtrack..."):
        music_prompt = create_music_prompt(final_profile)

    with st.spinner("Generating music... (this takes ~20-30s)"):
        audio_list = generate_music(music_prompt, max_new_tokens=DURATION_TOKENS[duration])

    # Step E: Explain
    with st.spinner("Writing the story of your music..."):
        explanation = explain_music(
            text_input or "", ai_profile, final_profile, overrides, music_prompt
        )

    # Store everything in session state so results survive reruns
    st.session_state["music_prompt"] = music_prompt
    st.session_state["final_profile"] = final_profile
    st.session_state["audio_list"] = audio_list
    st.session_state["ai_profile_result"] = ai_profile
    st.session_state["overrides_result"] = overrides
    st.session_state["mood_list_result"] = mood_list
    st.session_state["explanation"] = explanation
    st.session_state["gen_params"] = {
        "max_new_tokens": DURATION_TOKENS[duration],
        "temperature": 1.0,
        "guidance_scale": 3.0,
    }
    st.session_state["has_results"] = True

# --- RESULTS (persisted via session_state) ---
if st.session_state.get("has_results"):
    audio_list = st.session_state["audio_list"]
    ai_profile = st.session_state["ai_profile_result"]
    final_profile = st.session_state["final_profile"]
    overrides = st.session_state["overrides_result"]
    mood_list = st.session_state["mood_list_result"]
    music_prompt = st.session_state["music_prompt"]
    explanation = st.session_state["explanation"]

    st.divider()

    # Emotions detected
    emotions = ai_profile.get("emotions", [ai_profile.get("emotion", "?")])
    st.subheader(f"We sensed: {' + '.join(emotions)}")

    # Source badges
    sources_used = [m.get("source", "?") for m in mood_list]
    st.caption(f"Sources: {', '.join(sources_used)}")

    # Profile comparison
    col_ai, col_final = st.columns(2)
    with col_ai:
        st.caption("AI detected")
        st.write(f"Energy **{ai_profile.get('energy')}** | Style **{ai_profile.get('style')}** | Warmth **{ai_profile.get('warmth')}** | Arc **{ai_profile.get('arc')}**")
    with col_final:
        st.caption("Final (with your overrides)" if overrides else "Final (AI defaults)")
        st.write(f"Energy **{final_profile.get('energy')}** | Style **{final_profile.get('style')}** | Warmth **{final_profile.get('warmth')}** | Arc **{final_profile.get('arc')}**")

    if overrides:
        st.info(f"You adjusted: {', '.join(overrides)}")

    # Audio player — A/B comparison
    if len(audio_list) >= 2:
        col_a, col_b = st.columns(2)
        with col_a:
            st.caption("Version A")
            st.audio(audio_list[0], format="audio/wav")
            st.download_button("Download A", audio_list[0], file_name="music2myears_A.wav", mime="audio/wav")
        with col_b:
            st.caption("Version B")
            st.audio(audio_list[1], format="audio/wav")
            st.download_button("Download B", audio_list[1], file_name="music2myears_B.wav", mime="audio/wav")
        preferred = st.radio("Which version do you prefer?", ["A", "B", "No preference"], horizontal=True, key="ab_pref")
        st.session_state["preferred_version"] = preferred
    else:
        st.audio(audio_list[0], format="audio/wav")
        st.download_button("Download", audio_list[0], file_name="music2myears.wav", mime="audio/wav")

    # Music prompt used
    with st.expander("See the music prompt"):
        st.text_area("Prompt", music_prompt, height=150, disabled=True, label_visibility="collapsed")

    # --- EXPLAINER ---
    st.divider()
    st.subheader("How your input became music")

    narrative = explanation.get("narrative", "")
    if narrative:
        st.info(narrative)

    timeline = explanation.get("timeline", [])
    if timeline:
        steps = [t.get("step", "") for t in timeline]
        emotions = [t.get("emotion", "") for t in timeline]
        descriptions = [t.get("description", "") for t in timeline]

        fig = go.Figure(go.Bar(
            x=steps,
            y=list(range(1, len(steps) + 1)),
            text=emotions,
            hovertext=descriptions,
            marker_color=["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7"],
            textposition="inside",
        ))
        fig.update_layout(
            title="Pipeline Journey",
            xaxis_title="Step",
            yaxis_title="Stage",
            yaxis=dict(showticklabels=False),
            height=300,
            margin=dict(t=40, b=40),
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # --- FEEDBACK ---
    st.subheader("Rate this track")
    rating = st.slider("How well does this music match your feeling?", 1, 5, 3, key="rating")
    would_replay = st.toggle("Would you listen to this again?", key="replay")
    user_note = st.text_input("Any specific feedback?", placeholder="e.g. 'Too slow for the energy I wanted'", key="user_note")

    if st.button("Submit Feedback"):
        save_feedback(
            rating=rating,
            would_replay=would_replay,
            ai_profile=ai_profile,
            final_profile=final_profile,
            music_prompt=music_prompt,
            preferred_version=st.session_state.get("preferred_version", "N/A"),
            gen_params=st.session_state.get("gen_params"),
            user_note=user_note if user_note else None,
        )
        st.success("Thanks! Your feedback improves future generations.")

        summary = get_feedback_summary()
        if summary:
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                st.caption(
                    f"Learning from {summary['total_sessions']} sessions | "
                    f"Avg rating: {summary['avg_rating']}/5 | "
                    f"Replay rate: {summary['replay_rate']}%"
                )
            with col_s2:
                if summary["reflections_completed"] > 0:
                    st.caption(
                        f"Reflections: {summary['reflections_completed']} | "
                        f"Rules active: {summary['rules_active']} | "
                        f"Emotions learned: {', '.join(summary['emotions_learned']) or 'none'}"
                    )
                elif summary["next_reflection_in"] > 0:
                    st.caption(f"Next learning cycle in {summary['next_reflection_in']} more ratings")
