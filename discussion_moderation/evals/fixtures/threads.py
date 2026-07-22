"""Sample discussion threads for evaluation.

Each thread represents a different discussion state (ADR 0003)
in a realistic academic context. Threads are designed to test
whether agents correctly classify state, decide on intervention,
and select appropriate actions.
"""

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

from discussion_moderation.models import (
    Comment,
    DiscussionThread,
)

NOW = datetime(2026, 3, 12, 14, 0, tzinfo=UTC)

REAL_THREADS_DIR = (
    Path(__file__).resolve().parents[3] / "docs" / "threads" / "real"
)


def _load_real_thread(name: str) -> DiscussionThread:
    """Load a real MOOC-extracted thread (ADR 0041) into DiscussionThread."""
    data = json.loads((REAL_THREADS_DIR / f"{name}.json").read_text())
    return DiscussionThread.model_validate(data)


def new_thread() -> DiscussionThread:
    """A thread just posted by the instructor, no replies yet."""
    return DiscussionThread(
        id="thread-new",
        source="synthetic",
        course_id="course-v1:UCM+TFM+2026",
        title="Privacy implications of large language models",
        body=(
            "This week we're discussing privacy in "
            "LLMs. Consider: what are the main risks "
            "when personal data appears in training "
            "sets? Share your thoughts and respond to "
            "at least one classmate."
        ),
        author="Prof. García",
        created_at=NOW - timedelta(hours=1),
        learning_objectives=[
            "Identify privacy risks in LLM training data",
            "Evaluate current mitigation strategies",
            "Propose privacy-preserving alternatives",
        ],
    )


def active_thread() -> DiscussionThread:
    """A healthy, active discussion with peer interaction."""
    base = NOW - timedelta(days=1)
    return DiscussionThread(
        id="thread-active",
        source="synthetic",
        course_id="course-v1:UCM+TFM+2026",
        title="Algorithmic bias in hiring systems",
        body=(
            "How does bias enter ML hiring systems? "
            "Use at least one real case in your answer."
        ),
        author="Prof. García",
        created_at=base,
        learning_objectives=[
            "Identify sources of bias in ML pipelines",
            "Analyse real-world case studies",
            "Propose fairness interventions",
        ],
        comments=[
            Comment(
                author="Alice",
                body=(
                    "Amazon's recruiting tool is a clear "
                    "example - it penalized resumes with the "
                    "word 'women's' because the training data "
                    "reflected a decade of male-dominated "
                    "hiring. The bias was in the historical "
                    "data, not the algorithm itself."
                ),
                created_at=base + timedelta(hours=3),
            ),
            Comment(
                author="Bob",
                body=(
                    "Good point Alice. I'd add that even "
                    "removing gender features doesn't help if "
                    "proxy variables like university or "
                    "hobbies correlate with gender. The "
                    "ProPublica analysis of COMPAS showed "
                    "similar proxy issues in criminal justice."
                ),
                created_at=base + timedelta(hours=5),
            ),
            Comment(
                author="Carlos",
                body=(
                    "Building on what Bob said - I think the "
                    "problem is also in the evaluation metric. "
                    "If you optimize for 'past successful "
                    "hires' you're encoding whatever biases "
                    "existed in those decisions. Wouldn't "
                    "counterfactual fairness be a better "
                    "approach?"
                ),
                created_at=base + timedelta(hours=8),
            ),
            Comment(
                author="Diana",
                body=(
                    "Carlos, counterfactual fairness sounds "
                    "great in theory but it requires a causal "
                    "model of the world, which is hard to "
                    "build. In practice, companies use "
                    "demographic parity or equalized odds - "
                    "both have tradeoffs. Which fairness "
                    "metric do you think fits hiring best?"
                ),
                created_at=base + timedelta(hours=10),
            ),
        ],
    )


