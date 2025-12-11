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


class RouteRecommendInputSerializer(serializers.Serializer):
    """
    AI 추천 루트를 요청할 때 사용하는 입력 값 검증용 serializer
    (DB 모델이 아닌 단순 요청 검증용)
    """
    days = serializers.IntegerField(min_value=1, max_value=7)
    companion_type = serializers.ChoiceField(
        choices=["COUPLE", "FRIENDS", "FAMILY", "SOLO"]
    )
    transport = serializers.ChoiceField(
        choices=["CAR", "BUS"]
    )
    
    # 사용자로부터 태그가 리스트로 들어올 것이기 때문에 선택한 모든 태그를 리스트로 받음
    themes = serializers.ListField(
        child=serializers.ChoiceField(
            choices=["HEALING", "CAFE", "FOOD", "ACTIVITY"]
        ),
        required=False
    )



class RoutePlaceInputSerializer(serializers.Serializer):
    """
    확정 API에서 사용하는 장소 입력용 Serializer
    (DB 모델과 직접 연결되지 않고, 요청 JSON 구조만 검증)
    """
    order = serializers.IntegerField(min_value=1)
    name = serializers.CharField(max_length=200)
    address = serializers.CharField(max_length=255, required=False, allow_blank=True)
    latitude = serializers.FloatField(required=False, allow_null=True)
    longitude = serializers.FloatField(required=False, allow_null=True)
    memo = serializers.CharField(required=False, allow_blank=True)


class RouteDayInputSerializer(serializers.Serializer):
    """
    확정 API에서 사용하는 '일차 입력용' Serializer
    """
    day = serializers.IntegerField(min_value=1)
    places = RoutePlaceInputSerializer(many=True)


class RouteConfirmInputSerializer(serializers.Serializer):
    """
    추천/편집 결과를 확정하고 저장할 때 사용하는 최상위 입력 Serializer
    -> title, description, days[day, places[]] 구조 검증
    """
    title = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True)
    days = RouteDayInputSerializer(many=True)