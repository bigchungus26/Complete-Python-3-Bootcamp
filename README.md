# Ironforge — Evidence-Based Workout Program Designer

A Python CLI tool that generates personalized training programs based on peer-reviewed exercise science (18 papers, 2023-2025).

## How It Works

1. **Intake** — Answers structured questions about goals, training history, schedule, equipment, and individual factors
2. **Algorithm** — Applies evidence-based rules for volume, frequency, exercise selection, load/RIR, and periodization
3. **Output** — Generates a complete mesocycle with per-session exercises, sets, reps, RIR, rest periods, progression, and deload protocols

## Quick Start

```bash
python -m ironforge
```

Or with JSON output:

```bash
python -m ironforge --format json
```

## What It Generates

1. **Training Level Assessment** — Per movement pattern (squat, bench, row, etc.)
2. **Volume Targets** — Weekly fractional sets per muscle group (MEV → MRV)
3. **Split Structure** — Full Body / Upper-Lower / PPL based on available days
4. **Weekly Program** — Each session with exercises, sets × reps, RIR, rest, coaching notes
5. **Progression Instructions** — Linear / Double Progression / Autoregulated based on level
6. **Deload Protocol** — Active deload with reactive triggers
7. **Mesocycle Overview** — 5-week block structure (4 training + 1 deload)

## Key Algorithm Features

- **Fractional set accounting** — Compound exercises give partial credit to secondary muscles
- **Per-pattern classification** — You can be intermediate on bench but beginner on squat
- **97 approved exercises** — Only evidence-backed movements with proper muscle targeting
- **A/B session variation** — Different exercises between repeated session types
- **Antagonist supersets** — Optional time-saving pairing (reduces session time ~36%)
- **Sex-adjusted rep ranges** — Females biased toward higher rep ranges (more Type I fiber)
- **Equipment filtering** — Works for full gyms, limited gyms, and home setups

## Project Structure

```
ironforge/
├── data/           # Exercise database, muscle groups, algorithm constants
├── intake/         # Questionnaire flow and user profile
├── engine/         # Classifier, volume, frequency, selection, load, supersets, periodization
├── program/        # Data models and builder (orchestrator)
└── output/         # Terminal formatter
```

## Requirements

- Python 3.11+
- Zero external dependencies

## Tests

```bash
python -m unittest tests.test_program -v
```
