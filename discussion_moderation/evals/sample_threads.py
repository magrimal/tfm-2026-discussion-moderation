"""Sample discussion threads for evaluation.

Each thread represents a different discussion state (ADR 0003)
in a realistic academic context. Threads are designed to test
whether the agent correctly classifies state, decides on
intervention, and selects an appropriate action.
"""

from datetime import UTC, datetime, timedelta

from discussion_moderation.schemas.discussion import (
    DiscussionThread,
    Post,
)

NOW = datetime(2026, 3, 12, 14, 0, tzinfo=UTC)


def new_thread() -> DiscussionThread:
    """A thread just posted by the instructor, no replies yet."""
    return DiscussionThread(
        topic="Privacy implications of large language models",
        learning_objectives=[
            "Identify privacy risks in LLM training data",
            "Evaluate current mitigation strategies",
            "Propose privacy-preserving alternatives",
        ],
        posts=[
            Post(
                author="Prof. García",
                content=(
                    "This week we're discussing privacy in "
                    "LLMs. Consider: what are the main risks "
                    "when personal data appears in training "
                    "sets? Share your thoughts and respond to "
                    "at least one classmate."
                ),
                timestamp=NOW - timedelta(hours=1),
            ),
        ],
    )


def active_thread() -> DiscussionThread:
    """A healthy, active discussion with peer interaction."""
    base = NOW - timedelta(days=1)
    return DiscussionThread(
        topic="Algorithmic bias in hiring systems",
        learning_objectives=[
            "Identify sources of bias in ML pipelines",
            "Analyze real-world case studies",
            "Propose fairness interventions",
        ],
        posts=[
            Post(
                author="Prof. García",
                content=(
                    "How does bias enter ML hiring systems? "
                    "Use at least one real case in your answer."
                ),
                timestamp=base,
            ),
            Post(
                author="Alice",
                content=(
                    "Amazon's recruiting tool is a clear "
                    "example — it penalized resumes with the "
                    "word 'women's' because the training data "
                    "reflected a decade of male-dominated "
                    "hiring. The bias was in the historical "
                    "data, not the algorithm itself."
                ),
                timestamp=base + timedelta(hours=3),
            ),
            Post(
                author="Bob",
                content=(
                    "Good point Alice. I'd add that even "
                    "removing gender features doesn't help if "
                    "proxy variables like university or "
                    "hobbies correlate with gender. The "
                    "ProPublica analysis of COMPAS showed "
                    "similar proxy issues in criminal justice."
                ),
                timestamp=base + timedelta(hours=5),
            ),
            Post(
                author="Carlos",
                content=(
                    "Building on what Bob said — I think the "
                    "problem is also in the evaluation metric. "
                    "If you optimize for 'past successful "
                    "hires' you're encoding whatever biases "
                    "existed in those decisions. Wouldn't "
                    "counterfactual fairness be a better "
                    "approach?"
                ),
                timestamp=base + timedelta(hours=8),
            ),
            Post(
                author="Diana",
                content=(
                    "Carlos, counterfactual fairness sounds "
                    "great in theory but it requires a causal "
                    "model of the world, which is hard to "
                    "build. In practice, companies use "
                    "demographic parity or equalized odds — "
                    "both have tradeoffs. Which fairness "
                    "metric do you think fits hiring best?"
                ),
                timestamp=base + timedelta(hours=10),
            ),
        ],
    )


def stalled_thread() -> DiscussionThread:
    """A thread where participation died after one reply."""
    base = NOW - timedelta(days=4)
    return DiscussionThread(
        topic="Open source licensing in AI research",
        learning_objectives=[
            "Compare open source license types",
            "Analyze tensions between openness and safety",
            "Evaluate current industry positions",
        ],
        posts=[
            Post(
                author="Prof. García",
                content=(
                    "Should AI models be released under open "
                    "source licenses? Consider the tension "
                    "between reproducibility and potential "
                    "misuse."
                ),
                timestamp=base,
            ),
            Post(
                author="Elena",
                content=(
                    "I think open source is important for "
                    "science but there should be limits."
                ),
                timestamp=base + timedelta(hours=6),
            ),
        ],
    )


