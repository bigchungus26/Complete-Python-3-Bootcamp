"""End-to-end tests for the workout program generator."""

import unittest
from ironforge.data.muscle_groups import (
    Goal, Sex, CaloricPhase, EquipmentAccess, Equipment,
    MovementPattern, TrainingLevel, VolumeMuscle, Tier,
)
from ironforge.data.exercises import ALL_EXERCISES, exercises_by_muscle, MuscleGroup
from ironforge.intake.profile import UserProfile
from ironforge.engine.classifier import classify
from ironforge.engine.volume import compute_volume
from ironforge.engine.frequency import plan_frequency
from ironforge.engine.selection import select_exercises_for_session
from ironforge.engine.supersets import pair_supersets
from ironforge.engine.load import assign_loading
from ironforge.engine.periodization import (
    build_mesocycle_overview, build_progression_instructions,
    build_deload_instructions,
)
from ironforge.program.builder import build_program
from ironforge.output.formatter import render


class TestExerciseDatabase(unittest.TestCase):
    def test_exercise_count(self):
        # Should have ~97 entries (some may appear twice in ALL_EXERCISES
        # due to dual-category listing like PULLDOWN_ROW_MACHINE)
        unique = {e.name for e in ALL_EXERCISES}
        self.assertGreaterEqual(len(unique), 90)

    def test_all_exercises_have_equipment(self):
        for ex in ALL_EXERCISES:
            self.assertTrue(len(ex.equipment) > 0, f"{ex.name} has no equipment")

    def test_exercises_by_muscle(self):
        chest = exercises_by_muscle(MuscleGroup.CHEST_STERNAL)
        self.assertTrue(len(chest) > 0)
        for ex in chest:
            self.assertEqual(ex.primary, MuscleGroup.CHEST_STERNAL)


class TestClassifier(unittest.TestCase):
    def test_beginner_classification(self):
        p = UserProfile(training_months=3)
        levels = classify(p)
        for pattern, level in levels.items():
            self.assertEqual(level, TrainingLevel.BEGINNER)

    def test_intermediate_classification(self):
        p = UserProfile(training_months=18, adds_weight_every_1_2_weeks=True)
        levels = classify(p)
        for pattern, level in levels.items():
            self.assertEqual(level, TrainingLevel.INTERMEDIATE)

    def test_advanced_classification(self):
        p = UserProfile(training_months=48)
        levels = classify(p)
        for pattern, level in levels.items():
            self.assertEqual(level, TrainingLevel.ADVANCED)

    def test_per_pattern_override(self):
        p = UserProfile(
            training_months=18,
            pattern_experience={
                MovementPattern.SQUAT: TrainingLevel.BEGINNER,
                MovementPattern.HORIZONTAL_PUSH: TrainingLevel.ADVANCED,
            },
        )
        levels = classify(p)
        self.assertEqual(levels[MovementPattern.SQUAT], TrainingLevel.BEGINNER)
        self.assertEqual(levels[MovementPattern.HORIZONTAL_PUSH], TrainingLevel.ADVANCED)


class TestVolume(unittest.TestCase):
    def test_volume_at_mev(self):
        p = UserProfile(training_months=18)
        levels = classify(p)
        targets = compute_volume(p, levels)
        self.assertTrue(len(targets) > 0)
        for t in targets:
            self.assertGreaterEqual(t.working, t.mev)

    def test_priority_muscles_get_more_volume(self):
        p_no_priority = UserProfile(training_months=18)
        p_priority = UserProfile(
            training_months=18,
            priority_muscles=[VolumeMuscle.CHEST],
        )
        levels = classify(p_no_priority)
        targets_no = compute_volume(p_no_priority, levels)
        targets_yes = compute_volume(p_priority, levels)

        chest_no = next(t for t in targets_no if t.muscle == VolumeMuscle.CHEST)
        chest_yes = next(t for t in targets_yes if t.muscle == VolumeMuscle.CHEST)
        self.assertGreaterEqual(chest_yes.working, chest_no.working)


