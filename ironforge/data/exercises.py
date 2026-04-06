"""Approved exercise database — 97 exercises with metadata."""

from dataclasses import dataclass, field
from ironforge.data.muscle_groups import (
    MuscleGroup, MovementPattern, Tier, Equipment,
)


@dataclass(frozen=True)
class ExerciseDefinition:
    name: str
    primary: MuscleGroup
    secondary: tuple[tuple[MuscleGroup, float], ...] = ()
    pattern: MovementPattern = MovementPattern.ISOLATION
    tier: Tier = Tier.T3
    equipment: tuple[Equipment, ...] = (Equipment.MACHINE,)
    bilateral: bool = True
    notes: str = ""
    tags: tuple[str, ...] = ()


def _ex(name, primary, *, secondary=(), pattern=MovementPattern.ISOLATION,
         tier=Tier.T3, equipment=(Equipment.MACHINE,), bilateral=True,
         notes="", tags=()):
    return ExerciseDefinition(
        name=name, primary=primary,
        secondary=tuple(secondary),
        pattern=pattern, tier=tier,
        equipment=tuple(equipment),
        bilateral=bilateral, notes=notes,
        tags=tuple(tags),
    )


# ─── CHEST ───────────────────────────────────────────────────────────────────

INCLINE_SMITH_BENCH = _ex(
    "Incline Smith Bench Press", MuscleGroup.CHEST_CLAVICULAR,
    secondary=((MuscleGroup.TRICEPS_LATERAL, 0.5), (MuscleGroup.FRONT_DELT, 0.5)),
    pattern=MovementPattern.HORIZONTAL_PUSH, tier=Tier.T1,
    equipment=(Equipment.SMITH_MACHINE,),
    tags=("upper_chest", "press"),
)
SMITH_CHEST_PRESS = _ex(
    "Smith Guided Chest Press", MuscleGroup.CHEST_STERNAL,
    secondary=((MuscleGroup.TRICEPS_LATERAL, 0.5), (MuscleGroup.FRONT_DELT, 0.5)),
    pattern=MovementPattern.HORIZONTAL_PUSH, tier=Tier.T1,
    equipment=(Equipment.SMITH_MACHINE,),
    tags=("flat_chest", "press"),
)
INCLINE_BENCH = _ex(
    "Incline Bench", MuscleGroup.CHEST_CLAVICULAR,
    secondary=((MuscleGroup.TRICEPS_LATERAL, 0.5), (MuscleGroup.FRONT_DELT, 0.5)),
    pattern=MovementPattern.HORIZONTAL_PUSH, tier=Tier.T1,
    equipment=(Equipment.BARBELL,),
    tags=("upper_chest", "press"),
)
FLAT_BENCH = _ex(
    "Flat Bench", MuscleGroup.CHEST_STERNAL,
    secondary=((MuscleGroup.TRICEPS_LATERAL, 0.5), (MuscleGroup.FRONT_DELT, 0.5)),
    pattern=MovementPattern.HORIZONTAL_PUSH, tier=Tier.T1,
    equipment=(Equipment.BARBELL,),
    tags=("flat_chest", "press"),
)
INCLINE_DB_PRESS = _ex(
    "Incline Dumbbell Press", MuscleGroup.CHEST_CLAVICULAR,
    secondary=((MuscleGroup.TRICEPS_LATERAL, 0.5), (MuscleGroup.FRONT_DELT, 0.5)),
    pattern=MovementPattern.HORIZONTAL_PUSH, tier=Tier.T2,
    equipment=(Equipment.DUMBBELL,),
    tags=("upper_chest", "press"),
)
FLAT_DB_PRESS = _ex(
    "Flat Dumbbell Press", MuscleGroup.CHEST_STERNAL,
    secondary=((MuscleGroup.TRICEPS_LATERAL, 0.5), (MuscleGroup.FRONT_DELT, 0.5)),
    pattern=MovementPattern.HORIZONTAL_PUSH, tier=Tier.T2,
    equipment=(Equipment.DUMBBELL,),
    tags=("flat_chest", "press"),
)
DB_BENCH = _ex(
    "Dumbbell Bench", MuscleGroup.CHEST_STERNAL,
    secondary=((MuscleGroup.TRICEPS_LATERAL, 0.5), (MuscleGroup.FRONT_DELT, 0.5)),
    pattern=MovementPattern.HORIZONTAL_PUSH, tier=Tier.T2,
    equipment=(Equipment.DUMBBELL,),
    tags=("flat_chest", "press"),
)
FLAT_BENCH_CABLES = _ex(
    "Flat Bench Cables", MuscleGroup.CHEST_STERNAL,
    pattern=MovementPattern.HORIZONTAL_PUSH, tier=Tier.T3,
    equipment=(Equipment.CABLE,),
    tags=("flat_chest", "fly"),
)
LOW_CHEST_CABLE_FLY = _ex(
    "Low Chest Cable Fly", MuscleGroup.CHEST_STERNAL,
    equipment=(Equipment.CABLE,),
    tags=("flat_chest", "fly", "lower_chest"),
)
MID_CHEST_CABLE_FLY = _ex(
    "Mid Chest Cable Fly", MuscleGroup.CHEST_STERNAL,
    equipment=(Equipment.CABLE,),
    tags=("flat_chest", "fly"),
)
UPPER_CHEST_CABLE_FLY = _ex(
    "Upper Chest Cable Fly", MuscleGroup.CHEST_CLAVICULAR,
    equipment=(Equipment.CABLE,),
    tags=("upper_chest", "fly"),
)
CHEST_PRESS_MACHINE = _ex(
    "Chest Press Machine", MuscleGroup.CHEST_STERNAL,
    secondary=((MuscleGroup.TRICEPS_LATERAL, 0.5), (MuscleGroup.FRONT_DELT, 0.5)),
    pattern=MovementPattern.HORIZONTAL_PUSH, tier=Tier.T2,
    equipment=(Equipment.MACHINE,),
    tags=("flat_chest", "press"),
)
INCLINE_MACHINE_PRESS = _ex(
    "Incline Machine Chest Press", MuscleGroup.CHEST_CLAVICULAR,
    secondary=((MuscleGroup.TRICEPS_LATERAL, 0.5), (MuscleGroup.FRONT_DELT, 0.5)),
    pattern=MovementPattern.HORIZONTAL_PUSH, tier=Tier.T2,
    equipment=(Equipment.MACHINE,),
    tags=("upper_chest", "press"),
)
PEC_DECK = _ex(
    "Pec Deck", MuscleGroup.CHEST_STERNAL,
    equipment=(Equipment.MACHINE,),
    tags=("flat_chest", "fly"),
)
UPPER_CHEST_PEC_DECK = _ex(
    "Upper Chest Pec Deck", MuscleGroup.CHEST_CLAVICULAR,
    equipment=(Equipment.MACHINE,),
    tags=("upper_chest", "fly"),
)

