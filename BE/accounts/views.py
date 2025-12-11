from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import SignupSerializer, LoginSirializer, MeSerializer
from django.contrib.auth import login
from rest_framework.permissions import IsAuthenticated


class SignupAPIView(APIView):
    """
    POST /auth/signup/
    JSON 데이터를 받아 회원가입을 처리
    """

    def post(self, request):
        # http method가 post일 때만 실행됨
        serializer = SignupSerializer(data=request.data)

        # 데이터 검증 수행
        # is_valid 가 호출되면 자동으로 SignupSerializer 안에 오버라이드 되어있는
        # 유효성 검사 메서드가 호출됨
        if serializer.is_valid():
            # SignupSerializer 안에 오버라이드 되어있는 create 메서드가 호출된다.
            user = serializer.save()
            return Response(
                {"message": "회원가입 성공", "user_id": user.id, "username": user.username},
                status=status.HTTP_201_CREATED
            )
        
        # 유효성 검사 실패 시 에러를 반환함
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class LoginAPIView(APIView):
    """
    POST /auth/login/

    LoginSerializer로 username과 password를 검증하고
    성공하면 user 객체를 꺼내 login(request, user) 호출
    응답으로 로그인 성공 메시지와 일부 사용자 정보를 반환
    """

    def post(self, request):
        serializer = LoginSirializer(data=request.data)

        if serializer.is_valid():
            # validate() 인스턴스 메서드에서 넣어둔 user를 꺼내기
            user = serializer.validated_data["user"]

            # Django의 세션 기반 로그인
            login(request, user)

            return Response(
                {
                    "message": "로그인 성공",
                    "user_id": user.id,
                    "username": user.username,
                }
            )
        # 유효성 검사 실패 시 에러 응답
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class MeAPIView(APIView):
    """
    GET /auth/me/ -> JWT로 로그인된 사용자의 정보를 반환
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = MeSerializer(request.user)
        return Response(serializer.data)