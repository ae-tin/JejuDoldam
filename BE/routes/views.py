import requests
from django.db import transaction, IntegrityError
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Route, RouteDay, RoutePlace
from .utils import preprocessing_input_data
from accounts.models import User
from .serializers import (
    RouteSerializer,
    RouteDetailSerializer,
    RouteDaySerializer,
    RoutePlaceSerializer,
    RouteRecommendInputSerializer2,
    RouteDayInputSerializer,
    RoutePlaceInputSerializer,
    RouteConfirmInputSerializer,
)


# Create your views here.

class RouteListCreateAPIView(APIView):
    """
    GET /routes/ -> 내 루트 목록 조회
    POST/ routes/ -> 새로운 루트 생성
    """

    # 로그인한 사용자만 상호작용 하도록 설정
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        로그인한 모든 사용자의 루트를 최신순으로 조회함
        """
        routes = Route.objects.filter(user=request.user).order_by("-created_at")
        serializer = RouteSerializer(routes, many=True)
        return Response(serializer.data)


    def post(self, request):
        """
        로그인한 사용자의 요청을 받아 새로운 루트를 생성함
        """
        serializer = RouteSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            route = serializer.save(user=request.user)
            return Response(RouteSerializer(route).data, status=status.HTTP_201_CREATED)
        


class RouteDetailAPIView(APIView):
    """
    GET /routes/<route_pk>/ -> 루트 상세 조회 (일차 + 장소까지 중첩하여 응답)
    PUT /routes/<route_pk>/ -> 루트 전체 수정
    PATCH /routes/<route_pk>/ -> 루트 일부 수정
    DELETE /routes/<route_pk>/ -> 루트 삭제
    """
    
    # 로그인한 사용자만 상호작용 하도록 설정
    permission_classes = [IsAuthenticated]

    def get_object(self, request, route_pk):
        """
        요청한 route_pk에 따라 해당 사용자의 루트만 조회하도록 제한
        """
        return get_object_or_404(Route, pk=route_pk, user=request.user)


    def get(self, request, route_pk):
        """
        로그인한 사용자의 루트를 상세조회하는 함수
        루트 + days + places 까지 포함하여 상세조회
        """
        route = self.get_object(request, route_pk)
        serializer = RouteDetailSerializer(route)
        return Response(serializer.data)
    

    def put(self, request, route_pk):
        """
        로그인한 사용자의 루트를 전체 수정하는 함수
        """
        route = self.get_object(request, route_pk)
        serializer = RouteSerializer(route, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
        
        
    def patch(self, request, route_pk):
        """
        로그인한 사용자의 루트를 일부 수정하는 함수
        """
        route = self.get_object(request, route_pk)
        serializer = RouteSerializer(route, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
        

    def delete(self, request, route_pk):
        """
        로그인한 사용자의 루트를 삭제하는 함수
        """
        route = self.get_object(request, route_pk)
        route.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    


class RouteDayCreateAPIView(APIView):
    """
    POST/ routes/<route_pk>/days/
    -> 해당 루트에 일차를 하나 추가
    """

    # 로그인한 사용자만 접근 가능
    permission_classes = [IsAuthenticated]

    def post(self, request, route_pk):
        # 자신의 루트가 아니면 접근할 수 없음
        route = get_object_or_404(Route, pk=route_pk, user=request.user)

        # 사용자의 요청으로부터 일차(day) 값을 받아옴
        serializer = RouteDaySerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            # route를 강제로 지정하여 RouteDay 생성
            # 필드가 unique_together로 지정되어있어 같은 day가 두번 들어오면 에러 발생
            try:
                route_day = serializer.save(route=route)
            except Exception:
                # 이미 같은 day가 있는 경우
                return Response({"detail": "이미 해당 일차가 존재합니다."}, status=status.HTTP_400_BAD_REQUEST)
            
            # 무사히 지나와서 저장이 완료되었다면 정상 응답
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        

class RouteDayDetailAPIView(APIView):
    """
    PATCH /routes/days/<day_pk>/  -> 일차 정보 수정(day 번호 바꾸기)
    DELETE /routes/days/<day_pk>/  -> 해당 일차 및 그 안의 장소 전부 삭제
    """

    # 로그인한 사용자만 접근 가능
    permission_classes = [IsAuthenticated]
    
    def get_object(self, requset, day_pk):
        """
        요청을 보낸 사용자의 루트인지 확인하고 아니라면 None을 반환함
        """
        route_day = get_object_or_404(RouteDay, pk=day_pk)
        if route_day.route.user != requset.user:
            return None
        return route_day

    def patch(self, request, day_pk):
        route_day = get_object_or_404(RouteDay, pk=day_pk)
        # 요청을 보낸 사용자의 루트가 아니면 None이 반환되었을 것
        if route_day is None:
            return Response({"detail": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = RouteDaySerializer(route_day, data=request.data, partial=True)

        if serializer.is_valid(raise_exception=True):
            try:
                serializer.save()
            except Exception:
                # 이미 일차가 존재하면 실패함
                return Response({"detail": "해당 일차가 이미 존재합니다."}, status=status.HTTP_400_BAD_REQUEST)
            
            # 무사히 넘어왔다면 저장 성공 응답
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    def delete(self, request, day_pk):
        route_day = get_object_or_404(RouteDay, pk=day_pk)
        # 요청을 보낸 사용자의 루트가 아니면 None이 반환되었을 것
        if route_day is None:
            return Response({"detail": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        route_day.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class RoutePlaceCreateAPIView(APIView):
    """
    POST /routes/days/<day_pk>/places/
    """
    
    # 로그인한 사용자만 접근 가능
    permission_classes = [IsAuthenticated]

    def post(self, request, day_pk):
        # day_pk로 RouteDay 조회 + 요청한 유저의 Route에 속해있는지 확인
        route_day = get_object_or_404(RouteDay, pk=day_pk)
        if route_day.route.user != request.user:
            return Response({"message": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        
        # 사용자의 요청으로부터 장소 정보를 받아옴
        serializer = RoutePlaceSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            try:
                place = serializer.save(route_day=route_day)
            except Exception:
                # unique_together 때문에 route_day 및 order 중복 불가
                return Response({"detail": "해당 일차에 이미 같은 순서의 장소가 있습니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 무사히 저장이 지나와서 저장이 완료되었다면 정상 응답
        return Response(RoutePlaceSerializer(place).data, status=status.HTTP_201_CREATED)


class RoutePlaceDetailAPIView(APIView):
    """
    PATCH /routes/places/<place_pk>/  -> 장소 정보 수정(이름, 메모, 순서 등)
    DELETE /routes/places/<place_pk>/  -> 장소 정보 삭제
    """

    # 로그인한 사용자만 접근 가능
    permission_classes = [IsAuthenticated]

    def get_object(self, requset, place_pk):
        """
        요청을 보낸 사용자의 루트인지 확인하고 아니라면 None을 반환함
        """
        place = get_object_or_404(RoutePlace, pk=place_pk)
        if place.route_day.route.user != requset.user:
            return None
        return place
    
    def patch(self, request, place_pk):
        place = self.get_object(request, place_pk)
        if place is None:
            return Response({"detail": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = RoutePlaceSerializer(place, data=request.data, partial=True)

        if serializer.is_valid(raise_exception=True):
            try:
                serializer.save()
            except Exception:
                # route_day 혹은 order 중복으로 저장 실패
                return Response({"detail": "해당 일차에 이미 같은 순서의 장소가 존재합니다."}, status=status.HTTP_400_BAD_REQUEST)
            
        # 무사히 저장 완료 응답
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

    def delete(self, request, place_pk):
        place = self.get_object(request, place_pk)
        if place is None:
            return Response({"detail": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        place.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RouteRecommendAPIView(APIView):
    """
    POST /routes/recommend/
    -> 여행 조건을 받아서 추천 루트 리스트를 반환
    (지금은 하드코딩된 더미를 사용, 나중에 여기서 AI 로직을 호출할 예정)

    example_user = {
        "GENDER": "남",
        "AGE_GRP": "30",
        "MARR_STTS": "1",
        "JOB_NM": "3",
        "INCOME": 4,
        "TRAVEL_STYL_1": "2",
        "TRAVEL_STATUS_RESIDENCE": "서울특별자치도",
        "TRAVEL_STATUS_ACCOMPANY": "2인 여행(가족 외)",
        "TRAVEL_MOTIVE_1": "7",
        "TRAVEL_NUM": 3,
        "TRAVEL_COMPANIONS_NUM": 1,
        "MONTH": "8",
        "SEASON": "summer",
        "HOW_LONG": 3,
    }
    """
    # 로그인한 사용자만 접근 가능
    permission_classes = [IsAuthenticated]

    def post(self, request):
        
        # 입력값 검증
        serializer = RouteRecommendInputSerializer2(data=request.data)
        # 유효성 검사
        serializer.is_valid(raise_exception=True)
        # 유효성 검사를 통과한 깨끗한 데이터를 변수에 할당
        data = serializer.validated_data
        
        # 유저 DB 정보 로드
        user_data = get_object_or_404(User, username=request.user)
        user_info = {
            "GENDER": user_data.gender, # pass
            "AGE_GRP": user_data.birth_date, # calculate in AI API
            "MARR_STTS": user_data.marriage_status, # pass
            "JOB_NM": user_data.job, # pass
            "INCOME": user_data.income, # pass
            "TRAVEL_NUM": user_data.travel_num, # pass
            "TRAVEL_STATUS_RESIDENCE": user_data.residence, # pass
        }
        
        ai_input_data = {
            **user_info,
            **data,
        }
        ai_input_data = preprocessing_input_data(ai_input_data)

        print(ai_input_data)

        AI_SERVER_URL = "http://127.0.0.1:8001/route_rec_ai"
        ai_response = requests.post(
            AI_SERVER_URL,
            json=ai_input_data,
            timeout=5
        )

        ai_result = ai_response.json()
        # AI 추천 대신 더미 데이터 생성
        print('*'*30,"성공",'*'*30)
        print(ai_result["result"][0])
        print('*'*30,"성공",'*'*30)
        dummy_routes = self.create_dummy_routes(data)
        return Response(dummy_routes)
    

    def create_dummy_routes(self, data: dict) -> list[dict]:
        """
        나중에 ai 로직 구현이 완료되면 여기서 호출함
        지금은 더미 데이터를 하드코딩으로 생성하여 반환
        """
        days = data["days"]
        return [
            {
                "id": 1,
                "title": f"동부 힐링 루트 ({days}일)",
                "description": "성산일출봉 · 우도 · 섭지코지 중심 힐링 코스",
                "days": days,
                "places": [
                    {"day": 1, "order": 1, "name": "성산일출봉"},
                    {"day": 1, "order": 2, "name": "섭지코지"},
                    {"day": 2, "order": 1, "name": "우도"},
                ],
            },
            {
                "id": 2,
                "title": f"서부 카페투어 루트 ({days}일)",
                "description": "협재·애월 카페 위주의 여유로운 코스",
                "days": days,
                "places": [
                    {"day": 1, "order": 1, "name": "협재해수욕장"},
                    {"day": 1, "order": 2, "name": "애월 카페 거리"},
                ],
            },
            {
                "id": 3,
                "title": f"남부 맛집 루트 ({days}일)",
                "description": "서귀포 중심 맛집 & 관광 코스",
                "days": days,
                "places": [
                    {"day": 1, "order": 1, "name": "서귀포 매일 올레 시장"},
                    {"day": 1, "order": 2, "name": "정방폭포"},
                ],
            },
        ]
    


class RouteConfirmAPIView(APIView):
    """
    POST /api/v1/routes/confirm/
    -> 추천 결과(혹은 편집 완료된 루트)를 한번에 DB에 저장

    요청 예시:
    {
      "title": "3박 4일 제주 힐링 여행",
      "description": "동부 위주 힐링 코스",
      "days": [
        {
          "day": 1,
          "places": [
            {"order": 1, "name": "성산일출봉", ...},
            {"order": 2, "name": "섭지코지", ...}
          ]
        },
        ...
      ]
    }
    하나의 액션으로 Route 1개, RouteDay N개, RoutePlace M개를 전부 생성해야 함
    중간에 하나라도 실패하면 전체를 롤백해야 함
    """

    # 로그인한 사용자만 접근 가능
    permission_classes = [IsAuthenticated]

    @transaction.atomic  # 여러번 DB 작업이 일어나도 전부 성공하면 commit 처리, 중간에 하나라도 실패하면 rollback
    def post(self, request):
        # 요청 JSON 구조/타입 검증
        serializer = RouteConfirmInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # 직렬화 완료되고, 유효성검사가 완료된 깨끗한 데이터만 변수에 할당
        data = serializer.validated_data

        # 트랜잭션 내부에서 Route + Day + Place 한번에 생성
        try:
            route = self.create_route_days_places(request.user, data)
        except IntegrityError:
            # DB unique 관련 에러 발생 시
            return Response({"detail": "중복된 day 또는 장소 또는 순서(order)가 존재합니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 생성된 Route 전체 구조를 상세 serializer로 응답
        output_serializer = RouteDetailSerializer(route)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    def create_route_days_places(slef, user, data: dict) -> Route:
        """
        validated_data를 바탕으로
        Route 1개
        RouteDay N개
        RoutePlace M개
        를 생성하고 최종 Route 인스턴스를 반환
        """
        # Route 생성
        route = Route.objects.create(
            user=user,
            title=data["title"],
            description=data.get("description", ""),
        )

        # 각 day 데이터에 대해 RouteDay + RoutePlace 생성
        # data["days"]를 순회
        # day_data에는 일차(day), 장소(places)에 대한 정보가 담겨있음
        for day_data in data["days"]:
            # 일차 정보를 생성
            route_day = RouteDay.objects.create(route=route, day=day_data["day"])
            # 생성된 일차 정보의 장소를 순회하며 일차와 장소를 매핑
            for place_data in day_data["places"]:
                RoutePlace.objects.create(
                    route_day = route_day,
                    order = place_data["order"],
                    name=place_data["name"],
                    address=place_data.get("address", ""),  # 선택 입력 사항은 .get으로 처리
                    latitude=place_data.get("latitude"),
                    longitude=place_data.get("longitude"),
                    memo=place_data.get("memo", ""),
                )
        # 완성된 Route 객체를 반환
        return route