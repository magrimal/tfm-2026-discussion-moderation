"""Views for the forum intervention plugin facilitation API."""

from datetime import datetime, timezone

from django.http import JsonResponse
from django.views.decorators.http import require_GET
from opaque_keys.edx.keys import CourseKey

from openedx.core.djangoapps.content.learning_sequences.api import (
    get_user_course_outline,
)


@require_GET
def course_context(request, course_id: str) -> JsonResponse:
    """Return course outline context for the facilitation pipeline.

    GET /api/facilitation/v1/course-context/<course_id>/

    Returns JSON with:
      display_name (str): course title
      sections (list): one entry per CourseSectionData:
          title (str): section title
          sequences (list[str]): sequence titles within the section

    Not available from this API (TODO for future work):
      language: not exposed by get_user_course_outline
      course_start / course_end: requires get_user_course_outline_details,
          which is a heavier call
    """
    course_key = CourseKey.from_string(course_id)
    outline = get_user_course_outline(
        course_key=course_key,
        user=request.user,
        at_time=datetime.now(tz=timezone.utc),
    )

    sections = [
        {
            "title": section.title,
            "sequences": [seq.title for seq in section.sequences],
        }
        for section in outline.sections
    ]

    return JsonResponse(
        {
            "course_id": course_id,
            "display_name": outline.title,
            "sections": sections,
        }
    )
