"""Antagonist superset pairing logic."""

from ironforge.data.muscle_groups import VolumeMuscle, Tier
from ironforge.program.models import ProgrammedExercise


# Antagonist pairs for superset matching
ANTAGONIST_PAIRS: list[tuple[VolumeMuscle, VolumeMuscle]] = [
    (VolumeMuscle.CHEST, VolumeMuscle.BACK),
    (VolumeMuscle.BICEPS, VolumeMuscle.TRICEPS),
    (VolumeMuscle.QUADS, VolumeMuscle.HAMSTRINGS),
    (VolumeMuscle.SIDE_REAR_DELTS, VolumeMuscle.BACK),
]

# Reverse mapping for quick lookup
_PAIR_MAP: dict[VolumeMuscle, VolumeMuscle] = {}
for a, b in ANTAGONIST_PAIRS:
    _PAIR_MAP[a] = b
    _PAIR_MAP[b] = a


def _muscle_to_volume_muscle(ex: ProgrammedExercise) -> VolumeMuscle | None:
    """Map an exercise's primary muscle to a VolumeMuscle for pairing."""
    from ironforge.data.muscle_groups import MuscleGroup, VOLUME_MUSCLE_MAP
    primary = ex.exercise.primary
    for vm, muscles in VOLUME_MUSCLE_MAP.items():
        if primary in muscles:
            return vm
    return None


def pair_supersets(
    exercises: list[ProgrammedExercise],
    allow_supersets: bool = True,
) -> list[ProgrammedExercise]:
    """Assign superset pair IDs to antagonist exercises.

    T1 compounds are never supersetted — they are always done as straight sets.
    Returns the same list with superset_pair_id set on paired exercises.
    """
    if not allow_supersets:
        return exercises

    # Separate T1 (always straight) from T2/T3 (can be supersetted)
    straight = [e for e in exercises if e.tier == Tier.T1]
    candidates = [e for e in exercises if e.tier != Tier.T1]

    pair_id = 1
    paired: set[int] = set()

    for i, ex_a in enumerate(candidates):
        if i in paired:
            continue
        vm_a = _muscle_to_volume_muscle(ex_a)
        if vm_a is None or vm_a not in _PAIR_MAP:
            continue

        target_vm = _PAIR_MAP[vm_a]
        for j, ex_b in enumerate(candidates):
            if j <= i or j in paired:
                continue
            vm_b = _muscle_to_volume_muscle(ex_b)
            if vm_b == target_vm:
                ex_a.superset_pair_id = pair_id
                ex_b.superset_pair_id = pair_id
                paired.add(i)
                paired.add(j)
                pair_id += 1
                break

    return straight + candidates
