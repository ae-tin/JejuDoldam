from django.urls import path
from . import views

urlpatterns = [
    # as_view 메서드가 클래스로 구성되어있는 view를 마치 함수처럼 동작하게 만듦
    path("signup/", views.SignupAPIView.as_view()),
    
]
