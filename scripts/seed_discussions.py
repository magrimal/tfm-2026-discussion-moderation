"""
Seed synthetic academic discussion threads for a course.

Threads are grounded in typical learning objectives: reflecting on concepts,
applying them to new contexts, debating tradeoffs, and asking clarifying questions.

Run inside the LMS container:
    docker cp scripts/seed_discussions.py main_dev-lms-1:/tmp/seed_discussions.py
    tutor dev exec lms bash -c "./manage.py lms shell < /tmp/seed_discussions.py"
"""

from forum.backends.mysql.api import MySQLBackend

COURSE_ID = "course-v1:OpenedX+DemoX+DemoCourse"

# User IDs present in a default Tutor dev install. Adjust if yours differ.
ADMIN_ID = 4    # username: admin (plays instructor/TA role here)
STUDENT_ID = 14  # username: student
USER1_ID = 6    # username: user-1

backend = MySQLBackend()

# ---------------------------------------------------------------------------
# Threads — academic tone, tied to learning objectives
# ---------------------------------------------------------------------------

threads = [
    # LO: Recall and explain core concepts
    {
        "title": "LO1 — Explain in your own words: what problem does this approach solve?",
        "body": (
            "One of the first learning objectives asks us to articulate the core "
            "problem that the techniques in Unit 1 are designed to solve. Before "
            "looking back at the slides, try writing a two or three sentence "
            "explanation here. What is the problem, and why do existing alternatives "
            "fall short?\n\n"
            "I'll start: the problem as I understand it is that naive approaches "
            "don't scale because they recompute shared subproblems repeatedly. The "
            "techniques in Unit 1 trade memory for time by storing intermediate "
            "results. I'm less clear on when that tradeoff stops being worthwhile."
        ),
        "course_id": COURSE_ID,
        "author_id": USER1_ID,
        "thread_type": "discussion",
        "commentable_id": "course",
    },
    # LO: Apply a concept to a new context
    {
        "title": "LO2 — Applying Unit 2 concepts to a real dataset: what did you try?",
        "body": (
            "The second learning objective asks us to apply the Unit 2 framework to "
            "a dataset outside the course examples. I used a small public dataset "
            "of student click events from a MOOC. A few things I noticed:\n\n"
            "- The preprocessing step took much longer than expected because of "
            "missing values in the timestamp column.\n"
            "- The output matched my intuition for the most part, but one cluster "
            "came out looking like an artefact rather than a real pattern.\n\n"
            "Has anyone else tried applying this to a real dataset? What did you "
            "run into?"
        ),
        "course_id": COURSE_ID,
        "author_id": STUDENT_ID,
        "thread_type": "discussion",
        "commentable_id": "course",
    },
    # LO: Evaluate and compare tradeoffs
    {
        "title": "LO3 — Tradeoff debate: approach A vs approach B from Unit 3",
        "body": (
            "Unit 3 presents two competing approaches to the same problem and asks "
            "us to evaluate their tradeoffs. I want to make sure I'm not missing "
            "anything before the assessment.\n\n"
            "My current read:\n"
            "- Approach A is simpler to implement and reason about, but has worse "
            "worst-case behaviour.\n"
            "- Approach B has better guarantees but requires a non-trivial invariant "
            "to hold at all times, which adds implementation risk.\n\n"
            "The lecture seemed to favour Approach B for production contexts. Does "
            "that match what others took away? Are there cases where A is clearly "
            "the better choice?"
        ),
        "course_id": COURSE_ID,
        "author_id": STUDENT_ID,
        "thread_type": "discussion",
        "commentable_id": "course",
    },
    # LO: Identify assumptions and limits of a model
    {
        "title": "What assumptions does the Unit 4 model make, and when do they break?",
        "body": (
            "LO4 asks us to identify the assumptions underlying the model introduced "
            "in Unit 4 and reason about when they are violated.\n\n"
            "I can spot two assumptions explicitly stated in the lecture:\n"
            "1. The input distribution is stationary (does not shift over time).\n"
            "2. Features are independent given the class label.\n\n"
            "What I'm less sure about: are there implicit assumptions the model "
            "makes that aren't spelled out? I suspect there's something about the "
            "scale of the features, but I couldn't find it clearly stated anywhere."
        ),
        "course_id": COURSE_ID,
        "author_id": USER1_ID,
        "thread_type": "question",
        "commentable_id": "course",
    },
    # LO: Synthesise across units
    {
        "title": "Connecting Units 1-4: where do the concepts build on each other?",
        "body": (
            "As we head into the final unit I'm trying to build a coherent picture "
            "of how the course hangs together. A few connections I can see:\n\n"
            "- The efficiency concern from Unit 1 reappears in Unit 3 when "
            "evaluating approach complexity.\n"
            "- The assumption analysis in Unit 4 seems to require the vocabulary "
            "from Unit 2 to be precise.\n\n"
            "Are there connections I'm missing? I find it easier to retain material "
            "when I can see the structure rather than treating each unit as isolated."
        ),
        "course_id": COURSE_ID,
        "author_id": STUDENT_ID,
        "thread_type": "discussion",
        "commentable_id": "course",
    },
    # LO: Clarifying question on a specific concept
    {
        "title": "Clarification on the convergence condition in the Unit 3 proof",
        "body": (
            "In the Unit 3 lecture the instructor states that the algorithm "
            "converges when the change in the objective falls below a threshold ε, "
            "but then the graded exercise uses a fixed number of iterations instead.\n\n"
            "Are these two stopping conditions equivalent in this context, or is one "
            "strictly stronger? I want to make sure I'm using the right one in my "
            "project."
        ),
        "course_id": COURSE_ID,
        "author_id": USER1_ID,
        "thread_type": "question",
        "commentable_id": "course",
    },
    # LO: Reflective / metacognitive
    {
        "title": "What was the hardest concept to internalise so far, and what helped?",
        "body": (
            "This is a reflective thread for metacognition, which is part of LO5 "
            "(monitoring your own learning). Share: what was the concept that took "
            "the longest to click, and what finally made it make sense?\n\n"
            "For me it was the recurrence relation in Unit 1. What helped was "
            "drawing the recursion tree by hand for a small example. The lecture "
            "alone wasn't enough — I needed to trace it myself."
        ),
        "course_id": COURSE_ID,
        "author_id": ADMIN_ID,
        "thread_type": "discussion",
        "commentable_id": "course",
    },
]

