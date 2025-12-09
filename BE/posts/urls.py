from django.urls import path
from . import views

urlpatterns = [
    path("", views.PostListCreateAPIView.as_view()),
    path("<int:post_pk>/", views.PostDetailAPIView.as_view()),
]
