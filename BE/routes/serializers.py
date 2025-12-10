from rest_framework import serializers
from .models import Route, RouteDay, RoutePlace


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ["id", "title", "description", "created_at"]
        read_only_fields = ["id", "created_at"]
        # user 정보는 view에서 request.user로 넣기로 함


class RoutePlaceSerializer(serializers.ModelSerializer):
    """
    일차(RouteDay)에 포함된 개별 장소 정보
    """
    class Meta:
        model = RoutePlace
        fields = ["id", "order", "name", "address", "latitude", "longitude", "memo",]
        read_only_fields = ["id", ]


class RouteDaySerializer(serializers.ModelSerializer):
    """
    루트의 N일차 정보 + 그 날의 장소 목록
    """
    # palces 역참조
    places = RoutePlaceSerializer(many=True, read_only=True)

    class Meta:
        model = RouteDay
        fields = ["id", "day", "places", ]
        read_only_fields = ["id", ]
    

class RouteDetailSerializer(serializers.ModelSerializer):
    """
    루트 상세 조회용 Route Serializer
    days + places까지 중첩하여 응답
    RouteDaySerilaizer(RoutePlaceSerializer) 중첩 구조
    """
    
    # days 역참조
    days = RouteDaySerializer(many=True, read_only=True)

    class Meta:
        model = Route
        fields = ["id", "title", "description", "created_at", "days", ]
        read_only_fields = fields