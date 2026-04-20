"""Structural assertions for eval output validation.

These checks run on LLM-generated FacilitationResponse and
ClassifierEvalOutput values independently of expected outputs.
They verify structural invariants - properties that must hold
regardless of what the LLM decided, derived from the domain
model and ADR constraints.

Use these in eval suites after calling the pipeline to catch
output that is structurally wrong before comparing it to
expectations.
"""

from discussion_moderation.evals.utils import setup_eval_logging
from discussion_moderation.models import FacilitationResponse
from discussion_moderation.tools.knowledge_base import TECHNIQUES

logger = setup_eval_logging("assertions")

_KNOWN_TECHNIQUE_NAMES: frozenset[str] = frozenset(t.name for t in TECHNIQUES)


def assert_facilitation_response(
    response: FacilitationResponse,
    case_name: str = "",
) -> list[str]:
    """Check structural invariants on a FacilitationResponse.

    Does not compare against expected values - only checks
    properties that must always hold.

    Args:
        response: The LLM-generated facilitation response.
        case_name: Optional label for log messages.

    Returns:
        List of violation strings. Empty list means all checks
        passed.
    """
    prefix = f"[{case_name}] " if case_name else ""
    violations: list[str] = []

    if not response.response_text.strip():
        violations.append(f"{prefix}response_text is empty")

    if not response.technique_used.strip():
        violations.append(f"{prefix}technique_used is empty")
    elif response.technique_used not in _KNOWN_TECHNIQUE_NAMES:
        violations.append(
            f"{prefix}technique_used '{response.technique_used}' "
            f"is not a known technique name"
        )

    if response.technique_used == "instructor_escalation":
        if response.post_to_thread:
            violations.append(
                f"{prefix}instructor_escalation must have post_to_thread=False"
            )

    if not (0.0 <= response.confidence <= 1.0):
        violations.append(
            f"{prefix}confidence {response.confidence} is outside [0.0, 1.0]"
        )

    for violation in violations:
        logger.warning("Structural violation: %s", violation)

    return violations


def log_facilitation_response(
    response: FacilitationResponse,
    case_name: str = "",
) -> None:
    """Log a FacilitationResponse for inspection.

    Args:
        response: The facilitation response to log.
        case_name: Optional label for log messages.
    """
    prefix = f"[{case_name}] " if case_name else ""
    logger.info(
        "%stechnique=%s post_to_thread=%s confidence=%.2f",
        prefix,
        response.technique_used,
        response.post_to_thread,
        response.confidence,
    )
    preview = response.response_text[:120]
    logger.info("%sresponse: %s", prefix, preview)
