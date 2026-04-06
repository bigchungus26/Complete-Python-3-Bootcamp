"""Intake question definitions."""

from dataclasses import dataclass


@dataclass
class Question:
    key: str
    prompt: str
    options: list[str] | None = None
    allow_free_text: bool = False


BLOCK_A = [
    Question(
        key="primary_goal",
        prompt=(
            "What is your primary training goal?\n"
            "  (a) Maximum muscle growth (hypertrophy)\n"
            "  (b) Maximum strength (1RM progression)\n"
            "  (c) Both muscle and strength (hybrid)\n"
            "  (d) Maintain/build muscle while losing fat (body recomposition)"
        ),
        options=["a", "b", "c", "d"],
    ),
    Question(
        key="priority_muscles",
        prompt=(
            "Do you have any secondary goals or priority muscle groups to bring up?\n"
            "(e.g., 'chest and arms', 'glutes', 'back', or 'none')"
        ),
        allow_free_text=True,
    ),
    Question(
        key="caloric_phase",
        prompt=(
            "Are you currently in a caloric surplus, deficit, or maintenance?\n"
            "  (a) Surplus\n"
            "  (b) Deficit\n"
            "  (c) Maintenance"
        ),
        options=["a", "b", "c"],
    ),
]

BLOCK_B = [
    Question(
        key="training_months",
        prompt=(
            "How long have you been training consistently with progressive overload?\n"
            "  (a) Less than 6 months\n"
            "  (b) 6 months - 3 years\n"
            "  (c) 3+ years"
        ),
        options=["a", "b", "c"],
    ),
    Question(
        key="progression_rate",
        prompt=(
            "Can you currently add weight to your main compound lifts every single session?\n"
            "  (a) Yes — I add weight every session with good form\n"
            "  (b) No, but I add weight every 1-2 weeks\n"
            "  (c) No, weight goes up over weeks to months"
        ),
        options=["a", "b", "c"],
    ),
]

BLOCK_C = [
    Question(
        key="days_per_week",
        prompt=(
            "How many days per week can you train?\n"
            "  (a) 3\n"
            "  (b) 4\n"
            "  (c) 5\n"
            "  (d) 6"
        ),
        options=["a", "b", "c", "d"],
    ),
    Question(
        key="session_minutes",
        prompt=(
            "How long can each session be?\n"
            "  (a) Under 45 min\n"
            "  (b) 45-60 min\n"
            "  (c) 60-75 min\n"
            "  (d) 75-90 min\n"
            "  (e) 90+ min"
        ),
        options=["a", "b", "c", "d", "e"],
    ),
    Question(
        key="prefers_supersets",
        prompt=(
            "Do you prefer to superset antagonist movements to save time?\n"
            "  (a) Yes\n"
            "  (b) No\n"
            "  (c) No preference"
        ),
        options=["a", "b", "c"],
    ),
]

BLOCK_D = [
    Question(
        key="equipment_access",
        prompt=(
            "What equipment do you have access to?\n"
            "  (a) Full commercial gym (barbells, cables, machines, dumbbells)\n"
            "  (b) Gym with limited machines/cables\n"
            "  (c) Home gym with dumbbells and barbell only\n"
            "  (d) Other — describe"
        ),
        options=["a", "b", "c", "d"],
    ),
]

BLOCK_E = [
    Question(
        key="sex",
        prompt=(
            "Are you male or female?\n"
            "(Affects rep range recommendations — females bias slightly higher rep ranges)\n"
            "  (a) Male\n"
            "  (b) Female"
        ),
        options=["a", "b"],
    ),
    Question(
        key="injuries",
        prompt=(
            "Do you have any injuries, pain, or movement limitations?\n"
            "(Describe, or say 'none')"
        ),
        allow_free_text=True,
    ),
    Question(
        key="current_sets",
        prompt=(
            "Approximately how many hard sets per muscle group per week are you\n"
            "currently doing? (Rough number, e.g., '10', '15', or '0' if new)"
        ),
        allow_free_text=True,
    ),
    Question(
        key="current_program",
        prompt=(
            'What does your current program look like?\n'
            '(Brief description, or "starting fresh")'
        ),
        allow_free_text=True,
    ),
]

ALL_BLOCKS = [
    ("Block A — Goals", BLOCK_A),
    ("Block B — Training History", BLOCK_B),
    ("Block C — Schedule & Logistics", BLOCK_C),
    ("Block D — Equipment", BLOCK_D),
    ("Block E — Individual Factors", BLOCK_E),
]
