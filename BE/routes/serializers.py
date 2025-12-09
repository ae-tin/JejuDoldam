from rest_framework import serializers
from .models import Route


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ["id", "title", "description", "created_at"]
        read_only_fields = ["id", "created_at"]
        # user 정보는 view에서 request.user로 넣기로 함