def stalled_thread() -> DiscussionThread:
    """A thread where participation died after one reply."""
    base = NOW - timedelta(days=4)
    return DiscussionThread(
        id="thread-stalled",
        source="synthetic",
        course_id="course-v1:UCM+TFM+2026",
        title="Open source licensing in AI research",
        body=(
            "Should AI models be released under open "
            "source licenses? Consider the tension "
            "between reproducibility and potential "
            "misuse."
        ),
        author="Prof. García",
        created_at=base,
        learning_objectives=[
            "Compare open source license types",
            "Analyse tensions between openness and safety",
            "Evaluate current industry positions",
        ],
        comments=[
            Comment(
                author="Elena",
                body=(
                    "I think open source is important for "
                    "science but there should be limits."
                ),
                created_at=base + timedelta(hours=6),
            ),
        ],
    )


def conflictive_thread() -> DiscussionThread:
    """A thread with aggressive or dismissive exchanges."""
    base = NOW - timedelta(days=1)
    return DiscussionThread(
        id="thread-conflictive",
        source="synthetic",
        course_id="course-v1:UCM+TFM+2026",
        title="Regulation of AI systems in the EU",
        body=(
            "The EU AI Act classifies AI systems by "
            "risk level. Do you think this approach "
            "is effective? What are its limitations?"
        ),
        author="Prof. García",
        created_at=base,
        learning_objectives=[
            "Analyse the EU AI Act risk categories",
            "Evaluate regulatory approaches",
            "Compare with other jurisdictions",
        ],
        comments=[
            Comment(
                author="Frank",
                body=(
                    "The EU AI Act is just bureaucratic "
                    "overreach. It will kill innovation in "
                    "Europe while the US and China move ahead "
                    "without these ridiculous constraints."
                ),
                created_at=base + timedelta(hours=2),
            ),
            Comment(
                author="Grace",
                body=(
                    "That's a really superficial take, Frank. "
                    "Maybe if you actually read the Act "
                    "instead of parroting tech bro talking "
                    "points, you'd know that most AI systems "
                    "fall under minimal risk and aren't "
                    "affected at all."
                ),
                created_at=base + timedelta(hours=3),
            ),
            Comment(
                author="Frank",
                body=(
                    "Oh please, spare me the lecture. People "
                    "who've never built anything always love "
                    "to regulate. This is exactly what's "
                    "wrong with academia."
                ),
                created_at=base + timedelta(hours=4),
            ),
        ],
    )


def convergent_thread() -> DiscussionThread:
    """A thread where participants are reaching consensus."""
    base = NOW - timedelta(days=2)
    return DiscussionThread(
        id="thread-convergent",
        source="synthetic",
        course_id="course-v1:UCM+TFM+2026",
        title="Explainability vs. accuracy tradeoff",
        body=(
            "When should we prefer an explainable "
            "model over a more accurate black-box "
            "model? Is there always a tradeoff?"
        ),
        author="Prof. García",
        created_at=base,
        learning_objectives=[
            "Define explainability in ML context",
            "Analyse the accuracy-explainability tradeoff",
            "Identify domain-specific requirements",
        ],
        comments=[
            Comment(
                author="Hana",
                body=(
                    "In healthcare, explainability is "
                    "non-negotiable; doctors need to "
                    "understand why a model recommends a "
                    "treatment. The GDPR also requires "
                    "explanations for automated decisions "
                    "affecting individuals."
                ),
                created_at=base + timedelta(hours=4),
            ),
            Comment(
                author="Ivan",
                body=(
                    "I agree with Hana for high-stakes "
                    "domains. But for things like content "
                    "recommendation, accuracy matters more "
                    "and users don't really need explanations."
                ),
                created_at=base + timedelta(hours=8),
            ),
            Comment(
                author="Julia",
                body=(
                    "So it seems like we all agree the "
                    "answer is domain-dependent. High-stakes "
                    "decisions (healthcare, justice, finance) "
                    "need explainability; low-stakes "
                    "applications can prioritize accuracy. "
                    "The real question is where to draw the "
                    "line."
                ),
                created_at=base + timedelta(hours=12),
            ),
            Comment(
                author="Hana",
                body=(
                    "Exactly, Julia. And I'd add that recent "
                    "work on SHAP and LIME shows the tradeoff "
                    "isn't always as stark as it seems - you "
                    "can often get good explanations from "
                    "complex models without sacrificing much "
                    "accuracy."
                ),
                created_at=base + timedelta(hours=14),
            ),
        ],
    )


