"""Volume calculator — fractional sets, MEV/MAV/MRV landmarks."""

from ironforge.data.muscle_groups import (
    MovementPattern, TrainingLevel, VolumeMuscle, CaloricPhase, Goal,
)
from ironforge.data.constants import VOLUME_LANDMARKS
from ironforge.intake.profile import UserProfile
from ironforge.program.models import VolumeTarget


def compute_volume(
    profile: UserProfile,
    levels: dict[MovementPattern, TrainingLevel],
) -> list[VolumeTarget]:
    """Compute weekly fractional set targets for each muscle group, starting at MEV."""
    overall = profile.overall_level
    targets: list[VolumeTarget] = []

    for muscle, landmarks in VOLUME_LANDMARKS.items():
        mev = (landmarks.mev_low + landmarks.mev_high) / 2
        mrv = landmarks.mrv

        # Start at MEV for week 1 (mesocycle start)
        working = mev

        # Priority muscles: bump toward low-MAV
        if muscle in profile.priority_muscles:
            working = landmarks.mav_low

        # Don't exceed 30% above habitual baseline
        if profile.current_sets_per_muscle > 0:
            max_allowed = profile.current_sets_per_muscle * 1.3
            working = min(working, max_allowed)

        # In deficit: keep at MEV minimum, don't over-reach
        if profile.caloric_phase == CaloricPhase.DEFICIT:
            working = max(mev, min(working, landmarks.mav_low))

        # Advanced lifters: quality over quantity
        if overall == TrainingLevel.ADVANCED:
            working = min(working, landmarks.mav_high)

        # Ensure at least MEV
        working = max(working, mev)

        targets.append(VolumeTarget(
            muscle=muscle,
            mev=mev,
            working=round(working, 1),
            mrv=mrv,
        ))

    return targets