# ─── SHOULDERS ───────────────────────────────────────────────────────────────

SHOULDER_PRESS_MACHINE = _ex(
    "Shoulder Press Machine", MuscleGroup.FRONT_DELT,
    secondary=((MuscleGroup.TRICEPS_LATERAL, 0.5), (MuscleGroup.SIDE_DELT, 0.3)),
    pattern=MovementPattern.VERTICAL_PUSH, tier=Tier.T2,
    equipment=(Equipment.MACHINE,),
    tags=("ohp",),
)
SHOULDER_PRESS = _ex(
    "Shoulder Press", MuscleGroup.FRONT_DELT,
    secondary=((MuscleGroup.TRICEPS_LATERAL, 0.5), (MuscleGroup.SIDE_DELT, 0.3)),
    pattern=MovementPattern.VERTICAL_PUSH, tier=Tier.T1,
    equipment=(Equipment.DUMBBELL,),
    tags=("ohp",),
)
LATERAL_RAISE_MACHINE = _ex(
    "Lateral Raise Machine", MuscleGroup.SIDE_DELT,
    equipment=(Equipment.MACHINE,),
    tags=("side_delt",),
)
LATERAL_RAISE = _ex(
    "Lateral Raise", MuscleGroup.SIDE_DELT,
    equipment=(Equipment.DUMBBELL,),
    tags=("side_delt",),
)
LATERAL_RAISE_CABLE = _ex(
    "Lateral Raise with Cable", MuscleGroup.SIDE_DELT,
    equipment=(Equipment.CABLE,),
    tags=("side_delt",),
)
REAR_DELT_FLY = _ex(
    "Rear Delt Fly", MuscleGroup.REAR_DELT,
    equipment=(Equipment.DUMBBELL,),
    tags=("rear_delt",),
)
REAR_DELT_FLY_SUPPORTED = _ex(
    "Rear Delt Fly with Chest Support", MuscleGroup.REAR_DELT,
    equipment=(Equipment.DUMBBELL,),
    tags=("rear_delt", "chest_supported"),
)
CABLE_FACE_PULL = _ex(
    "Cable Face Pull", MuscleGroup.REAR_DELT,
    equipment=(Equipment.CABLE,),
    tags=("rear_delt", "health_accessory"),
    notes="Health accessory only — not primary rear delt volume",
)

# ─── TRICEPS ─────────────────────────────────────────────────────────────────

