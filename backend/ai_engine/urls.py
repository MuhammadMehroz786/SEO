from django.urls import path
from . import views

urlpatterns = [
    path("generate-meta/", views.generate_meta, name="generate-meta"),
    path("generate-alt/", views.generate_alt_text, name="generate-alt"),
    path("score-content/", views.score_content, name="score-content"),
    path("bulk-generate-meta/", views.bulk_generate_meta, name="bulk-generate-meta"),
]
