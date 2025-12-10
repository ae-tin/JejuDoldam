from django.urls import path
from . import views

urlpatterns = [
    path("", views.RouteListCreateAPIView.as_view()),
    path("<int:route_pk>/", views.RouteDetailAPIView.as_view()),
    # 일차 추가
    path("<int:route_pk>/days/", views.RouteDayCreateAPIView.as_view()),
    # 일차 수정 및 삭제
    path("days/<int:day_pk>/", views.RouteDayDetailAPIView.as_view()),
    # 특정 일차에 장소 추가
    path("days/<int:day_pk>/places/", views.RoutePlaceCreateAPIView.as_view()),
    # 특정 장소 수정/삭제
    path("places/<int:place_pk>/", views.RoutePlaceDetailAPIView.as_view()),
    
]