DIP_MACHINE = _ex(
    "Dip Machine", MuscleGroup.TRICEPS_LATERAL,
    secondary=((MuscleGroup.CHEST_STERNAL, 0.5),),
    pattern=MovementPattern.HORIZONTAL_PUSH, tier=Tier.T2,
    equipment=(Equipment.MACHINE,),
    tags=("triceps", "compound"),
)
ROPE_TRICEP_EXT = _ex(
    "Rope Tricep Extension", MuscleGroup.TRICEPS_LATERAL,
    equipment=(Equipment.CABLE,),
    tags=("triceps", "pushdown"),
)
OH_ROPE_TRICEP_EXT = _ex(
    "Overhead Rope Tricep Extension", MuscleGroup.TRICEPS_LONG,
    equipment=(Equipment.CABLE,),
    tags=("triceps", "overhead", "long_head"),
)
STRAIGHT_BAR_TRICEP_EXT = _ex(
    "Straight Bar Tricep Extension", MuscleGroup.TRICEPS_LATERAL,
    equipment=(Equipment.CABLE,),
    tags=("triceps", "pushdown"),
)
OH_STRAIGHT_BAR_TRICEP_EXT = _ex(
    "Overhead Straight Bar Tricep Extension", MuscleGroup.TRICEPS_LONG,
    equipment=(Equipment.CABLE,),
    tags=("triceps", "overhead", "long_head"),
)
VBAR_TRICEP_EXT = _ex(
    "V-Bar Tricep Extension", MuscleGroup.TRICEPS_LATERAL,
    equipment=(Equipment.CABLE,),
    tags=("triceps", "pushdown"),
)
OH_VBAR_TRICEP_EXT = _ex(
    "Overhead V-Bar Tricep Extension", MuscleGroup.TRICEPS_LONG,
    equipment=(Equipment.CABLE,),
    tags=("triceps", "overhead", "long_head"),
)
SINGLE_ARM_DHANDLE_TRICEP = _ex(
    "Single Arm D-Handle Tricep Extension", MuscleGroup.TRICEPS_LATERAL,
    equipment=(Equipment.CABLE,), bilateral=False,
    tags=("triceps", "pushdown"),
)
OH_SINGLE_ARM_DB_EXT = _ex(
    "Overhead Single Arm Dumbbell Extension", MuscleGroup.TRICEPS_LONG,
    equipment=(Equipment.DUMBBELL,), bilateral=False,
    tags=("triceps", "overhead", "long_head"),
)
OH_EZ_BAR_TRICEP_EXT = _ex(
    "Overhead EZ Bar Tricep Extension", MuscleGroup.TRICEPS_LONG,
    equipment=(Equipment.EZ_BAR,),
    tags=("triceps", "overhead", "long_head"),
)
EZ_BAR_SKULL_CRUSHER = _ex(
    "EZ Bar Skull Crusher", MuscleGroup.TRICEPS_LONG,
    equipment=(Equipment.EZ_BAR,),
    tags=("triceps", "long_head", "heavy"),
)
EZ_BAR_JM_PRESS = _ex(
    "EZ Bar JM Press", MuscleGroup.TRICEPS_LONG,
    secondary=((MuscleGroup.TRICEPS_LATERAL, 0.5),),
    equipment=(Equipment.EZ_BAR,), tier=Tier.T2,
    tags=("triceps", "long_head", "heavy"),
)
SMITH_JM_PRESS = _ex(
    "Smith JM Press", MuscleGroup.TRICEPS_LONG,
    secondary=((MuscleGroup.TRICEPS_LATERAL, 0.5),),
    equipment=(Equipment.SMITH_MACHINE,), tier=Tier.T2,
    tags=("triceps", "long_head", "heavy"),
)

# ─── BICEPS ──────────────────────────────────────────────────────────────────

