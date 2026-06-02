# ═══════════════════════════════════════════════════════════════════
#  LESSON 4 — The Sentinel Awakens: Build the Trust Gate
#  This is YOUR file. The sections between START and END markers
#  are where you write your code.
#  Everything outside those markers is provided — do not change it.
# ═══════════════════════════════════════════════════════════════════

import random
import streamlit as st

from constants import (
    MAX_TRUST, BANISH_THRESHOLD, STREAK_BONUS_AT,
    HELPFUL_HINTS, RUDE_HINTS,
    SENTINEL_FALLBACKS, REPEAT_REPLIES,
)


# ── PROVIDED: Groq AI helper — do not change ─────────────────────
def _ask_sentinel_ai(player_name: str, message: str, trust: int, mood: str) -> str:
    import config
    mood_styles = {
        "Suspicious": "You are deeply suspicious and cold. Short, sharp sentences. You test every word.",
        "Watching":   "You are cautious but paying attention. Quiet intensity, a little poetic.",
        "Curious":    "You're genuinely intrigued. Ask questions back. Warmer but still mysterious.",
        "Accepting":  "Ancient, wise, almost warm. Flowing sentences. You're a guide now.",
    }
    feel_map = {
        "Suspicious": "You barely acknowledge them.",
        "Watching":   "You're starting to notice them.",
        "Curious":    "You're genuinely interested in them.",
        "Accepting":  "You respect them. They've earned it.",
    }
    if config.GROQ_API_KEY:
        try:
            from groq import Groq
            r = Groq(api_key=config.GROQ_API_KEY).chat.completions.create(
                model=config.GROQ_TEXT_MODEL, temperature=0.9,
                messages=[
                    {"role": "system", "content": (
                        f"You are The Sentinel — an ancient immortal gatekeeper.\n"
                        f"{mood_styles.get(mood, mood_styles['Suspicious'])}\n"
                        "Use contractions, vary sentence length, react emotionally.\n"
                        "Never break character. Never mention being an AI.\n"
                        "Under 80 words. End with a question, warning, or hint."
                    )},
                    {"role": "user", "content": (
                        f'Traveler: {player_name or "Unknown"}\n'
                        f'How you feel: {feel_map.get(mood, feel_map["Suspicious"])}\n'
                        f'Message: "{message}"\nRespond naturally. Don\'t reveal numbers.'
                    )},
                ],
            )
            return r.choices[0].message.content.strip()
        except Exception:
            pass
    return random.choice(SENTINEL_FALLBACKS.get(mood, SENTINEL_FALLBACKS["Suspicious"]))


# ── PROVIDED: chat log helper — do not change ─────────────────────
def _append_log(role: str, text: str):
    st.session_state.sentinel_messages.append(f"[{role}]: {text}")


# ═══════════════════════════════════════════════════════════════════
#  TASK 1 — analyze_player_tone
#
#  Read the player's message and return an integer trust delta.
#  Positive = trust goes up. Negative = trust goes down.
#
#  Rules:
#  • Base delta = +4
#  • Message under 4 chars  → subtract 1
#  • Contains a HELPFUL word → add +10
#  • Contains a RUDE word    → subtract 12
#  • Contains "?"            → add +2
#  • streak >= STREAK_BONUS_AT and delta > 0 → add +6
#  • Clamp result between -15 and +20
# ═══════════════════════════════════════════════════════════════════
def analyze_player_tone(message: str, streak: int = 0, recent_messages: list = None) -> int:
    msg = message.lower().strip()

    # PROVIDED: repeat detection — do not change
    if recent_messages:
        recent_lower = [m.lower().strip() for m in recent_messages[-6:]]
        if recent_lower.count(msg) >= 2:
            return 0

    # ─────────────────────────────────────────────────────────────
    # ── LESSON 4 START ───────────────────────────────────────────

    delta = 4

    if len(msg) < 4:
        delta -= 1

    if any(word in msg for word in HELPFUL_HINTS):
        delta += 10

    if any(word in msg for word in RUDE_HINTS):
        delta -= 12

    if "?" in msg:
        delta += 2

    if streak >= STREAK_BONUS_AT and delta > 0:
        delta += 6

    delta = max(-15, min(20, delta))

    # ── LESSON 4 END ─────────────────────────────────────────────
    # ─────────────────────────────────────────────────────────────

    return delta


# ═══════════════════════════════════════════════════════════════════
#  TASK 2 — get_sentinel_mood
#
#  Map trust score → mood label string.
#
#  trust < 20  → "Suspicious"
#  trust < 50  → "Watching"
#  trust < 80  → "Curious"
#  trust >= 80 → "Accepting"
# ═══════════════════════════════════════════════════════════════════
def get_sentinel_mood(trust: int) -> str:
    # ─────────────────────────────────────────────────────────────
    # ── LESSON 4 START ───────────────────────────────────────────

    if trust < 20:
        return "Suspicious"
    elif trust < 50:
        return "Watching"
    elif trust < 80:
        return "Curious"
    else:
        return "Accepting"

    # ── LESSON 4 END ─────────────────────────────────────────────
    # ─────────────────────────────────────────────────────────────


