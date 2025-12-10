from rest_framework import serializers
from .models import Post

class PostSerialzer(serializers.ModelSerializer):
    """
    게시글 기본 CRUD에 사용할 serializer
    - 목록 조회, 상세조회, 작성, 수정에 모두 사용됨
    """
    class Meta:
        model = Post
        fields = "__all__"
        read_only_fields = ["id", "user", "created_at", "updated_at"]