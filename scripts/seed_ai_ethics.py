"""
Seed synthetic discussion threads into the Ethics in AI course.

Copy files into the container, then run the script:

    docker cp scripts/seed_ai_ethics.py main_dev-lms-1:/tmp/seed_ai_ethics.py
    docker cp docs/threads/ai-ethics main_dev-lms-1:/tmp/threads_ai_ethics
    tutor dev exec lms bash -c "./manage.py lms shell < /tmp/seed_ai_ethics.py"
"""

import json
from pathlib import Path

from django.contrib.auth.models import User
from forum.backends.mysql.api import MySQLBackend

# ── Configuration ────────────────────────────────────────────────────────────
# Adjust to match the actual course key shown in Studio.
COURSE_ID = "course-v1:openedx+ETHICS+2026"  # TODO: replace with actual course key

# Map each thread file to the discussion XBlock url_name it belongs to.
THREAD_MAPPING = [
    ("formulaic.json",           "unit1_discuss"),
    ("hostile_then_silent.json", "unit2_discuss"),
    ("integration_phase.json",   "unit3_discuss"),
]

THREADS_DIR = Path("/tmp/threads_ai_ethics")
# ─────────────────────────────────────────────────────────────────────────────

backend = MySQLBackend()


def get_or_create_user(username):
    user, created = User.objects.get_or_create(
        username=username,
        defaults={"email": f"{username}@example.com", "is_active": True},
    )
    if created:
        user.set_unusable_password()
        user.save()
        print(f"  [new user] {username} (id={user.id})")
    return user.id


for filename, commentable_id in THREAD_MAPPING:
    data = json.loads((THREADS_DIR / filename).read_text())
    children = data["children"]
    if not children:
        print(f"Skipping {filename}: no posts")
        continue

    first = children[0]
    author_id = get_or_create_user(first["username"])

    thread_id = backend.create_thread({
        "title": data["title"],
        "body": first["body"],
        "course_id": COURSE_ID,
        "author_id": author_id,
        "thread_type": "discussion",
        "commentable_id": commentable_id,
    })
    print(f"Thread {thread_id}: {data['title']!r} → {commentable_id}")

    for comment in children[1:]:
        commenter_id = get_or_create_user(comment["username"])
        backend.create_comment({
            "body": comment["body"],
            "course_id": COURSE_ID,
            "author_id": commenter_id,
            "comment_thread_id": thread_id,
        })
    print(f"  {len(children) - 1} comments added")

from forum.backends.mysql.models import CommentThread, Comment

print(
    f"\nDone. {COURSE_ID} now has "
    f"{CommentThread.objects.filter(course_id=COURSE_ID).count()} threads and "
    f"{Comment.objects.filter(course_id=COURSE_ID).count()} comments."
)
