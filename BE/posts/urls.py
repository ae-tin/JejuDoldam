from django.urls import path
from . import views

urlpatterns = [
    # 게시글 목록 조회, 생성
    path("", views.PostListAPIView.as_view()),
    # 게시글 상세조회, 수정, 삭제
    path("<int:post_pk>/", views.PostDetailAPIView.as_view()),
    # 게시글 좋아요
    path("<int:post_pk>/like/", views.LikeAPIView.as_view()),
    # 댓글 생성 및 삭제
    path("<int:post_pk>/comment/", views.CommentAPIView.as_view()),
    path("comment/<int:comment_pk>/", views.CommentAPIView.as_view()),
    
    # 로그인한 사용자가 작성한 게시글 조회
    path("my/", views.MyPostsAPIView.as_view()),
    # 로그인한 사용자가 좋아요한 게시글 조회
    path("my/like/", views.MyLikePostAPIView.as_view()),
]
