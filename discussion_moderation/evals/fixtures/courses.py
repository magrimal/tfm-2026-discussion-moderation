"""Sample course contexts for evaluation.

Provides CourseContext fixtures that can be paired with thread
fixtures to test pipeline behavior with and without course
context.
"""

from discussion_moderation.models import CourseContext, CourseSection

AI_ETHICS_COURSE = CourseContext(
    course_id="course-v1:UCM+AIEthics+2026",
    display_name="AI Ethics and Society",
    sections=[
        CourseSection(
            title="Module 1: Foundations of AI Ethics",
            sequences=["Introduction", "Key Concepts", "Historical Context"],
        ),
        CourseSection(
            title="Module 2: Case Studies",
            sequences=["Bias in Hiring Algorithms", "Autonomous Vehicles"],
        ),
        CourseSection(
            title="Module 3: Policy and Governance",
            sequences=["Regulatory Frameworks", "International Perspectives"],
        ),
    ],
)

INTRO_CS_COURSE = CourseContext(
    course_id="course-v1:UCM+IntroCS+2026",
    display_name="Introduction to Computer Science",
    sections=[
        CourseSection(
            title="Module 1: Algorithms",
            sequences=["Sorting", "Searching", "Complexity"],
        ),
        CourseSection(
            title="Module 2: Data Structures",
            sequences=["Lists", "Trees", "Graphs"],
        ),
    ],
)

ML_COURSE_ES = CourseContext(
    course_id="course-v1:UCM+ML+2026",
    display_name="Aprendizaje Automático",
    sections=[
        CourseSection(
            title="Módulo 1: Regresión",
            sequences=["Regresión lineal", "Regresión logística"],
        ),
        CourseSection(
            title="Módulo 2: Clasificación",
            sequences=["k-NN", "SVM", "Árboles de decisión"],
        ),
        CourseSection(
            title="Módulo 3: Redes Neuronales",
            sequences=["Perceptrón", "Backpropagation"],
        ),
    ],
)

ALL_COURSES = {
    "ai_ethics": AI_ETHICS_COURSE,
    "intro_cs": INTRO_CS_COURSE,
    "ml_es": ML_COURSE_ES,
}
