"""Algorithm constants: volume landmarks, rep ranges, RIR targets, rest periods."""

from ironforge.data.muscle_groups import VolumeMuscle, Tier, TrainingLevel
from dataclasses import dataclass


@dataclass(frozen=True)
class VolumeLandmarks:
    mev_low: float
    mev_high: float
    mav_low: float
    mav_high: float
    mrv: float


# Volume landmarks in fractional sets per week
VOLUME_LANDMARKS: dict[VolumeMuscle, VolumeLandmarks] = {
    VolumeMuscle.QUADS:          VolumeLandmarks(4, 6, 6, 14, 18),
    VolumeMuscle.CHEST:          VolumeLandmarks(10, 10, 12, 20, 22),
    VolumeMuscle.BACK:           VolumeLandmarks(8, 8, 10, 20, 25),
    VolumeMuscle.BICEPS:         VolumeLandmarks(8, 8, 14, 20, 20),
    VolumeMuscle.SIDE_REAR_DELTS: VolumeLandmarks(8, 8, 16, 22, 26),
    VolumeMuscle.HAMSTRINGS:     VolumeLandmarks(4, 6, 6, 12, 16),
    VolumeMuscle.TRICEPS:        VolumeLandmarks(4, 4, 8, 18, 18),
    VolumeMuscle.CALVES:         VolumeLandmarks(12, 12, 12, 18, 20),
    VolumeMuscle.GLUTES:         VolumeLandmarks(4, 6, 6, 14, 18),
    VolumeMuscle.ABS:            VolumeLandmarks(2, 4, 4, 10, 14),
    VolumeMuscle.FOREARMS:       VolumeLandmarks(2, 2, 4, 8, 10),
}


# Rep ranges by tier — all capped to 4-10
REP_RANGES: dict[Tier, tuple[int, int]] = {
    Tier.T1: (4, 6),
    Tier.T2: (6, 8),
    Tier.T3: (8, 10),
}

# Female bias: slightly higher within the 4-10 window
REP_RANGES_FEMALE: dict[Tier, tuple[int, int]] = {
    Tier.T1: (5, 8),
    Tier.T2: (6, 10),
    Tier.T3: (8, 10),
}


# RIR targets by week of mesocycle (1-indexed)
RIR_BY_WEEK: dict[int, int] = {
    1: 3,
    2: 2,
    3: 2,
    4: 1,
}

RIR_DELOAD: int = 5

# Beginner RIR override (their calibration is off by 3-5 reps)
RIR_BEGINNER: int = 3

# Rest periods in seconds (min, max)
REST_PERIODS: dict[Tier, tuple[int, int]] = {
    Tier.T1: (120, 180),
    Tier.T2: (120, 150),
    Tier.T3: (90, 120),
}

# Per-session ceiling: direct hard sets per muscle
PER_SESSION_DIRECT_CEILING = 8
PER_SESSION_FRACTIONAL_CEILING = 11

# Maximum sets per exercise per session
MAX_SETS_PER_EXERCISE = 3

# Compound spillover contributions (fractional sets)
# Maps from exercise muscle group categories to secondary contributions
COMPOUND_SPILLOVER = {
    "bench_press": {
        "primary": "chest",
        "secondary": {"triceps": 0.5, "front_delt": 0.5},
    },
    "overhead_press": {
        "primary": "front_delt",
        "secondary": {"triceps": 0.5, "side_delt": 0.3},
    },
    "row": {
        "primary": "back",
        "secondary": {"biceps": 0.5, "rear_delt": 0.3},
    },
    "pulldown": {
        "primary": "lats",
        "secondary": {"biceps": 0.5},
    },
    "squat": {
        "primary": "quads",
        "secondary": {"glutes": 0.5},
    },
    "rdl": {
        "primary": "hamstrings",
        "secondary": {"glutes": 0.5, "spinal_erectors": 0.5},
    },
    "hip_thrust": {
        "primary": "glutes",
        "secondary": {},
    },
    "dip": {
        "primary": "chest",
        "secondary": {"triceps": 0.5},
    },
}


# Split templates by days per week
SPLIT_TEMPLATES = {
    3: "full_body",
    4: "upper_lower",
    5: "ul_ppl_hybrid",
    6: "ppl",
}

# Deload frequency by training level (weeks between deloads)
DELOAD_FREQUENCY: dict[TrainingLevel, tuple[int, int]] = {
    TrainingLevel.BEGINNER: (8, 12),
    TrainingLevel.INTERMEDIATE: (4, 6),
    TrainingLevel.ADVANCED: (3, 5),
}

# Mesocycle length (training weeks only — no forced deload)
MESO_LENGTH = 4
