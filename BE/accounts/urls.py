from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # as_view 메서드가 클래스로 구성되어있는 view를 마치 함수처럼 동작하게 만듦
    path("signup/", views.SignupAPIView.as_view()),

    # JWT 로그인(username + password -> access, refresh 발급)
    path("jwt/login/", TokenObtainPairView.as_view()),

    # (access 만료 시 refresh로 재발급)
    path("jwt/refresh/", TokenRefreshView.as_view()),

    # 회원 정보 조회
    path("me/", views.MeAPIView.as_view()),
]