def off_topic_thread() -> DiscussionThread:
    """A thread that drifted away from the assigned topic."""
    base = NOW - timedelta(days=1)
    return DiscussionThread(
        id="thread-off-topic",
        source="synthetic",
        course_id="course-v1:UCM+TFM+2026",
        title="Environmental impact of training large models",
        body=(
            "Training GPT-4 reportedly consumed "
            "significant energy. How should we "
            "balance model capability with "
            "environmental cost?"
        ),
        author="Prof. García",
        created_at=base,
        learning_objectives=[
            "Quantify energy consumption of LLM training",
            "Compare with other industries",
            "Propose sustainable AI practices",
        ],
        comments=[
            Comment(
                author="Kevin",
                body=(
                    "Speaking of GPT-4, did you all see the "
                    "new features they added last week? The "
                    "image generation is incredible. I used "
                    "it to make a poster for my other class."
                ),
                created_at=base + timedelta(hours=2),
            ),
            Comment(
                author="Laura",
                body=(
                    "Yeah the image stuff is cool! I've been "
                    "using it to generate study materials. "
                    "Way better than Midjourney honestly."
                ),
                created_at=base + timedelta(hours=3),
            ),
            Comment(
                author="Kevin",
                body=(
                    "Totally. And the coding assistant is "
                    "getting scary good. I wonder if we'll "
                    "even need to learn programming in a few "
                    "years lol."
                ),
                created_at=base + timedelta(hours=5),
            ),
        ],
    )


def shallow_discourse_thread() -> DiscussionThread:
    """Active thread with distributed participation but formulaic discourse.

    Students are present and posting, but nobody builds on prior ideas or
    develops arguments. Designed to trigger intellectual facilitation.
    """
    base = NOW - timedelta(days=2)
    return DiscussionThread(
        id="thread-shallow-discourse",
        source="synthetic",
        course_id="course-v1:UCM+TFM+2026",
        title="Transparency requirements for AI decision systems",
        body=(
            "When should AI systems be required to explain "
            "their decisions? Consider specific domains and "
            "what transparency would mean in practice. "
            "Build on your classmates' arguments."
        ),
        author="Prof. García",
        created_at=base,
        learning_objectives=[
            "Distinguish between interpretability and explainability",
            "Identify domain-specific transparency requirements",
            "Evaluate practical tradeoffs in explainability techniques",
        ],
        comments=[
            Comment(
                author="Mia",
                body=(
                    "I think transparency is really important, "
                    "especially in healthcare. Doctors should "
                    "understand why an AI recommends a treatment."
                ),
                created_at=base + timedelta(hours=5),
            ),
            Comment(
                author="Noah",
                body=(
                    "I agree with Mia. Transparency builds trust "
                    "and trust is essential for AI adoption. "
                    "Without it, people won't use these systems."
                ),
                created_at=base + timedelta(hours=9),
            ),
            Comment(
                author="Olivia",
                body=(
                    "Yes, and regulation should require it. "
                    "The EU AI Act addresses this for high-risk "
                    "systems, which is a good step forward."
                ),
                created_at=base + timedelta(hours=14),
            ),
            Comment(
                author="Mia",
                body=(
                    "Exactly. Companies won't do it on their own, "
                    "so regulation is the right approach."
                ),
                created_at=base + timedelta(hours=18),
            ),
            Comment(
                author="Noah",
                body=(
                    "Good points all around. I think we all agree "
                    "that transparency is necessary and important."
                ),
                created_at=base + timedelta(hours=22),
            ),
        ],
    )


