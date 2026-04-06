"""Renders a Program to terminal output."""

from ironforge.program.models import Program, ProgrammedExercise


def _header(title: str) -> str:
    return f"\n{'=' * 60}\n  {title}\n{'=' * 60}\n"


def _subheader(title: str) -> str:
    return f"\n{'─' * 40}\n  {title}\n{'─' * 40}"


def _format_exercise(ex: ProgrammedExercise, idx: int) -> str:
    """Format a single exercise line."""
    load = ex.load
    tier_label = f"[T{ex.tier.value}]"
    superset = ""
    if ex.superset_pair_id is not None:
        superset = f"  [Superset {ex.superset_pair_id}]"

    line = (
        f"  {idx}. {tier_label} {ex.exercise.name}\n"
        f"     {load.sets} x {load.rep_low}-{load.rep_high} reps  |  "
        f"RIR {load.rir}  |  Rest {load.rest_seconds}s{superset}"
    )
    if ex.notes:
        line += f"\n     Notes: {ex.notes}"
    return line


def render(program: Program) -> str:
    """Render the complete program as formatted text."""
    lines: list[str] = []

    # ── Section 1: Training Level Assessment ──
    lines.append(_header("1. TRAINING LEVEL ASSESSMENT"))
    for pattern, level in program.level_assessment.items():
        lines.append(f"  {pattern.name:<20s}  →  {level.name}")

    # ── Section 2: Volume Targets ──
    lines.append(_header("2. WEEKLY VOLUME TARGETS (Fractional Sets)"))
    lines.append(f"  {'Muscle Group':<20s}  {'MEV':>5s}  {'Week 1':>7s}  {'MRV':>5s}")
    lines.append(f"  {'─' * 42}")
    for vt in program.volume_targets:
        lines.append(
            f"  {vt.muscle.name:<20s}  {vt.mev:>5.1f}  {vt.working:>7.1f}  {vt.mrv:>5.0f}"
        )

    # ── Section 3: Split Structure ──
    lines.append(_header("3. SPLIT STRUCTURE"))
    lines.append(f"  Split: {program.split_name}")
    lines.append(f"  Rationale: {program.split_rationale}")

    # ── Section 4: Weekly Program (Week 1) ──
    lines.append(_header("4. WEEKLY PROGRAM — Mesocycle Week 1"))
    for session in program.week1.sessions:
        lines.append(_subheader(session.day_label))
        for idx, ex in enumerate(session.exercises, 1):
            lines.append(_format_exercise(ex, idx))
        lines.append("")

    # ── Section 5: Progression Instructions ──
    lines.append(_header("5. PROGRESSION INSTRUCTIONS"))
    lines.append(program.progression_instructions)

    # ── Section 6: Deload Instructions ──
    lines.append(_header("6. DELOAD INSTRUCTIONS"))
    lines.append(program.deload_instructions)

    # ── Section 7: Mesocycle Progression ──
    lines.append(_header("7. MESOCYCLE PROGRESSION (Weeks 1-5)"))
    lines.append(
        f"  {'Week':<6s}  {'Volume':<35s}  {'RIR':<10s}  {'Load'}"
    )
    lines.append(f"  {'─' * 70}")
    for mo in program.mesocycle_overview:
        lines.append(
            f"  {mo.week:<6d}  {mo.volume_description:<35s}  "
            f"{mo.rir:<10s}  {mo.load_note}"
        )

    return "\n".join(lines)
