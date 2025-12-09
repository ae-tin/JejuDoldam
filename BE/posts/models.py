from django.db import models
from django.conf import settings

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

    def __str__(self):
        # admin 페이지에서 보기 좋게
        return f"[{self.id}] {self.title} (by {self.user.username})"