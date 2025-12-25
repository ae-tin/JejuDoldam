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
    # 추천 장소 반환
    path("recommend/places/", views.PlaceRecommendAPIView.as_view()),
    # 추천 루트 반환
    path("recommend/", views.RouteRecommendAPIView.as_view()),
    # 추천/편집 결과 확정
    path("confirm/", views.RouteConfirmAPIView.as_view()),
    # 카카오맵 장소 검색
    path("search/", views.KakaoPlaceSearchAPIView.as_view()),
    # 게시글 상세조회 시 루트 정보 조회
    path("post/<int:route_pk>/", views.RouteDetailInPostAPIView.as_view()),
    
    path("photo/", views.RandomRoutePlaceAPIView.as_view()),
]
