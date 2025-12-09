from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from . models import Route
from .serializers import RouteSerializer


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
    GET /routes/<route_pk>/ -> 루트 상세 조회
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
        """
        route = self.get_object(request, route_pk)
        serializer = RouteSerializer(route)
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
    
