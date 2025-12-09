from django.urls import path
from . import views

urlpatterns = [
    path("", views.RouteListCreateAPIView.as_view()),
    path("<int:route_pk>/", views.RouteDetailAPIView.as_view()),
]