PREACHER_CURL = _ex(
    "Preacher Curl", MuscleGroup.BICEPS,
    equipment=(Equipment.DUMBBELL,),
    tags=("biceps", "distal"),
)
MACHINE_PREACHER_CURL = _ex(
    "Machine Preacher Curl", MuscleGroup.BICEPS,
    equipment=(Equipment.MACHINE,),
    tags=("biceps", "distal"),
)
EZ_BAR_PREACHER_CURL = _ex(
    "EZ Bar Preacher Curl", MuscleGroup.BICEPS,
    equipment=(Equipment.EZ_BAR,),
    tags=("biceps", "distal"),
)
SINGLE_ARM_DB_PREACHER = _ex(
    "Single Arm Dumbbell Preacher Curl", MuscleGroup.BICEPS,
    equipment=(Equipment.DUMBBELL,), bilateral=False,
    tags=("biceps", "distal"),
)
SPIDER_CURL = _ex(
    "Spider Curl", MuscleGroup.BICEPS,
    equipment=(Equipment.DUMBBELL,),
    tags=("biceps", "distal"),
)
INCLINE_DB_CURL = _ex(
    "Incline Bench Dumbbell Curl", MuscleGroup.BICEPS,
    equipment=(Equipment.DUMBBELL,),
    tags=("biceps", "proximal", "stretch"),
    notes="30° bench; primary stretch-position curl",
)
STANDING_ALT_DB_CURL = _ex(
    "Standing Alternating Dumbbell Curl", MuscleGroup.BICEPS,
    equipment=(Equipment.DUMBBELL,), bilateral=False,
    tags=("biceps", "general"),
)
HAMMER_CURL = _ex(
    "Hammer Curl", MuscleGroup.BRACHIALIS,
    equipment=(Equipment.DUMBBELL,),
    tags=("brachialis",),
    notes="Do NOT count as biceps volume",
)
SEATED_HAMMER_CURL = _ex(
    "Seated Hammer Curl", MuscleGroup.BRACHIALIS,
    equipment=(Equipment.DUMBBELL,),
    tags=("brachialis",),
    notes="Do NOT count as biceps volume",
)
BAYESIAN_CURL = _ex(
    "Bayesian Curl", MuscleGroup.BICEPS,
    equipment=(Equipment.CABLE,),
    tags=("biceps", "proximal", "stretch"),
    notes="Arm-behind-body position; excellent stretch-position curl",
)
EZ_BAR_CABLE_CURL = _ex(
    "EZ Bar Cable Curl", MuscleGroup.BICEPS,
    equipment=(Equipment.CABLE,),
    tags=("biceps", "general"),
)

# ─── BACK — VERTICAL PULLS ──────────────────────────────────────────────────

LAT_PULLDOWN_MACHINE = _ex(
    "Lat Pulldown Machine", MuscleGroup.LATS,
    secondary=((MuscleGroup.BICEPS, 0.5),),
    pattern=MovementPattern.VERTICAL_PULL, tier=Tier.T2,
    equipment=(Equipment.MACHINE,),
    tags=("vertical_pull", "lat"),
)
LAT_PULLDOWN_WIDE = _ex(
    "Lat Pulldown Wide Grip", MuscleGroup.LATS,
    secondary=((MuscleGroup.BICEPS, 0.5),),
    pattern=MovementPattern.VERTICAL_PULL, tier=Tier.T2,
    equipment=(Equipment.CABLE,),
    tags=("vertical_pull", "lat"),
)
LAT_PULLDOWN_NEUTRAL = _ex(
    "Lat Pulldown Neutral Grip", MuscleGroup.LATS,
    secondary=((MuscleGroup.BICEPS, 0.5),),
    pattern=MovementPattern.VERTICAL_PULL, tier=Tier.T2,
    equipment=(Equipment.CABLE,),
    tags=("vertical_pull", "lat"),
)
LAT_PULLDOWN_CLOSE = _ex(
    "Lat Pulldown Close Grip", MuscleGroup.LATS,
    secondary=((MuscleGroup.BICEPS, 0.5),),
    pattern=MovementPattern.VERTICAL_PULL, tier=Tier.T2,
    equipment=(Equipment.CABLE,),
    tags=("vertical_pull", "lat"),
)
SINGLE_ARM_LAT_PULLDOWN = _ex(
    "Single Arm Lat Pulldown", MuscleGroup.LATS,
    secondary=((MuscleGroup.BICEPS, 0.5),),
    pattern=MovementPattern.VERTICAL_PULL, tier=Tier.T2,
    equipment=(Equipment.CABLE,), bilateral=False,
    tags=("vertical_pull", "lat"),
)
PULLDOWN_ROW_MACHINE = _ex(
    "Pulldown & Row Machine", MuscleGroup.LATS,
    secondary=((MuscleGroup.BICEPS, 0.5), (MuscleGroup.MID_BACK, 0.5)),
    pattern=MovementPattern.VERTICAL_PULL, tier=Tier.T2,
    equipment=(Equipment.MACHINE,),
    tags=("vertical_pull", "lat", "row"),
)
EZ_BAR_CABLE_PULLOVER = _ex(
    "EZ Bar Cable Pullover", MuscleGroup.LATS,
    equipment=(Equipment.CABLE,),
    tags=("lat", "stretch"),
    notes="Stretch-focused lat exercise",
)
SINGLE_ARM_CABLE_PULLOVER = _ex(
    "Single Arm Cable Pullover", MuscleGroup.LATS,
    equipment=(Equipment.CABLE,), bilateral=False,
    tags=("lat", "stretch"),
    notes="Stretch-focused lat exercise",
)
FLAT_PULLOVER_MACHINE = _ex(
    "Flat Pullover Machine", MuscleGroup.LATS,
    equipment=(Equipment.MACHINE,),
    tags=("lat", "stretch"),
    notes="Stretch-focused lat exercise",
)

# ─── BACK — HORIZONTAL ROWS ─────────────────────────────────────────────────

