from django.db import models
from django.conf import settings
from routes.models import Route

# Create your models here.


class Post(models.Model):
    """
    게시글에 관련된 모델

    - 어떤 유저가 작성한 글인지: user(FK)
    - 제목, 내용, 작성/수정 시각
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts",
    )
    title = models.CharField(max_length=200)
    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)  # 최초 생성 시 자동 저장
    updated_at = models.DateTimeField(auto_now=True)      # 저장될 때마다 자동 갱신
    
    # 게시글 작성자의 루트(추가 여부는 선택사항)
    route = models.ForeignKey(Route, on_delete=models.SET_NULL, null=True, blank=True, default=None)
    
    # 게시글 좋아요
    like_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='like_posts',)

    def __str__(self):
        # admin 페이지에서 보기 좋게
        return f"[{self.id}] {self.title} (by {self.user.username})"
    

class Comment(models.Model):
    """
    댓글에 관련된 모델
    - 어떤 유저가 작성한 댓글인지(FK)
    - 어떤 게시글에 작성된 댓글인지(FK)
    """
    # 어떤 유저가 작성한 댓글인지
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="write_comments",
    )

    # 어떤 게시글에 작성된 댓글인지
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="writed_comments",)

    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)