"""Sample course contexts for evaluation.

Provides CourseContext fixtures that can be paired with thread
fixtures to test pipeline behavior with and without course
context.
"""

from discussion_moderation.common.types import CourseContext

AI_ETHICS_COURSE = CourseContext(
    course_name="AI Ethics and Society",
    module_topic="Ethical implications of AI systems",
    audience_level="graduate",
    language="en",
)

INTRO_CS_COURSE = CourseContext(
    course_name="Introduction to Computer Science",
    module_topic="Foundations of computing",
    audience_level="undergraduate",
    language="en",
)

ML_COURSE_ES = CourseContext(
    course_name="Aprendizaje Automático",
    module_topic="Fundamentos de ML",
    audience_level="graduate",
    language="es",
)

ALL_COURSES = {
    "ai_ethics": AI_ETHICS_COURSE,
    "intro_cs": INTRO_CS_COURSE,
    "ml_es": ML_COURSE_ES,
}