TBAR_ROW = _ex(
    "T-Bar Row", MuscleGroup.MID_BACK,
    secondary=((MuscleGroup.LATS, 0.5), (MuscleGroup.BICEPS, 0.5)),
    pattern=MovementPattern.HORIZONTAL_PULL, tier=Tier.T1,
    equipment=(Equipment.BARBELL,),
    tags=("row", "mid_back"),
)
SMITH_BARBELL_ROW = _ex(
    "Smith Machine Barbell Row", MuscleGroup.MID_BACK,
    secondary=((MuscleGroup.LATS, 0.5), (MuscleGroup.BICEPS, 0.5)),
    pattern=MovementPattern.HORIZONTAL_PULL, tier=Tier.T1,
    equipment=(Equipment.SMITH_MACHINE,),
    tags=("row", "mid_back"),
    notes="Do not program above 20 reps",
)
BARBELL_ROW = _ex(
    "Barbell Row", MuscleGroup.MID_BACK,
    secondary=((MuscleGroup.LATS, 0.5), (MuscleGroup.BICEPS, 0.5)),
    pattern=MovementPattern.HORIZONTAL_PULL, tier=Tier.T1,
    equipment=(Equipment.BARBELL,),
    tags=("row", "mid_back"),
    notes="Do not program above 20 reps",
)
SEATED_CHEST_SUPPORTED_ROW = _ex(
    "Seated Chest-Supported Row", MuscleGroup.MID_BACK,
    secondary=((MuscleGroup.LATS, 0.5), (MuscleGroup.BICEPS, 0.5)),
    pattern=MovementPattern.HORIZONTAL_PULL, tier=Tier.T2,
    equipment=(Equipment.MACHINE,),
    tags=("row", "mid_back", "chest_supported"),
    notes="Preferred for stability and stretch",
)
CHEST_SUPPORTED_ELBOWS_TUCKED = _ex(
    "Chest Supported Elbows Tucked Row", MuscleGroup.LATS,
    secondary=((MuscleGroup.BICEPS, 0.5),),
    pattern=MovementPattern.HORIZONTAL_PULL, tier=Tier.T2,
    equipment=(Equipment.MACHINE,),
    tags=("row", "lat_emphasis", "chest_supported"),
)
CHEST_SUPPORTED_ELBOWS_FLARED = _ex(
    "Chest Supported Elbows Flared Row", MuscleGroup.MID_BACK,
    secondary=((MuscleGroup.REAR_DELT, 0.5), (MuscleGroup.BICEPS, 0.5)),
    pattern=MovementPattern.HORIZONTAL_PULL, tier=Tier.T2,
    equipment=(Equipment.MACHINE,),
    tags=("row", "mid_back", "rear_delt", "chest_supported"),
)
SINGLE_ARM_CABLE_ROW = _ex(
    "Single Arm Cable Row", MuscleGroup.MID_BACK,
    secondary=((MuscleGroup.LATS, 0.5), (MuscleGroup.BICEPS, 0.5)),
    pattern=MovementPattern.HORIZONTAL_PULL, tier=Tier.T2,
    equipment=(Equipment.CABLE,), bilateral=False,
    tags=("row", "mid_back"),
)
WIDE_GRIP_CABLE_ROW = _ex(
    "Wide Grip Cable Row", MuscleGroup.MID_BACK,
    secondary=((MuscleGroup.REAR_DELT, 0.5), (MuscleGroup.BICEPS, 0.5)),
    pattern=MovementPattern.HORIZONTAL_PULL, tier=Tier.T2,
    equipment=(Equipment.CABLE,),
    tags=("row", "mid_back", "rear_delt"),
)
DB_ROW_TO_HIP = _ex(
    "Dumbbell Row to Hip", MuscleGroup.LATS,
    secondary=((MuscleGroup.BICEPS, 0.5),),
    pattern=MovementPattern.HORIZONTAL_PULL, tier=Tier.T2,
    equipment=(Equipment.DUMBBELL,), bilateral=False,
    tags=("row", "lat_emphasis"),
)
ROW_MACHINE = _ex(
    "Row Machine", MuscleGroup.MID_BACK,
    secondary=((MuscleGroup.LATS, 0.5), (MuscleGroup.BICEPS, 0.5)),
    pattern=MovementPattern.HORIZONTAL_PULL, tier=Tier.T2,
    equipment=(Equipment.MACHINE,),
    tags=("row", "mid_back"),
)

# ─── BACK — TRAPS / ACCESSORY ───────────────────────────────────────────────

DB_SHRUG = _ex(
    "DB Shrug", MuscleGroup.UPPER_TRAP,
    equipment=(Equipment.DUMBBELL,),
    tags=("trap",),
)
BACK_EXTENSION = _ex(
    "Back Extension / Hyperextension", MuscleGroup.SPINAL_ERECTORS,
    secondary=((MuscleGroup.GLUTES, 0.3), (MuscleGroup.HAMSTRINGS, 0.3)),
    equipment=(Equipment.BODYWEIGHT,),
    tags=("lower_back", "lower_trap_sub"),
    notes="Use Y-raise arm variation for lower trap work if possible",
)

