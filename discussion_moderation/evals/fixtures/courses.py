"""Sample course contexts for evaluation.

Provides CourseContext fixtures that can be paired with thread
fixtures to test pipeline behavior with and without course
context.
"""

from discussion_moderation.models import CourseContext

AI_ETHICS_COURSE = CourseContext(
    course_id="course-v1:UCM+AIEthics+2026",
    display_name="AI Ethics and Society",
    sections=[
        "Foundations of AI Ethics",
        "Case Studies",
        "Policy and Governance",
    ],
    module_topic="Ethical implications of AI systems",
    language="en",
)

INTRO_CS_COURSE = CourseContext(
    course_id="course-v1:UCM+IntroCS+2026",
    display_name="Introduction to Computer Science",
    sections=["Algorithms", "Data Structures", "Software Engineering Basics"],
    module_topic="Foundations of computing",
    language="en",
)

ML_COURSE_ES = CourseContext(
    course_id="course-v1:UCM+ML+2026",
    display_name="Aprendizaje Automático",
    sections=["Regresión", "Clasificación", "Redes Neuronales"],
    module_topic="Fundamentos de ML",
    language="es",
)

ALL_COURSES = {
    "ai_ethics": AI_ETHICS_COURSE,
    "intro_cs": INTRO_CS_COURSE,
    "ml_es": ML_COURSE_ES,
}
