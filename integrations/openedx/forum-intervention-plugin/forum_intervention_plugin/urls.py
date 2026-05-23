"""URL patterns for the forum intervention plugin."""

from django.urls import path

from . import views

app_name = "forum_intervention"

urlpatterns = [
    path(
        "v1/course-context/<str:course_id>/",
        views.course_context,
        name="course_context",
    ),
]