def dominated_thread() -> DiscussionThread:
    """Active thread where one student's voice crowds out others.

    Marco posts repeatedly with substantive content while other
    students make brief acknowledgments. Designed to trigger social
    facilitation to redistribute participation.
    """
    base = NOW - timedelta(days=3)
    return DiscussionThread(
        id="thread-dominated",
        source="synthetic",
        course_id="course-v1:UCM+TFM+2026",
        title="Federated learning as a privacy-preserving approach",
        body=(
            "Federated learning is proposed as a way to train "
            "models without centralizing personal data. What are "
            "its real privacy guarantees? What are its limits?"
        ),
        author="Prof. García",
        created_at=base,
        learning_objectives=[
            "Explain federated learning and its privacy assumptions",
            "Identify attacks that undermine federated privacy",
            "Compare federated learning with alternative approaches",
        ],
        comments=[
            Comment(
                author="Marco",
                body=(
                    "Federated learning's privacy guarantees are "
                    "often overstated. Model updates themselves leak "
                    "information through gradient inversion attacks. "
                    "Zhu et al. (2019) showed you can reconstruct "
                    "training samples from gradients with high "
                    "fidelity. The data never leaves the device, "
                    "but the information does."
                ),
                created_at=base + timedelta(hours=4),
            ),
            Comment(
                author="Nora",
                body="Interesting, I hadn't thought about gradient attacks.",
                created_at=base + timedelta(hours=9),
            ),
            Comment(
                author="Marco",
                body=(
                    "Right, and differential privacy can be added "
                    "on top to limit gradient leakage, but at a "
                    "cost to accuracy. The epsilon parameter controls "
                    "this tradeoff and production values are often "
                    "too large to provide meaningful privacy. "
                    "Apple's use of local DP is a good case: their "
                    "epsilon choices were criticized as insufficient."
                ),
                created_at=base + timedelta(hours=15),
            ),
            Comment(
                author="Pavel",
                body=(
                    "Thanks Marco, this is helpful for understanding "
                    "the tradeoffs."
                ),
                created_at=base + timedelta(hours=20),
            ),
            Comment(
                author="Marco",
                body=(
                    "There's also the fairness angle. Federated "
                    "models can perform worse for underrepresented "
                    "groups if their local datasets are smaller or "
                    "less diverse. Li et al. (2020) on FedProx "
                    "addresses convergence on heterogeneous data, "
                    "but fairness across participants is still open. "
                    "Federated learning is better than centralizing "
                    "data, but it's a privacy trade-off, not a "
                    "privacy solution."
                ),
                created_at=base + timedelta(hours=28),
            ),
            Comment(
                author="Nora",
                body="I agree with Marco's conclusion.",
                created_at=base + timedelta(hours=34),
            ),
        ],
    )


def declining_vs_never_posted_thread() -> DiscussionThread:
    """Active thread with both a declining and a never-posted student.

    Quinn posted once early then stopped responding to a direct
    question, showing a declining trajectory. Riley never posted at
    all. Designed to test whether social facilitation targets the
    declining participant over the never-posted one (Kim et al.,
    2021, per ADR 0004).
    """
    base = NOW - timedelta(days=3)
    return DiscussionThread(
        id="thread-declining-vs-never-posted",
        source="synthetic",
        course_id="course-v1:UCM+TFM+2026",
        title="Fairness tradeoffs in credit scoring models",
        body=(
            "Credit scoring models optimize for default "
            "prediction, but fairness metrics often conflict "
            "with that objective. Where should the line be "
            "drawn, and who should draw it?"
        ),
        author="Prof. García",
        created_at=base,
        learning_objectives=[
            "Identify fairness-accuracy tradeoffs in scoring models",
            "Evaluate who bears the cost of different fairness choices",
        ],
        comments=[
            Comment(
                author="Quinn",
                body=(
                    "I think demographic parity is the right "
                    "starting point, even if it costs some "
                    "accuracy. The alternative is baking "
                    "historical lending bias into the model."
                ),
                created_at=base + timedelta(hours=3),
            ),
            Comment(
                author="Sam",
                body=(
                    "Quinn, how would you respond to the "
                    "critique that demographic parity can force "
                    "the model to reject qualified applicants "
                    "just to balance group outcomes?"
                ),
                created_at=base + timedelta(hours=8),
            ),
            Comment(
                author="Tara",
                body=(
                    "Sam raises a fair point. I'd lean toward "
                    "equalized odds instead, since it keeps "
                    "error rates comparable without forcing "
                    "outcome parity directly."
                ),
                created_at=base + timedelta(hours=20),
            ),
        ],
    )