thread_ids = []
for thread_data in threads:
    tid = backend.create_thread(thread_data)
    thread_ids.append(tid)
    print(f"Created thread {tid}: {thread_data['title']!r}")

# ---------------------------------------------------------------------------
# Comments (top-level responses)
# ---------------------------------------------------------------------------

# Each entry: (thread index, author_id, body)
top_level_comments = [
    # Thread 0 — LO1 explain in your own words
    (0, ADMIN_ID,
     "Good framing. I'd add that the 'when does the tradeoff stop being worthwhile' "
     "question is actually central to LO1b. The lecture hint is: look at the "
     "relationship between problem size and the cost of storing intermediate results."),
    (0, STUDENT_ID,
     "My version: the problem is optimisation over a space that has overlapping "
     "subproblems. Without memoisation you revisit the same states exponentially "
     "often. With it you visit each state once. The tradeoff stops making sense when "
     "state space is so large that the memory cost exceeds available resources."),

    # Thread 1 — LO2 apply to real dataset
    (1, ADMIN_ID,
     "The artefact cluster is worth investigating. One common cause is that missing "
     "values filled with a constant (e.g. 0 or -1) form their own cluster because "
     "they're similar to each other, not because they represent a real pattern. "
     "Did you impute before clustering or after?"),
    (1, USER1_ID,
     "I tried a different dataset (product reviews). The biggest surprise was that "
     "the framework assumes numeric features, so I had to encode the categorical "
     "variables first. That step wasn't in the lecture and took a while to sort out."),

    # Thread 2 — LO3 tradeoff debate
    (2, ADMIN_ID,
     "Your reading matches the lecture intent. Approach A is preferred when the "
     "invariant required by B is hard to maintain — typically in distributed systems "
     "where you can't atomically update the shared state. In single-process contexts "
     "B is usually the better default."),
    (2, USER1_ID,
     "One case where I'd pick A: when the dataset is small enough that worst-case "
     "behaviour doesn't matter and the priority is auditability. Approach A is much "
     "easier to step through in a debugger."),

    # Thread 3 — Unit 4 assumptions
    (3, ADMIN_ID,
     "You're right to suspect a feature scale assumption. The model is sensitive to "
     "the relative magnitude of features — if one feature has values in the thousands "
     "and another in the range 0-1, the first will dominate. This is implicit rather "
     "than stated, which is a gap in the lecture I'll flag for the course team."),
    (3, STUDENT_ID,
     "Another implicit assumption I found: the training set is assumed to be "
     "representative of the deployment distribution. The lecture mentions this "
     "briefly in the context of evaluation but doesn't frame it as a model assumption."),

    # Thread 4 — connecting units
    (4, ADMIN_ID,
     "One connection you might be missing: the proof technique in Unit 3 uses the "
     "bounding argument introduced abstractly in Unit 1. They look different on the "
     "surface but they're the same move: show that a quantity decreases monotonically."),
    (4, USER1_ID,
     "The vocabulary point about Unit 2 and Unit 4 is something I noticed too. "
     "Specifically, the term 'feature representation' gets used loosely until Unit 2 "
     "gives it a precise definition, and Unit 4 relies on that precision."),

    # Thread 5 — convergence clarification
    (5, ADMIN_ID,
     "They are not equivalent in general, but they are equivalent here under the "
     "conditions the Unit 3 proof establishes: the objective is strictly decreasing "
     "and bounded below, so after enough iterations the change will be below any ε "
     "you choose. The fixed-iteration version in the exercise is a simplification for "
     "grading purposes. Use the ε condition in your project — it's more principled."),

    # Thread 6 — hardest concept
    (6, STUDENT_ID,
     "For me it was the duality result in Unit 2. I kept treating the two "
     "formulations as just algebraic tricks rather than seeing that they represent "
     "the same problem from different perspectives. What helped: re-reading the "
     "geometric interpretation slowly, then re-deriving it on paper."),
    (6, USER1_ID,
     "The inductive step in the Unit 1 proof was the hardest part for me. I kept "
     "confusing what I was allowed to assume in the hypothesis with what I was "
     "trying to prove. Writing out the assumption and the goal explicitly at the top "
     "of each attempt fixed it."),
]

