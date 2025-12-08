from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import SignupSerializer

# Create your views here.

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