def preventive_social_activation_thread() -> DiscussionThread:
    """Active thread with deteriorating tone that hasn't crossed into conflict.

    Exchanges are getting terser and more dismissive across
    consecutive replies, but nothing here is overtly hostile or
    abuse-flagged. Designed to test whether social facilitation can
    activate preventively on tone trajectory, before the classifier
    would label the thread conflictive (ADR 0004).
    """
    base = NOW - timedelta(days=1)
    return DiscussionThread(
        id="thread-preventive-social",
        source="synthetic",
        course_id="course-v1:UCM+TFM+2026",
        title="Should model cards be legally mandated?",
        body=(
            "Some regulators propose mandatory model cards for "
            "any deployed ML system. Is documentation a "
            "sufficient accountability mechanism, or does it "
            "just shift the burden onto users?"
        ),
        author="Prof. García",
        created_at=base,
        learning_objectives=[
            "Evaluate documentation-based accountability mechanisms",
            "Distinguish disclosure from enforcement",
        ],
        comments=[
            Comment(
                author="Uma",
                body=(
                    "Model cards seem useful to me - at least "
                    "users would know what they're dealing with "
                    "and could make an informed choice."
                ),
                created_at=base + timedelta(hours=2),
            ),
            Comment(
                author="Victor",
                body=(
                    "That assumes users read documentation, "
                    "which they mostly don't. Disclosure without "
                    "enforcement doesn't change anything."
                ),
                created_at=base + timedelta(hours=4),
            ),
            Comment(
                author="Uma",
                body=("Sure, but it's still a floor. Better than nothing."),
                created_at=base + timedelta(hours=6),
            ),
            Comment(
                author="Victor",
                body="Not really, no.",
                created_at=base + timedelta(hours=7),
            ),
            Comment(
                author="Uma",
                body="Ok.",
                created_at=base + timedelta(hours=9),
            ),
        ],
    )


def ambiguous_signals_thread() -> DiscussionThread:
    """Thread with deliberately mixed, contradictory state signals.

    Recent replies are substantive (arguing against stall) but the
    gap since the last one approaches the stalled threshold, and the
    discussion is on-topic but shallow. No single state fits
    cleanly. Designed to test whether the classifier abstains under
    genuine ambiguity instead of forcing a low-confidence
    intervention (ADR 0008, Principles 3-4).
    """
    base = NOW - timedelta(hours=44)
    return DiscussionThread(
        id="thread-ambiguous-signals",
        source="synthetic",
        course_id="course-v1:UCM+TFM+2026",
        title="Interpretability methods for tabular models",
        body=(
            "SHAP and LIME are the most common interpretability "
            "tools for tabular models. Are they actually giving "
            "us causal understanding, or just a locally "
            "consistent approximation?"
        ),
        author="Prof. García",
        created_at=base,
        learning_objectives=[
            "Distinguish correlational from causal explanations",
            "Evaluate limitations of post-hoc interpretability",
        ],
        comments=[
            Comment(
                author="Will",
                body=(
                    "I don't think they give causal "
                    "understanding, just a local approximation "
                    "of the model's own behavior."
                ),
                created_at=base + timedelta(hours=1),
            ),
            Comment(
                author="Xena",
                body="Fair.",
                created_at=base + timedelta(hours=2, minutes=30),
            ),
        ],
    )