comment_ids = []
for (thread_idx, author_id, body) in top_level_comments:
    cid = backend.create_comment({
        "body": body,
        "course_id": COURSE_ID,
        "author_id": author_id,
        "comment_thread_id": thread_ids[thread_idx],
    })
    comment_ids.append((thread_idx, cid))
    print(f"Created comment {cid} on thread {thread_ids[thread_idx]}")

# ---------------------------------------------------------------------------
# Replies (depth 1)
# ---------------------------------------------------------------------------

# comment_ids is indexed in insertion order. Map thread index -> list of comment ids
# for easier targeting.
from collections import defaultdict
comments_by_thread = defaultdict(list)
for (tidx, cid) in comment_ids:
    comments_by_thread[tidx].append(cid)

# (thread_idx, parent_comment_index_within_thread, author_id, body)
replies = [
    # Reply to admin's response on Thread 0
    (0, 0, USER1_ID,
     "That's the reference I was missing — the relationship between problem size and "
     "storage cost. Going back to look at that section now."),

    # Reply to admin's response on Thread 1 (missing values point)
    (1, 0, STUDENT_ID,
     "I imputed before clustering with the column median. I think that's what caused "
     "the cluster — the median-filled rows were all similar. Trying mean now to see "
     "if it changes the picture."),

    # Reply to admin's convergence answer on Thread 5
    (5, 0, USER1_ID,
     "That's exactly what I needed. So the fixed-iteration version is sound because "
     "the proof gives us a bound on how many iterations are needed, it's just less "
     "precise than the ε condition. Makes sense."),

    # Reply to student on Thread 6 (duality)
    (6, 0, ADMIN_ID,
     "The geometric interpretation is the right handle for that concept. If it helps: "
     "think of the primal as asking 'what is the best I can do?' and the dual as "
     "asking 'what is the best a certificate of my answer can guarantee?' Strong "
     "duality means these two questions have the same answer."),
]

for (tidx, parent_idx, author_id, body) in replies:
    parent_cid = comments_by_thread[tidx][parent_idx]
    rid = backend.create_comment({
        "body": body,
        "course_id": COURSE_ID,
        "author_id": author_id,
        "comment_thread_id": thread_ids[tidx],
        "parent_id": parent_cid,
        "depth": 1,
    })
    print(f"Created reply {rid} on comment {parent_cid}")

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

from forum.backends.mysql.models import CommentThread, Comment

print(
    f"\nDone. {COURSE_ID} now has "
    f"{CommentThread.objects.filter(course_id=COURSE_ID).count()} threads and "
    f"{Comment.objects.filter(course_id=COURSE_ID).count()} comments/replies."
)