def conflictive_thread() -> DiscussionThread:
    """A thread with aggressive or dismissive exchanges."""
    base = NOW - timedelta(days=1)
    return DiscussionThread(
        topic="Regulation of AI systems in the EU",
        learning_objectives=[
            "Analyze the EU AI Act risk categories",
            "Evaluate regulatory approaches",
            "Compare with other jurisdictions",
        ],
        posts=[
            Post(
                author="Prof. García",
                content=(
                    "The EU AI Act classifies AI systems by "
                    "risk level. Do you think this approach "
                    "is effective? What are its limitations?"
                ),
                timestamp=base,
            ),
            Post(
                author="Frank",
                content=(
                    "The EU AI Act is just bureaucratic "
                    "overreach. It will kill innovation in "
                    "Europe while the US and China move ahead "
                    "without these ridiculous constraints."
                ),
                timestamp=base + timedelta(hours=2),
            ),
            Post(
                author="Grace",
                content=(
                    "That's a really superficial take, Frank. "
                    "Maybe if you actually read the Act "
                    "instead of parroting tech bro talking "
                    "points, you'd know that most AI systems "
                    "fall under minimal risk and aren't "
                    "affected at all."
                ),
                timestamp=base + timedelta(hours=3),
            ),
            Post(
                author="Frank",
                content=(
                    "Oh please, spare me the lecture. People "
                    "who've never built anything always love "
                    "to regulate. This is exactly what's "
                    "wrong with academia."
                ),
                timestamp=base + timedelta(hours=4),
            ),
        ],
    )


def convergent_thread() -> DiscussionThread:
    """A thread where participants are reaching consensus."""
    base = NOW - timedelta(days=2)
    return DiscussionThread(
        topic="Explainability vs. accuracy tradeoff",
        learning_objectives=[
            "Define explainability in ML context",
            "Analyze the accuracy-explainability tradeoff",
            "Identify domain-specific requirements",
        ],
        posts=[
            Post(
                author="Prof. García",
                content=(
                    "When should we prefer an explainable "
                    "model over a more accurate black-box "
                    "model? Is there always a tradeoff?"
                ),
                timestamp=base,
            ),
            Post(
                author="Hana",
                content=(
                    "In healthcare, explainability is "
                    "non-negotiable — doctors need to "
                    "understand why a model recommends a "
                    "treatment. The GDPR also requires "
                    "explanations for automated decisions "
                    "affecting individuals."
                ),
                timestamp=base + timedelta(hours=4),
            ),
            Post(
                author="Ivan",
                content=(
                    "I agree with Hana for high-stakes "
                    "domains. But for things like content "
                    "recommendation, accuracy matters more "
                    "and users don't really need explanations."
                ),
                timestamp=base + timedelta(hours=8),
            ),
            Post(
                author="Julia",
                content=(
                    "So it seems like we all agree the "
                    "answer is domain-dependent. High-stakes "
                    "decisions (healthcare, justice, finance) "
                    "need explainability; low-stakes "
                    "applications can prioritize accuracy. "
                    "The real question is where to draw the "
                    "line."
                ),
                timestamp=base + timedelta(hours=12),
            ),
            Post(
                author="Hana",
                content=(
                    "Exactly, Julia. And I'd add that recent "
                    "work on SHAP and LIME shows the tradeoff "
                    "isn't always as stark as it seems — you "
                    "can often get good explanations from "
                    "complex models without sacrificing much "
                    "accuracy."
                ),
                timestamp=base + timedelta(hours=14),
            ),
        ],
    )


def off_topic_thread() -> DiscussionThread:
    """A thread that drifted away from the assigned topic."""
    base = NOW - timedelta(days=1)
    return DiscussionThread(
        topic="Environmental impact of training large models",
        learning_objectives=[
            "Quantify energy consumption of LLM training",
            "Compare with other industries",
            "Propose sustainable AI practices",
        ],
        posts=[
            Post(
                author="Prof. García",
                content=(
                    "Training GPT-4 reportedly consumed "
                    "significant energy. How should we "
                    "balance model capability with "
                    "environmental cost?"
                ),
                timestamp=base,
            ),
            Post(
                author="Kevin",
                content=(
                    "Speaking of GPT-4, did you all see the "
                    "new features they added last week? The "
                    "image generation is incredible. I used "
                    "it to make a poster for my other class."
                ),
                timestamp=base + timedelta(hours=2),
            ),
            Post(
                author="Laura",
                content=(
                    "Yeah the image stuff is cool! I've been "
                    "using it to generate study materials. "
                    "Way better than Midjourney honestly."
                ),
                timestamp=base + timedelta(hours=3),
            ),
            Post(
                author="Kevin",
                content=(
                    "Totally. And the coding assistant is "
                    "getting scary good. I wonder if we'll "
                    "even need to learn programming in a few "
                    "years lol."
                ),
                timestamp=base + timedelta(hours=5),
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