# ─── LEGS — QUADS ────────────────────────────────────────────────────────────

BARBELL_SQUAT = _ex(
    "Barbell Squat", MuscleGroup.QUADS,
    secondary=((MuscleGroup.GLUTES, 0.5),),
    pattern=MovementPattern.SQUAT, tier=Tier.T1,
    equipment=(Equipment.BARBELL,),
    tags=("squat", "quad"),
    notes="High-bar, full depth",
)
SMITH_SQUAT = _ex(
    "Smith Machine Squat", MuscleGroup.QUADS,
    secondary=((MuscleGroup.GLUTES, 0.5),),
    pattern=MovementPattern.SQUAT, tier=Tier.T1,
    equipment=(Equipment.SMITH_MACHINE,),
    tags=("squat", "quad"),
)
SQUAT_RACK = _ex(
    "Squat Rack", MuscleGroup.QUADS,
    secondary=((MuscleGroup.GLUTES, 0.5),),
    pattern=MovementPattern.SQUAT, tier=Tier.T1,
    equipment=(Equipment.BARBELL,),
    tags=("squat", "quad"),
)
HACK_SQUAT = _ex(
    "Hack Squat", MuscleGroup.QUADS,
    pattern=MovementPattern.SQUAT, tier=Tier.T2,
    equipment=(Equipment.MACHINE,),
    tags=("squat", "quad", "quad_isolator"),
)
HACK_SQUAT_MACHINE = _ex(
    "Hack Squat Machine", MuscleGroup.QUADS,
    pattern=MovementPattern.SQUAT, tier=Tier.T2,
    equipment=(Equipment.MACHINE,),
    tags=("squat", "quad", "quad_isolator"),
    notes="Purest quad isolator; 8-15+ reps",
)
BELT_SQUAT = _ex(
    "Belt Squat", MuscleGroup.QUADS,
    secondary=((MuscleGroup.GLUTES, 0.3),),
    pattern=MovementPattern.SQUAT, tier=Tier.T2,
    equipment=(Equipment.MACHINE,),
    tags=("squat", "quad"),
)
PENDULUM_SQUAT = _ex(
    "Pendulum Squat", MuscleGroup.QUADS,
    pattern=MovementPattern.SQUAT, tier=Tier.T2,
    equipment=(Equipment.MACHINE,),
    tags=("squat", "quad"),
)
BULGARIAN_SPLIT_SQUAT = _ex(
    "Bulgarian Split Squat", MuscleGroup.QUADS,
    secondary=((MuscleGroup.GLUTES, 0.5),),
    pattern=MovementPattern.SQUAT, tier=Tier.T2,
    equipment=(Equipment.DUMBBELL,), bilateral=False,
    tags=("squat", "quad", "glute", "unilateral"),
)
SMITH_BULGARIAN = _ex(
    "Smith Machine Bulgarian Split Squat", MuscleGroup.QUADS,
    secondary=((MuscleGroup.GLUTES, 0.5),),
    pattern=MovementPattern.SQUAT, tier=Tier.T2,
    equipment=(Equipment.SMITH_MACHINE,), bilateral=False,
    tags=("squat", "quad", "glute", "unilateral"),
)
LEG_PRESS = _ex(
    "Leg Press", MuscleGroup.QUADS,
    secondary=((MuscleGroup.GLUTES, 0.3),),
    pattern=MovementPattern.SQUAT, tier=Tier.T2,
    equipment=(Equipment.MACHINE,),
    tags=("squat", "quad"),
    notes="VL-dominant; pair with leg extension",
)
LEG_PRESS_ELEVATED = _ex(
    "Leg Press Feet Elevated", MuscleGroup.QUADS,
    secondary=((MuscleGroup.GLUTES, 0.5), (MuscleGroup.HAMSTRINGS, 0.3)),
    pattern=MovementPattern.SQUAT, tier=Tier.T2,
    equipment=(Equipment.MACHINE,),
    tags=("squat", "quad", "glute"),
)
LEG_PRESS_LOWERED = _ex(
    "Leg Press Feet Lowered", MuscleGroup.QUADS,
    pattern=MovementPattern.SQUAT, tier=Tier.T2,
    equipment=(Equipment.MACHINE,),
    tags=("squat", "quad", "quad_bias"),
    notes="Increased quad bias",
)
LEG_EXTENSION = _ex(
    "Leg Extension", MuscleGroup.QUADS,
    pattern=MovementPattern.KNEE_EXTENSION, tier=Tier.T3,
    equipment=(Equipment.MACHINE,),
    tags=("quad", "isolation", "rf"),
    notes="MUST use reclined backrest (40° hip flexion) for RF growth",
)