def dual_state_stalled_off_topic_thread() -> DiscussionThread:
    """Thread that is simultaneously stalled and off-topic.

    The last substantive reply on the assigned topic came well past
    the stalled threshold ago; the only activity since then has
    drifted away from the learning objectives. Designed to test
    which single state label the classifier assigns when two
    conditions apply at once (ADR 0015) - distinct from B14's
    stalled+conflictive pairing.
    """
    base = NOW - timedelta(days=4)
    return DiscussionThread(
        id="thread-dual-state-stalled-off-topic",
        source="synthetic",
        course_id="course-v1:UCM+TFM+2026",
        title="Data minimization principles in ML pipelines",
        body=(
            "Data minimization says collect only what you need. "
            "How does that principle hold up against the "
            "practice of collecting broad features 'just in "
            "case' they improve model performance later?"
        ),
        author="Prof. García",
        created_at=base,
        learning_objectives=[
            "Apply data minimization to ML pipeline design",
            "Evaluate tensions between minimization and model performance",
        ],
        comments=[
            Comment(
                author="Yusuf",
                body=(
                    "I think minimization mostly loses in "
                    "practice - teams collect broadly because "
                    "retraining on newly available features is "
                    "cheaper than negotiating new data access "
                    "later."
                ),
                created_at=base + timedelta(hours=3),
            ),
            Comment(
                author="Zara",
                body=(
                    "By the way, did anyone see the new laptop "
                    "announcements this week? Might be worth "
                    "upgrading before the semester gets busy."
                ),
                created_at=base + timedelta(days=3, hours=2),
            ),
            Comment(
                author="Yusuf",
                body="Ha, yeah I saw those. Tempting.",
                created_at=base + timedelta(days=3, hours=5),
            ),
        ],
    )


def real_dominated_thread() -> DiscussionThread:
    """Real MOOC thread (ADR 0041) matching the `dominated` pattern."""
    return _load_real_thread("dominated")


def real_explicit_distress_thread() -> DiscussionThread:
    """Real MOOC thread (ADR 0041) matching the `explicit_distress` pattern."""
    return _load_real_thread("explicit_distress")


def real_formulaic_thread() -> DiscussionThread:
    """Real MOOC thread (ADR 0041) matching the `formulaic` pattern."""
    return _load_real_thread("formulaic")


def real_hostile_then_silent_thread() -> DiscussionThread:
    """Real MOOC thread (ADR 0041) matching `hostile_then_silent`."""
    return _load_real_thread("hostile_then_silent")


def real_integration_phase_thread() -> DiscussionThread:
    """Real MOOC thread (ADR 0041) matching the `integration_phase` pattern."""
    return _load_real_thread("integration_phase")


def real_overt_attack_thread() -> DiscussionThread:
    """Real MOOC thread (ADR 0041) matching the `overt_attack` pattern."""
    return _load_real_thread("overt_attack")


ALL_THREADS = {
    "new": new_thread,
    "active": active_thread,
    "stalled": stalled_thread,
    "conflictive": conflictive_thread,
    "convergent": convergent_thread,
    "off_topic": off_topic_thread,
    "shallow_discourse": shallow_discourse_thread,
    "dominated": dominated_thread,
    "declining_vs_never_posted": declining_vs_never_posted_thread,
    "preventive_social_activation": preventive_social_activation_thread,
    "ambiguous_signals": ambiguous_signals_thread,
    "dual_state_stalled_off_topic": dual_state_stalled_off_topic_thread,
    "real_dominated": real_dominated_thread,
    "real_explicit_distress": real_explicit_distress_thread,
    "real_formulaic": real_formulaic_thread,
    "real_hostile_then_silent": real_hostile_then_silent_thread,
    "real_integration_phase": real_integration_phase_thread,
    "real_overt_attack": real_overt_attack_thread,
}
