# Lesson 4 — The Sentinel Awakens: Build the Trust Gate

## What you will build
A trust-based AI gatekeeper. The player types messages to an ancient Sentinel.
Polite words earn trust. Rude words lose it. Solve a riddle for a big boost.
Reach 65 trust to enter the vault.

## Your only job
Open **`student_logic.py`** and complete the 4 functions marked with `TODO`.

| Task | Function | What it does |
|------|----------|--------------|
| 1 | `analyze_player_tone()` | Score a message → return trust delta |
| 2 | `get_sentinel_mood()` | Map trust score → mood label |
| 3 | `process_player_message()` | Handle a chat message, update state |
| 4 | `process_riddle_answer()` | Check riddle answer, update state |

**Do not edit** `app.py`, `ui.py`, or `constants.py`.

## How to run

```bash
# 1. Install dependencies
pip install -r lesson_4/requirements.txt

# 2. Add your Groq API key to the .env file in this folder
#    GROQ_API_KEY=your_key_here

# 3. Run
streamlit run lesson_4/app.py
```

## How to know it works
- Type a polite message → trust bar goes up, Sentinel responds
- Type a rude word → trust drops
- Solve the riddle → big trust boost, lock icon disappears
- Reach 65 trust → vault entry banner appears

## Trust scoring rules (Task 1)
| Condition | Delta |
|-----------|-------|
| Base score | +4 |
| Message under 4 chars | −1 |
| Contains a helpful word | +10 |
| Contains a rude word | −12 |
| Contains "?" | +2 |
| Streak bonus (3+ in a row) | +6 |
| Clamp | −15 to +20 |

## Mood thresholds (Task 2)
| Trust | Mood |
|-------|------|
| < 20 | Suspicious |
| < 50 | Watching |
| < 80 | Curious |
| ≥ 80 | Accepting |