# ─── LEGS — HAMSTRINGS ───────────────────────────────────────────────────────

RDL = _ex(
    "RDL", MuscleGroup.HAMSTRINGS,
    secondary=((MuscleGroup.GLUTES, 0.5), (MuscleGroup.SPINAL_ERECTORS, 0.5)),
    pattern=MovementPattern.HIP_HINGE, tier=Tier.T1,
    equipment=(Equipment.BARBELL,),
    tags=("hamstring", "hinge", "bflh"),
    notes="Mandatory hip extension component",
)
SLDL = _ex(
    "SLDL", MuscleGroup.HAMSTRINGS,
    secondary=((MuscleGroup.GLUTES, 0.5), (MuscleGroup.SPINAL_ERECTORS, 0.5)),
    pattern=MovementPattern.HIP_HINGE, tier=Tier.T1,
    equipment=(Equipment.BARBELL,),
    tags=("hamstring", "hinge", "bflh"),
    notes="Mandatory hip extension component",
)
LYING_HAM_CURL = _ex(
    "Lying Hamstring Curl", MuscleGroup.HAMSTRINGS,
    pattern=MovementPattern.KNEE_FLEXION,
    equipment=(Equipment.MACHINE,),
    tags=("hamstring", "curl"),
)
SEATED_HAM_CURL = _ex(
    "Seated Hamstring Curl", MuscleGroup.HAMSTRINGS,
    pattern=MovementPattern.KNEE_FLEXION,
    equipment=(Equipment.MACHINE,),
    tags=("hamstring", "curl", "primary"),
    notes="Primary hamstring exercise; 70-90% of curl volume; hip-flexed = BFlh stretch",
)
ROUNDED_BACK_HYPER = _ex(
    "Rounded Back Hyperextension", MuscleGroup.HAMSTRINGS,
    secondary=((MuscleGroup.GLUTES, 0.3),),
    pattern=MovementPattern.HIP_HINGE,
    equipment=(Equipment.BODYWEIGHT,),
    tags=("hamstring", "hinge"),
)

# ─── LEGS — GLUTES ───────────────────────────────────────────────────────────

HIP_THRUST = _ex(
    "Hip Thrust", MuscleGroup.GLUTES,
    pattern=MovementPattern.HIP_HINGE, tier=Tier.T2,
    equipment=(Equipment.BARBELL,),
    tags=("glute", "primary"),
    notes="Mandatory when glute growth is a goal; zero hamstring CSA change",
)
SMITH_HIP_THRUST = _ex(
    "Smith Machine Hip Thrust", MuscleGroup.GLUTES,
    pattern=MovementPattern.HIP_HINGE, tier=Tier.T2,
    equipment=(Equipment.SMITH_MACHINE,),
    tags=("glute", "primary"),
)
GLUTE_KICKBACK = _ex(
    "Glute Kickback", MuscleGroup.GLUTES,
    equipment=(Equipment.CABLE,),
    tags=("glute", "isolation"),
)
KICKBACK_MACHINE = _ex(
    "Kickback Machine", MuscleGroup.GLUTES,
    equipment=(Equipment.MACHINE,),
    tags=("glute", "isolation"),
)

# ─── CALVES ──────────────────────────────────────────────────────────────────

CALF_EXTENSION = _ex(
    "Calf Extension", MuscleGroup.CALVES,
    equipment=(Equipment.MACHINE,),
    tags=("calf", "gastrocnemius"),
    notes="Use standing/knee-extended; post-failure lengthened partials every set",
)
DONKEY_CALF_RAISE = _ex(
    "Donkey Calf Raise", MuscleGroup.CALVES,
    equipment=(Equipment.MACHINE,),
    tags=("calf", "gastrocnemius"),
    notes="Excellent stretch; post-failure lengthened partials every set",
)

# ─── ADDITIONAL ──────────────────────────────────────────────────────────────

AB_CURL_MACHINE = _ex(
    "Ab Curl Machine", MuscleGroup.ABS,
    equipment=(Equipment.MACHINE,),
    tags=("abs",),
)
ADDUCTOR_MACHINE = _ex(
    "Adductor Machine", MuscleGroup.ADDUCTORS,
    equipment=(Equipment.MACHINE,),
    tags=("adductor",),
)
ABDUCTOR_MACHINE = _ex(
    "Abductor Machine", MuscleGroup.ABDUCTORS,
    equipment=(Equipment.MACHINE,),
    tags=("abductor",),
)
FOREARM_WRIST_CURL = _ex(
    "Forearm Wrist Curl", MuscleGroup.FOREARMS,
    equipment=(Equipment.DUMBBELL,),
    tags=("forearm",),
)


# ─── MASTER LIST ─────────────────────────────────────────────────────────────

