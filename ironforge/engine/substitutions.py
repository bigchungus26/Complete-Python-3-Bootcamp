"""Exercise substitution groups — exercises that target the same region of the same muscle.

Used by the regenerate feature to swap exercises without changing the program's
muscle targeting. If a group has only 1 exercise, it's not substitutable.
"""

from ironforge.data.exercises import ExerciseDefinition, ALL_EXERCISES
from collections import defaultdict


def _region_tags(ex: ExerciseDefinition) -> tuple[str, ...]:
    """Extract region-identifying tags from an exercise."""
    REGION_TAGS = {
        'upper_chest', 'flat_chest', 'press', 'fly',
        'side_delt', 'rear_delt', 'overhead', 'long_head', 'pushdown',
        'proximal', 'distal', 'stretch', 'general', 'brachialis',
        'vertical_pull', 'lat', 'row', 'mid_back', 'lat_emphasis',
        'squat', 'quad', 'quad_isolator', 'rf',
        'hamstring', 'curl', 'hinge', 'bflh',
        'glute', 'calf', 'gastrocnemius',
    }
    return tuple(sorted(t for t in ex.tags if t in REGION_TAGS))


def _build_groups() -> dict[str, list[ExerciseDefinition]]:
    """Build substitution groups keyed by (primary_muscle, region_tags)."""
    groups: dict[tuple, list[ExerciseDefinition]] = defaultdict(list)
    seen_names: set[str] = set()
    for ex in ALL_EXERCISES:
        if ex.name in seen_names:
            continue
        seen_names.add(ex.name)
        key = (ex.primary.name, _region_tags(ex))
        groups[key].append(ex)
    # Convert to string keys for JSON-friendliness
    return {
        f"{muscle}|{'_'.join(tags) if tags else 'base'}": exercises
        for (muscle, tags), exercises in groups.items()
    }


SUBSTITUTION_GROUPS = _build_groups()

# Reverse lookup: exercise name → group key
EXERCISE_TO_GROUP: dict[str, str] = {}
for group_key, exercises in SUBSTITUTION_GROUPS.items():
    for ex in exercises:
        EXERCISE_TO_GROUP[ex.name] = group_key


def get_substitutes(exercise_name: str) -> list[ExerciseDefinition]:
    """Return all exercises that can substitute for the given one (same region)."""
    group_key = EXERCISE_TO_GROUP.get(exercise_name)
    if not group_key:
        return []
    return [ex for ex in SUBSTITUTION_GROUPS[group_key] if ex.name != exercise_name]


def is_substitutable(exercise_name: str) -> bool:
    """True if the exercise has at least one valid substitute."""
    return len(get_substitutes(exercise_name)) > 0
