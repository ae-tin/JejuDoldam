from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from . models import Route, RouteDay, RoutePlace
from .serializers import RouteSerializer, RouteDetailSerializer, RouteDaySerializer, RoutePlaceSerializer


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
            return Response({"message": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        
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
            return Response({"message": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        place.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
        