class TestFrequency(unittest.TestCase):
    def test_no_consecutive_muscle_overlap(self):
        """Every non-full-body split must have zero muscle overlap on adjacent days."""
        from ironforge.engine.frequency import SPLITS_BY_DAYS
        for days, splits in SPLITS_BY_DAYS.items():
            for split in splits:
                if split.requires_rest_days:
                    continue
                for i in range(len(split.sessions) - 1):
                    a = set(split.sessions[i].muscle_focus)
                    b = set(split.sessions[i + 1].muscle_focus)
                    overlap = a & b
                    self.assertEqual(
                        overlap, set(),
                        f"{split.name}: {split.sessions[i].day_label} and "
                        f"{split.sessions[i+1].day_label} share {overlap}",
                    )

    def test_all_rep_ranges_within_4_10(self):
        """Every rep range must be between 4 and 10."""
        from ironforge.data.constants import REP_RANGES, REP_RANGES_FEMALE
        for ranges in [REP_RANGES, REP_RANGES_FEMALE]:
            for tier, (lo, hi) in ranges.items():
                self.assertGreaterEqual(lo, 4, f"{tier}: rep_low {lo} < 4")
                self.assertLessEqual(hi, 10, f"{tier}: rep_high {hi} > 10")

    def test_3_day_full_body(self):
        p = UserProfile(days_per_week=3)
        targets = compute_volume(p, classify(p))
        split = plan_frequency(p, targets)
        self.assertEqual(split.name, "Full Body")
        self.assertEqual(len(split.sessions), 3)

    def test_4_day_upper_lower(self):
        p = UserProfile(days_per_week=4)
        targets = compute_volume(p, classify(p))
        split = plan_frequency(p, targets)
        self.assertEqual(split.name, "Upper / Lower")
        self.assertEqual(len(split.sessions), 4)

    def test_6_day_ppl(self):
        p = UserProfile(days_per_week=6)
        targets = compute_volume(p, classify(p))
        split = plan_frequency(p, targets)
        self.assertEqual(split.name, "PPL (x2)")
        self.assertEqual(len(split.sessions), 6)


class TestLoad(unittest.TestCase):
    def test_t1_higher_rir_week1(self):
        load = assign_loading(Tier.T1, TrainingLevel.INTERMEDIATE, Sex.MALE, week=1)
        self.assertGreaterEqual(load.rir, 3)

    def test_beginner_higher_rir(self):
        load = assign_loading(Tier.T2, TrainingLevel.BEGINNER, Sex.MALE)
        self.assertGreaterEqual(load.rir, 3)

    def test_female_higher_reps(self):
        male = assign_loading(Tier.T1, TrainingLevel.INTERMEDIATE, Sex.MALE)
        female = assign_loading(Tier.T1, TrainingLevel.INTERMEDIATE, Sex.FEMALE)
        self.assertGreater(female.rep_low, male.rep_low)

    def test_rest_periods_minimum(self):
        for tier in Tier:
            load = assign_loading(tier, TrainingLevel.INTERMEDIATE, Sex.MALE)
            self.assertGreaterEqual(load.rest_seconds, 90)


class TestSelection(unittest.TestCase):
    def test_chest_session_has_press_and_fly(self):
        from ironforge.engine.frequency import SessionTemplate
        p = UserProfile(days_per_week=4)
        levels = classify(p)
        targets = compute_volume(p, levels)
        split = plan_frequency(p, targets)

        template = split.sessions[0]  # Upper A
        exercises = select_exercises_for_session(
            template, split.sessions, p, levels, targets, 0,
        )
        chest_exercises = [
            e for e in exercises
            if e.exercise.primary in (MuscleGroup.CHEST_CLAVICULAR, MuscleGroup.CHEST_STERNAL)
        ]
        self.assertGreaterEqual(len(chest_exercises), 2)

    def test_back_has_vertical_and_horizontal(self):
        from ironforge.engine.frequency import SessionTemplate
        p = UserProfile(days_per_week=4)
        levels = classify(p)
        targets = compute_volume(p, levels)
        split = plan_frequency(p, targets)

        template = split.sessions[0]  # Upper A
        exercises = select_exercises_for_session(
            template, split.sessions, p, levels, targets, 0,
        )
        patterns = {e.exercise.pattern for e in exercises}
        self.assertIn(MovementPattern.VERTICAL_PULL, patterns)
        self.assertIn(MovementPattern.HORIZONTAL_PULL, patterns)


class TestSupersets(unittest.TestCase):
    def test_t1_never_supersetted(self):
        from ironforge.engine.frequency import SessionTemplate
        p = UserProfile(days_per_week=4, prefers_supersets=True)
        levels = classify(p)
        targets = compute_volume(p, levels)
        split = plan_frequency(p, targets)

        template = split.sessions[0]
        exercises = select_exercises_for_session(
            template, split.sessions, p, levels, targets, 0,
        )
        exercises = pair_supersets(exercises)
        for ex in exercises:
            if ex.tier == Tier.T1:
                self.assertIsNone(ex.superset_pair_id)


