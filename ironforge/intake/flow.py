"""Conversational intake engine — walks through questions, builds UserProfile."""

from ironforge.data.muscle_groups import (
    Goal, Sex, CaloricPhase, EquipmentAccess, Equipment,
    MovementPattern, TrainingLevel, VolumeMuscle,
)
from ironforge.intake.profile import UserProfile
from ironforge.intake.questions import ALL_BLOCKS


def _ask(prompt: str, options: list[str] | None = None) -> str:
    """Ask a question and validate input."""
    print()
    print(prompt)
    while True:
        answer = input("\n> ").strip().lower()
        if not answer:
            print("Please enter a response.")
            continue
        if options and answer not in options:
            print(f"Please enter one of: {', '.join(options)}")
            continue
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

    # If "arms" mentioned, add both biceps and triceps
    if "arm" in text:
        if VolumeMuscle.TRICEPS not in found:
            found.append(VolumeMuscle.TRICEPS)

    return found


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
            answer = _ask(q.prompt, q.options)

            # ── Parse answers into profile ──
            if q.key == "primary_goal":
                profile.primary_goal = {
                    "a": Goal.HYPERTROPHY, "b": Goal.STRENGTH,
                    "c": Goal.HYBRID, "d": Goal.RECOMP,
                }[answer]

            elif q.key == "priority_muscles":
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

            elif q.key == "progression_rate":
                if answer == "a":
                    profile.can_add_weight_every_session = True
                elif answer == "b":
                    profile.adds_weight_every_1_2_weeks = True

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
                    "d": EquipmentAccess.OTHER,
                }[answer]
                # Set available equipment based on access
                if profile.equipment_access == EquipmentAccess.HOME_GYM:
                    profile.available_equipment = {
                        Equipment.BARBELL, Equipment.DUMBBELL,
                        Equipment.EZ_BAR, Equipment.BODYWEIGHT,
                    }
                elif profile.equipment_access == EquipmentAccess.LIMITED_GYM:
                    profile.available_equipment = {
                        Equipment.BARBELL, Equipment.DUMBBELL,
                        Equipment.CABLE, Equipment.EZ_BAR,
                        Equipment.BODYWEIGHT, Equipment.MACHINE,
                    }
                # Full gym keeps the default (everything)

            elif q.key == "sex":
                profile.sex = {"a": Sex.MALE, "b": Sex.FEMALE}[answer]

            elif q.key == "injuries":
                if answer.lower() not in ("none", "no", "n/a"):
                    profile.injuries = [answer]

            elif q.key == "current_sets":
                try:
                    profile.current_sets_per_muscle = int(answer)
                except ValueError:
                    profile.current_sets_per_muscle = 0

            elif q.key == "current_program":
                profile.current_program = answer

    print(f"\n{'─' * 40}")
    print("  Intake complete! Generating your program...")
    print(f"{'─' * 40}\n")

    return profile
