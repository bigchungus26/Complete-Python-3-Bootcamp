"""Conversational intake engine — walks through questions, builds UserProfile."""

from ironforge.data.muscle_groups import (
    Sex, CaloricPhase, EquipmentAccess, Equipment,
    VolumeMuscle,
)
from ironforge.intake.profile import UserProfile
from ironforge.intake.questions import ALL_BLOCKS


# Equipment multi-select options for limited / home gym.
EQUIPMENT_OPTIONS: list[tuple[str, Equipment, str]] = [
    ("a", Equipment.BARBELL, "Barbell"),
    ("b", Equipment.DUMBBELL, "Dumbbells"),
    ("c", Equipment.EZ_BAR, "EZ Bar"),
    ("d", Equipment.TRAP_BAR, "Trap / Hex Bar"),
    ("e", Equipment.KETTLEBELL, "Kettlebells"),
    ("f", Equipment.CABLE, "Cables"),
    ("g", Equipment.MACHINE, "Machines"),
    ("h", Equipment.SMITH_MACHINE, "Smith Machine"),
    ("i", Equipment.PULL_UP_BAR, "Pull-up Bar"),
    ("j", Equipment.DIP_STATION, "Dip Station"),
    ("k", Equipment.ADJUSTABLE_BENCH, "Adjustable Bench"),
    ("l", Equipment.RESISTANCE_BANDS, "Resistance Bands"),
    ("m", Equipment.BODYWEIGHT, "Bodyweight only"),
]

# Injury option-letter → key (matches questions.INJURY_OPTIONS order).
INJURY_LETTER_MAP: dict[str, str] = {
    "a": "lower_back",
    "b": "knee",
    "c": "shoulder",
    "d": "elbow",
    "e": "wrist",
    "f": "hip",
}


def _ask(prompt: str, options: list[str] | None = None,
         multi_select: bool = False) -> str:
    """Ask a question and validate input."""
    print()
    print(prompt)
    while True:
        answer = input("\n> ").strip().lower()
        if not answer:
            if multi_select:
                return ""
            print("Please enter a response.")
            continue
        if options and not multi_select and answer not in options:
            print(f"Please enter one of: {', '.join(options)}")
            continue
        if options and multi_select:
            picks = [p.strip() for p in answer.split(",") if p.strip()]
            invalid = [p for p in picks if p not in options]
            if invalid:
                print(f"Invalid: {', '.join(invalid)}. Choose from: {', '.join(options)}")
                continue
            return ",".join(picks)
        return answer


def _parse_priority_muscles(text: str) -> list[VolumeMuscle]:
    """Parse free-text priority muscles into VolumeMuscle list."""
    text = text.lower()
    if text in ("none", "no", "n/a", ""):
        return []

    mapping = {
        "chest": VolumeMuscle.CHEST,
        "back": VolumeMuscle.BACK,
        "bicep": VolumeMuscle.BICEPS,
        "arm": VolumeMuscle.BICEPS,
        "tricep": VolumeMuscle.TRICEPS,
        "shoulder": VolumeMuscle.SIDE_REAR_DELTS,
        "delt": VolumeMuscle.SIDE_REAR_DELTS,
        "quad": VolumeMuscle.QUADS,
        "leg": VolumeMuscle.QUADS,
        "ham": VolumeMuscle.HAMSTRINGS,
        "glute": VolumeMuscle.GLUTES,
        "calf": VolumeMuscle.CALVES,
        "calves": VolumeMuscle.CALVES,
        "ab": VolumeMuscle.ABS,
        "core": VolumeMuscle.ABS,
    }

    found: list[VolumeMuscle] = []
    for keyword, muscle in mapping.items():
        if keyword in text and muscle not in found:
            found.append(muscle)

    if "arm" in text:
        if VolumeMuscle.TRICEPS not in found:
            found.append(VolumeMuscle.TRICEPS)

    return found


def _ask_equipment_multiselect() -> set[Equipment]:
    """Prompt the user to pick the equipment they have available."""
    letters = [opt[0] for opt in EQUIPMENT_OPTIONS]
    label_lines = "\n".join(f"  ({l}) {label}" for l, _, label in EQUIPMENT_OPTIONS)
    prompt = (
        "Which equipment do you actually have? Pick all that apply (comma-separated).\n"
        f"{label_lines}"
    )
    answer = _ask(prompt, options=letters, multi_select=True)
    if not answer:
        return {Equipment.BODYWEIGHT}
    picks = {p.strip() for p in answer.split(",") if p.strip()}
    selected = {eq for letter, eq, _ in EQUIPMENT_OPTIONS if letter in picks}
    return selected or {Equipment.BODYWEIGHT}


def run_intake() -> UserProfile:
    """Run the full intake questionnaire and return a UserProfile."""
    profile = UserProfile()

    print("=" * 60)
    print("  IRONFORGE — Evidence-Based Workout Program Designer")
    print("=" * 60)
    print("\nI'll ask you a series of questions to build your program.")
    print("Answer each one before we proceed.\n")

    for block_name, questions in ALL_BLOCKS:
        print(f"\n{'─' * 40}")
        print(f"  {block_name}")
        print(f"{'─' * 40}")

        for q in questions:
            answer = _ask(q.prompt, q.options, q.multi_select)

            if q.key == "priority_muscles":
                profile.priority_muscles = _parse_priority_muscles(answer)
                if VolumeMuscle.GLUTES in profile.priority_muscles:
                    profile.wants_glute_focus = True

            elif q.key == "caloric_phase":
                profile.caloric_phase = {
                    "a": CaloricPhase.SURPLUS, "b": CaloricPhase.DEFICIT,
                    "c": CaloricPhase.MAINTENANCE,
                }[answer]

            elif q.key == "training_months":
                profile.training_months = {"a": 3, "b": 18, "c": 48}[answer]

            elif q.key == "days_per_week":
                profile.days_per_week = {"a": 3, "b": 4, "c": 5, "d": 6}[answer]

            elif q.key == "session_minutes":
                profile.session_minutes = {
                    "a": 40, "b": 52, "c": 67, "d": 82, "e": 95,
                }[answer]

            elif q.key == "prefers_supersets":
                profile.prefers_supersets = answer in ("a", "c")

            elif q.key == "equipment_access":
                profile.equipment_access = {
                    "a": EquipmentAccess.FULL_GYM,
                    "b": EquipmentAccess.LIMITED_GYM,
                    "c": EquipmentAccess.HOME_GYM,
                }[answer]
                if profile.equipment_access != EquipmentAccess.FULL_GYM:
                    profile.available_equipment = _ask_equipment_multiselect()
                # Full gym keeps the dataclass default (everything).

            elif q.key == "sex":
                profile.sex = {"a": Sex.MALE, "b": Sex.FEMALE}[answer]

            elif q.key == "injuries":
                if not answer:
                    profile.injuries = []
                else:
                    picks = [p.strip() for p in answer.split(",") if p.strip()]
                    profile.injuries = [
                        INJURY_LETTER_MAP[p] for p in picks if p in INJURY_LETTER_MAP
                    ]

    print(f"\n{'─' * 40}")
    print("  Intake complete! Generating your program...")
    print(f"{'─' * 40}\n")

    return profile