# ═══════════════════════════════════════════════════════════════════
#  TASK 3 — process_player_message
#
#  Called every time the player sends a chat message.
#  Steps:
#  1.  Guard — empty player name → toast + return
#  2.  Guard — empty message → return
#  3.  Repeat check → toast, log, return early
#  4.  analyze_player_tone() → delta
#  5.  Update trust (clamped 0–MAX_TRUST)
#  6.  Update mood
#  7.  Update streak
#  8.  Log player message
#  9.  Get + log Sentinel reply
#  10. Append msg to player_messages
#  11. Set latest_clue
#  12. Increment messages_sent
#  13. Banish check
# ═══════════════════════════════════════════════════════════════════
def process_player_message(msg: str):
    s = st.session_state

    # ─────────────────────────────────────────────────────────────
    # ── LESSON 4 START ───────────────────────────────────────────

    # Step 1 — guard: empty player name
    if not s.player_name.strip():
        st.toast("Enter your traveler name first.", icon="⚠️")
        return

    # Step 2 — guard: empty message
    if not msg.strip():
        return

    # Step 3 — repeat detection
    recent = [m.lower().strip() for m in s.player_messages[-6:]]
    if recent.count(msg.lower().strip()) >= 2:
        st.toast("The Sentinel noticed you're repeating yourself.", icon="😐")
        _append_log("YOU", msg)
        _append_log("SENTINEL", random.choice(REPEAT_REPLIES))
        s.player_messages.append(msg)
        s.messages_sent += 1
        return

    # Step 4 — analyze tone
    delta = analyze_player_tone(msg, s.streak, s.player_messages)

    # Step 5 — update trust
    s.trust_score = max(0, min(MAX_TRUST, s.trust_score + delta))

    # Step 6 — update mood
    s.sentinel_mood = get_sentinel_mood(s.trust_score)

    # Step 7 — update streak
    s.streak = s.streak + 1 if delta > 0 else 0

    # Step 8 — log player message
    _append_log("YOU", msg)

    # Step 9 — get and log Sentinel reply
    reply = _ask_sentinel_ai(s.player_name, msg, s.trust_score, s.sentinel_mood)
    _append_log("SENTINEL", reply)

    # Step 10 — append to player_messages
    s.player_messages.append(msg)

    # Step 11 — update latest clue
    s.latest_clue = "The Sentinel studies your tone."

    # Step 12 — increment messages_sent
    s.messages_sent += 1

    # Step 13 — banish check
    if s.trust_score <= BANISH_THRESHOLD and delta < 0:
        s.banished = True

    # ── LESSON 4 END ─────────────────────────────────────────────
    # ─────────────────────────────────────────────────────────────


# ═══════════════════════════════════════════════════════════════════
#  TASK 4 — process_riddle_answer
#
#  Called when the player submits a riddle answer.
#  Steps:
#  1. Guard — already solved → toast + return
#  2. Guard — empty answer → return
#  3. Get riddle from session state
#  4. Check correct / wrong and update state accordingly
# ═══════════════════════════════════════════════════════════════════
def process_riddle_answer(answer: str):
    s = st.session_state

    # ─────────────────────────────────────────────────────────────
    # ── LESSON 4 START ───────────────────────────────────────────

    # Step 1 — guard: already solved
    if s.riddle_solved:
        st.toast("Logic lock already solved.", icon="ℹ️")
        return

    # Step 2 — guard: empty answer
    if not answer.strip():
        return

    # Step 3 — get riddle
    riddle = s.riddle

    # Step 4 — check correct or wrong
    if riddle["answer"].lower() in answer.lower().strip():
        # Correct
        s.riddle_solved = True
        s.trust_score = min(MAX_TRUST, s.trust_score + 35)
        s.sentinel_mood = get_sentinel_mood(s.trust_score)
        s.streak += 1
        _append_log("YOU", f"Riddle: {answer}")
        _append_log("SENTINEL", random.choice([
            "Yes. That's it. I felt the lock shift just now — something old and heavy, finally moving.",
            "Hm. You actually got it. The seal loosens. Don't make me regret this.",
            "Correct. The gate remembers that answer. You're smarter than you look, traveler.",
        ]))
        s.latest_clue = "The runes brighten — a thin line of light appears in the gate."
        st.toast("Correct! The lock flashes open.", icon="✅")
    else:
        # Wrong
        s.trust_score = max(0, s.trust_score - 5)
        s.sentinel_mood = get_sentinel_mood(s.trust_score)
        s.streak = 0
        _append_log("YOU", f"Riddle: {answer}")
        _append_log("SENTINEL", random.choice([
            "That's not it. Think harder — the hint is right in front of you.",
            "No... you're not there yet. Read the riddle again, slowly.",
            f"Wrong answer. The lock doesn't budge. Hint: {riddle['hint']}",
        ]))
        s.latest_clue = f"Hint: {riddle['hint']}"
        st.toast("Incorrect — the seal holds.", icon="❌")

    # ── LESSON 4 END ─────────────────────────────────────────────
    # ─────────────────────────────────────────────────────────────
