"""Sample discussion threads for evaluation.

Each thread represents a different discussion state (ADR 0003)
in a realistic academic context. Threads are designed to test
whether agents correctly classify state, decide on intervention,
and select appropriate actions.
"""

from datetime import UTC, datetime, timedelta

from discussion_moderation.models import (
    Comment,
    DiscussionThread,
)

NOW = datetime(2026, 3, 12, 14, 0, tzinfo=UTC)


def new_thread() -> DiscussionThread:
    """A thread just posted by the instructor, no replies yet."""
    return DiscussionThread(
        id="thread-new",
        course_id="course-v1:UCM+TFM+2026",
        title="Privacy implications of large language models",
        created_at=NOW - timedelta(hours=1),
        learning_objectives=[
            "Identify privacy risks in LLM training data",
            "Evaluate current mitigation strategies",
            "Propose privacy-preserving alternatives",
        ],
        children=[
            Comment(
                username="Prof. García",
                body=(
                    "This week we're discussing privacy in "
                    "LLMs. Consider: what are the main risks "
                    "when personal data appears in training "
                    "sets? Share your thoughts and respond to "
                    "at least one classmate."
                ),
                created_at=NOW - timedelta(hours=1),
            ),
        ],
    )


def active_thread() -> DiscussionThread:
    """A healthy, active discussion with peer interaction."""
    base = NOW - timedelta(days=1)
    return DiscussionThread(
        id="thread-active",
        course_id="course-v1:UCM+TFM+2026",
        title="Algorithmic bias in hiring systems",
        created_at=base,
        learning_objectives=[
            "Identify sources of bias in ML pipelines",
            "Analyze real-world case studies",
            "Propose fairness interventions",
        ],
        children=[
            Comment(
                username="Prof. García",
                body=(
                    "How does bias enter ML hiring systems? "
                    "Use at least one real case in your answer."
                ),
                created_at=base,
            ),
            Comment(
                username="Alice",
                body=(
                    "Amazon's recruiting tool is a clear "
                    "example — it penalized resumes with the "
                    "word 'women's' because the training data "
                    "reflected a decade of male-dominated "
                    "hiring. The bias was in the historical "
                    "data, not the algorithm itself."
                ),
                created_at=base + timedelta(hours=3),
            ),
            Comment(
                username="Bob",
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
                username="Carlos",
                body=(
                    "Building on what Bob said — I think the "
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
                username="Diana",
                body=(
                    "Carlos, counterfactual fairness sounds "
                    "great in theory but it requires a causal "
                    "model of the world, which is hard to "
                    "build. In practice, companies use "
                    "demographic parity or equalized odds — "
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
        course_id="course-v1:UCM+TFM+2026",
        title="Open source licensing in AI research",
        created_at=base,
        learning_objectives=[
            "Compare open source license types",
            "Analyze tensions between openness and safety",
            "Evaluate current industry positions",
        ],
        children=[
            Comment(
                username="Prof. García",
                body=(
                    "Should AI models be released under open "
                    "source licenses? Consider the tension "
                    "between reproducibility and potential "
                    "misuse."
                ),
                created_at=base,
            ),
            Comment(
                username="Elena",
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
        course_id="course-v1:UCM+TFM+2026",
        title="Regulation of AI systems in the EU",
        created_at=base,
        learning_objectives=[
            "Analyze the EU AI Act risk categories",
            "Evaluate regulatory approaches",
            "Compare with other jurisdictions",
        ],
        children=[
            Comment(
                username="Prof. García",
                body=(
                    "The EU AI Act classifies AI systems by "
                    "risk level. Do you think this approach "
                    "is effective? What are its limitations?"
                ),
                created_at=base,
            ),
            Comment(
                username="Frank",
                body=(
                    "The EU AI Act is just bureaucratic "
                    "overreach. It will kill innovation in "
                    "Europe while the US and China move ahead "
                    "without these ridiculous constraints."
                ),
                created_at=base + timedelta(hours=2),
            ),
            Comment(
                username="Grace",
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
                username="Frank",
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
        course_id="course-v1:UCM+TFM+2026",
        title="Explainability vs. accuracy tradeoff",
        created_at=base,
        learning_objectives=[
            "Define explainability in ML context",
            "Analyze the accuracy-explainability tradeoff",
            "Identify domain-specific requirements",
        ],
        children=[
            Comment(
                username="Prof. García",
                body=(
                    "When should we prefer an explainable "
                    "model over a more accurate black-box "
                    "model? Is there always a tradeoff?"
                ),
                created_at=base,
            ),
            Comment(
                username="Hana",
                body=(
                    "In healthcare, explainability is "
                    "non-negotiable — doctors need to "
                    "understand why a model recommends a "
                    "treatment. The GDPR also requires "
                    "explanations for automated decisions "
                    "affecting individuals."
                ),
                created_at=base + timedelta(hours=4),
            ),
            Comment(
                username="Ivan",
                body=(
                    "I agree with Hana for high-stakes "
                    "domains. But for things like content "
                    "recommendation, accuracy matters more "
                    "and users don't really need explanations."
                ),
                created_at=base + timedelta(hours=8),
            ),
            Comment(
                username="Julia",
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
                username="Hana",
                body=(
                    "Exactly, Julia. And I'd add that recent "
                    "work on SHAP and LIME shows the tradeoff "
                    "isn't always as stark as it seems — you "
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
        course_id="course-v1:UCM+TFM+2026",
        title="Environmental impact of training large models",
        created_at=base,
        learning_objectives=[
            "Quantify energy consumption of LLM training",
            "Compare with other industries",
            "Propose sustainable AI practices",
        ],
        children=[
            Comment(
                username="Prof. García",
                body=(
                    "Training GPT-4 reportedly consumed "
                    "significant energy. How should we "
                    "balance model capability with "
                    "environmental cost?"
                ),
                created_at=base,
            ),
            Comment(
                username="Kevin",
                body=(
                    "Speaking of GPT-4, did you all see the "
                    "new features they added last week? The "
                    "image generation is incredible. I used "
                    "it to make a poster for my other class."
                ),
                created_at=base + timedelta(hours=2),
            ),
            Comment(
                username="Laura",
                body=(
                    "Yeah the image stuff is cool! I've been "
                    "using it to generate study materials. "
                    "Way better than Midjourney honestly."
                ),
                created_at=base + timedelta(hours=3),
            ),
            Comment(
                username="Kevin",
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


ALL_THREADS = {
    "new": new_thread,
    "active": active_thread,
    "stalled": stalled_thread,
    "conflictive": conflictive_thread,
    "convergent": convergent_thread,
    "off_topic": off_topic_thread,
}