ALL_EXERCISES: list[ExerciseDefinition] = [
    # Chest
    INCLINE_SMITH_BENCH, SMITH_CHEST_PRESS, INCLINE_BENCH, FLAT_BENCH,
    INCLINE_DB_PRESS, FLAT_DB_PRESS, DB_BENCH, FLAT_BENCH_CABLES,
    LOW_CHEST_CABLE_FLY, MID_CHEST_CABLE_FLY, UPPER_CHEST_CABLE_FLY,
    CHEST_PRESS_MACHINE, INCLINE_MACHINE_PRESS, PEC_DECK,
    UPPER_CHEST_PEC_DECK,
    # Shoulders
    SHOULDER_PRESS_MACHINE, SHOULDER_PRESS, LATERAL_RAISE_MACHINE,
    LATERAL_RAISE, LATERAL_RAISE_CABLE, REAR_DELT_FLY,
    REAR_DELT_FLY_SUPPORTED, CABLE_FACE_PULL,
    # Triceps
    DIP_MACHINE, ROPE_TRICEP_EXT, OH_ROPE_TRICEP_EXT,
    STRAIGHT_BAR_TRICEP_EXT, OH_STRAIGHT_BAR_TRICEP_EXT,
    VBAR_TRICEP_EXT, OH_VBAR_TRICEP_EXT, SINGLE_ARM_DHANDLE_TRICEP,
    OH_SINGLE_ARM_DB_EXT, OH_EZ_BAR_TRICEP_EXT, EZ_BAR_SKULL_CRUSHER,
    EZ_BAR_JM_PRESS, SMITH_JM_PRESS,
    # Biceps
    PREACHER_CURL, MACHINE_PREACHER_CURL, EZ_BAR_PREACHER_CURL,
    SINGLE_ARM_DB_PREACHER, SPIDER_CURL, INCLINE_DB_CURL,
    STANDING_ALT_DB_CURL, HAMMER_CURL, SEATED_HAMMER_CURL,
    BAYESIAN_CURL, EZ_BAR_CABLE_CURL,
    # Back — Vertical
    LAT_PULLDOWN_MACHINE, LAT_PULLDOWN_WIDE, LAT_PULLDOWN_NEUTRAL,
    LAT_PULLDOWN_CLOSE, SINGLE_ARM_LAT_PULLDOWN, PULLDOWN_ROW_MACHINE,
    EZ_BAR_CABLE_PULLOVER, SINGLE_ARM_CABLE_PULLOVER,
    FLAT_PULLOVER_MACHINE,
    # Back — Horizontal
    TBAR_ROW, SMITH_BARBELL_ROW, BARBELL_ROW,
    SEATED_CHEST_SUPPORTED_ROW, CHEST_SUPPORTED_ELBOWS_TUCKED,
    CHEST_SUPPORTED_ELBOWS_FLARED, SINGLE_ARM_CABLE_ROW,
    WIDE_GRIP_CABLE_ROW, DB_ROW_TO_HIP, ROW_MACHINE,
    PULLDOWN_ROW_MACHINE,
    # Back — Accessory
    DB_SHRUG, BACK_EXTENSION,
    # Legs — Quads
    BARBELL_SQUAT, SMITH_SQUAT, SQUAT_RACK, HACK_SQUAT,
    HACK_SQUAT_MACHINE, BELT_SQUAT, PENDULUM_SQUAT,
    BULGARIAN_SPLIT_SQUAT, SMITH_BULGARIAN, LEG_PRESS,
    LEG_PRESS_ELEVATED, LEG_PRESS_LOWERED, LEG_EXTENSION,
    # Legs — Hamstrings
    RDL, SLDL, LYING_HAM_CURL, SEATED_HAM_CURL, ROUNDED_BACK_HYPER,
    # Legs — Glutes
    HIP_THRUST, SMITH_HIP_THRUST, GLUTE_KICKBACK, KICKBACK_MACHINE,
    # Calves
    CALF_EXTENSION, DONKEY_CALF_RAISE,
    # Additional
    AB_CURL_MACHINE, ADDUCTOR_MACHINE, ABDUCTOR_MACHINE,
    FOREARM_WRIST_CURL,
]


def exercises_by_muscle(muscle: MuscleGroup) -> list[ExerciseDefinition]:
    """Return all exercises where the given muscle is the primary target."""
    return [e for e in ALL_EXERCISES if e.primary == muscle]


def exercises_by_tag(tag: str) -> list[ExerciseDefinition]:
    """Return all exercises that have the given tag."""
    return [e for e in ALL_EXERCISES if tag in e.tags]


def exercises_for_equipment(
    available: set[Equipment],
) -> list[ExerciseDefinition]:
    """Return exercises usable with the given equipment set."""
    return [
        e for e in ALL_EXERCISES
        if any(eq in available for eq in e.equipment)
    ]
