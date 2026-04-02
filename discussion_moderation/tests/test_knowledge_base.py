"""Tests for knowledge_base anti-patterns — ADR 0002 / ADR 0008."""

from discussion_moderation.tools.knowledge_base import get_anti_patterns


class TestAntiPatternsTimingPrinciples:
    """ADR 0008 timing principles are represented in the anti-pattern list."""

    def test_premature_intervention_before_impasse_is_listed(self):
        """AP-1: intervening before impasse is an anti-pattern.

        Expected result: get_anti_patterns() contains an entry referencing
        premature intervention (VanLehn 2011 / Kapur 2016).
        """
        patterns = get_anti_patterns()
        combined = " ".join(patterns).lower()

        assert "impasse" in combined or "premature" in combined

    def test_reintervening_without_cooldown_is_listed(self):
        """AP-2: re-intervening without cooldown is an anti-pattern.

        Expected result: get_anti_patterns() contains an entry referencing
        cooldown between interventions (Rovai 2007).
        """
        patterns = get_anti_patterns()
        combined = " ".join(patterns).lower()

        assert "cooldown" in combined

    def test_snapshot_decision_without_trajectory_is_listed(self):
        """AP-3: deciding based on snapshot state without trajectory is an anti-pattern.

        Expected result: get_anti_patterns() contains an entry referencing
        trajectory or declining participation (Chang & D-N-M 2019).
        """
        patterns = get_anti_patterns()
        combined = " ".join(patterns).lower()

        assert "trajectory" in combined or "snapshot" in combined

    def test_low_confidence_intervention_over_abstention_is_listed(self):
        """AP-4: choosing intervention over abstention under low confidence is an anti-pattern.

        Expected result: get_anti_patterns() contains an entry referencing
        abstention under ambiguity (Koedinger & Aleven 2007 / Anthropic 2025).
        """
        patterns = get_anti_patterns()
        combined = " ".join(patterns).lower()

        assert "abstain" in combined or "ambiguity" in combined or "false positive" in combined
