from django.urls import path
from . import views

urlpatterns = [
    # 게시글 목록 조회
    path("", views.PostListAPIView.as_view()),
    # 게시글 생성
    path("create/", views.PostCreateAPIView.as_view()),
    # 게시글 상세조회
    path("<int:post_pk>/", views.PostDetailAPIView.as_view()),
    # 게시글 수정 및 삭제
    path("<int:post_pk>/operation/", views.PostUpdateDeleteAPIView.as_view()),
    # 게시글 좋아요
    path("<int:post_pk>/like/", views.LikeAPIView.as_view()),
    # 댓글 생성 및 삭제
    path("<int:post_pk>/comment/", views.CommentAPIView.as_view()),
    path("comment/<int:comment_pk>/", views.CommentAPIView.as_view()),
]