class TestEndToEnd(unittest.TestCase):
    def _build(self, **kwargs):
        p = UserProfile(**kwargs)
        program = build_program(p)
        return program, render(program)

    def test_beginner_hypertrophy_4day(self):
        program, output = self._build(
            primary_goal=Goal.HYPERTROPHY, training_months=3, days_per_week=4,
        )
        self.assertIn("BEGINNER", output)
        self.assertIn("Upper / Lower", output)
        self.assertIn("LINEAR PROGRESSION", output)

    def test_intermediate_strength_5day(self):
        program, output = self._build(
            primary_goal=Goal.STRENGTH, training_months=18, days_per_week=5,
        )
        self.assertIn("INTERMEDIATE", output)
        self.assertIn("Upper / Lower / Push / Pull / Legs", output)
        self.assertIn("STRENGTH NOTES", output)

    def test_advanced_recomp_6day(self):
        program, output = self._build(
            primary_goal=Goal.RECOMP, training_months=48, days_per_week=6,
            caloric_phase=CaloricPhase.DEFICIT,
        )
        self.assertIn("ADVANCED", output)
        self.assertIn("PPL", output)
        self.assertIn("DEFICIT NOTE", output)

    def test_female_higher_reps(self):
        program, output = self._build(
            training_months=18, days_per_week=4, sex=Sex.FEMALE,
        )
        # Female T1 should be 5-8, not 4-6
        self.assertIn("5-8", output)

    def test_home_gym_equipment_filter(self):
        program, output = self._build(
            training_months=18, days_per_week=4,
            equipment_access=EquipmentAccess.HOME_GYM,
            available_equipment={
                Equipment.BARBELL, Equipment.DUMBBELL,
                Equipment.EZ_BAR, Equipment.BODYWEIGHT,
            },
        )
        # Should not contain any machine-only exercises
        self.assertNotIn("Machine Chest Press", output)

    def test_glute_focus(self):
        program, output = self._build(
            training_months=18, days_per_week=4,
            wants_glute_focus=True,
            priority_muscles=[VolumeMuscle.GLUTES],
        )
        self.assertIn("Hip Thrust", output)

    def test_all_sessions_have_exercises(self):
        for days in [3, 4, 5, 6]:
            program, output = self._build(
                training_months=18, days_per_week=days,
            )
            for session in program.weeks[0].sessions:
                self.assertTrue(
                    len(session.exercises) > 0,
                    f"{days}-day split, session {session.day_label} has no exercises",
                )

    def test_mesocycle_has_4_weeks(self):
        program, _ = self._build(training_months=18, days_per_week=4)
        self.assertEqual(len(program.mesocycle_overview), 4)
        self.assertEqual(len(program.weeks), 4)

    def test_sets_constant_across_weeks(self):
        """Same exercises and sets every week — only RIR changes."""
        program, _ = self._build(training_months=18, days_per_week=4)
        w1 = [(e.exercise.name, e.load.sets)
              for s in program.weeks[0].sessions for e in s.exercises]
        w4 = [(e.exercise.name, e.load.sets)
              for s in program.weeks[3].sessions for e in s.exercises]
        self.assertEqual(w1, w4)

    def test_max_3_sets_per_exercise(self):
        for days in [3, 4, 5, 6]:
            program, _ = self._build(training_months=18, days_per_week=days)
            for week in program.weeks:
                for s in week.sessions:
                    for e in s.exercises:
                        self.assertLessEqual(
                            e.load.sets, 3,
                            f"{e.exercise.name} has {e.load.sets} sets",
                        )

    def test_rir_decreases_across_weeks(self):
        program, _ = self._build(training_months=18, days_per_week=4)
        rir_w1 = program.weeks[0].sessions[0].exercises[0].load.rir
        rir_w4 = program.weeks[3].sessions[0].exercises[0].load.rir
        self.assertGreater(rir_w1, rir_w4)

    def test_deload_instructions_present(self):
        _, output = self._build(training_months=18, days_per_week=4)
        self.assertIn("ACTIVE DELOAD", output)
        self.assertIn("NUCKOLS RULE", output)

    def test_split_selection(self):
        program, _ = self._build(
            training_months=18, days_per_week=6, split_key="arnold_6",
        )
        self.assertEqual(program.split_name, "Arnold Split (x2)")

    def test_multiple_priority_muscles(self):
        program, output = self._build(
            training_months=18, days_per_week=4,
            priority_muscles=[VolumeMuscle.CHEST, VolumeMuscle.BACK, VolumeMuscle.BICEPS],
        )
        # All three should be at MAV-low, not MEV
        chest_target = next(t for t in program.volume_targets if t.muscle == VolumeMuscle.CHEST)
        back_target = next(t for t in program.volume_targets if t.muscle == VolumeMuscle.BACK)
        biceps_target = next(t for t in program.volume_targets if t.muscle == VolumeMuscle.BICEPS)
        self.assertGreater(chest_target.working, chest_target.mev)
        self.assertGreater(back_target.working, back_target.mev)
        self.assertGreater(biceps_target.working, biceps_target.mev)


if __name__ == "__main__":
    unittest.main()
