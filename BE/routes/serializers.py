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


class RouteRecommendInputSerializer2(serializers.Serializer):
    """
    AI 추천 루트 요청 입력값 검증용 Serializer
    (한국관광공사/여행 빅데이터 코드 체계 기반)
    """

    # 여행 스타일 (자연/도시 선호도)
    TRAVEL_STYL_1 = serializers.ChoiceField(
        choices=[
            (1, "자연 매우선호"),
            (2, "자연 중간선호"),
            (3, "자연 약간선호"),
            (4, "중립"),
            (5, "도시 약간선호"),
            (6, "도시 중간선호"),
            (7, "도시 매우선호"),
        ]
    )

    # 동반 유형
    TRAVEL_STATUS_ACCOMPANY = serializers.ChoiceField(
        choices=[
            ("나홀로 여행", "나홀로 여행"),
            ("2인 여행(가족 외)", "2인 여행(가족 외)"),
            ("3인 이상 여행(가족 외)", "3인 이상 여행(가족 외)"),
            ("2인 가족 여행", "2인 가족 여행"),
            ("자녀 동반 여행", "자녀 동반 여행"),
            ("부모 동반 여행", "부모 동반 여행"),
            ("3대 동반 여행(친척 포함)", "3대 동반 여행(친척 포함)"),
        ]
    )

    # 여행 동기
    TRAVEL_MOTIVE_1 = serializers.ChoiceField(
        choices=[
            ("일상 탈출", "일상 탈출"),
            ("휴식과 충전", "휴식과 충전"),
            ("동반자와의 유대감", "동반자와의 유대감"),
            ("자아 성찰", "자아 성찰"),
            ("SNS / 과시", "SNS / 과시"),
            ("운동 / 건강", "운동 / 건강"),
            ("새로운 경험", "새로운 경험"),
            ("문화 탐방 / 교육", "문화 탐방 / 교육"),
            ("특별한 목적(칠순, 신혼, 수학여행 등)", "특별한 목적(칠순, 신혼, 수학여행 등)"),
            ("기타", "기타"),
        ]
    )

    # 여행 기간 (일수)
    HOW_LONG = serializers.IntegerField(min_value=1, max_value=7)

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