from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import SignupSerializer, LoginSirializer, MeSerializer, UserInfoUpdateSerializer, UserInfoSettingSerializer
from django.contrib.auth import login
from rest_framework.permissions import IsAuthenticated
import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken # JWT 발급용

User = get_user_model()

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
    PATCH /auth/me/  -> 회원정보 변경 요청
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = MeSerializer(request.user)
        return Response(serializer.data)
    
    def patch(self, request):
        """
        현재 로그인한 사용자의 회원정보를 수정함
        """
        user = request.user
        serializer = UserInfoSettingSerializer(user, request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            if not request.user.is_setting:
                request.user.is_setting = True
            user = serializer.save()
            serializer = MeSerializer(user)
            return Response(serializer.data)
    

class KakaoLoginAPIView(APIView):
    """
    카카오 회원가입/로그인 진행
    """
    def post(self, request):
        # 프론트에서 전달받은 인가 코드(Authorization Code)
        code = request.data.get('code')
        if not code:
            return Response({"error": "코드가 유효하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 토큰 받기(Aceess Token)
        # 백엔드에서 직접 카카오 서버와 통신
        token_req = requests.post(
            "https://kauth.kakao.com/oauth/token",
            headers={"Content-Type": "application/x-www-form-urlencoded;charset=utf-8"},
            data={
                "grant_type": "authorization_code",
                "client_id": settings.KAKAO_REST_API_KEY,
                "redirect_url": settings.KAKAO_REDIRECT_URI,
                "code": code,
                "client_secret": settings.KAKAO_CLIENT_SECRET,
            }
        )
        token_req_json = token_req.json()
        error = token_req_json.get("error")
        # 에러 발생 시
        if error is not None:
            return Response({"error": "카카오 토큰 가져오기 실패"}, status=status.HTTP_400_BAD_REQUEST)
        
        kakao_access_token = token_req_json.get("access_token")
        
        # 사용자 정보 가져오기
        user_info_req = requests.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={
                "Authorization": f"Bearer {kakao_access_token}",
                "Content-Type": "application/x-www-form-urlencoded;charset=utf-8"
            }
        )
        user_info_json = user_info_req.json()
        print(user_info_json)
        # 카카오 계정 정보 추출(이메일, 닉네임 등)
        kakao_account = user_info_json.get("kakao_account")
        email = kakao_account.get('email')
        
        # 로그인, 회원가입 로직 처리
        # 이메일로 기존 회원 확인 (없으면 회원가입)
        if not email:
            return Response({'error': "카카오 계정 정보에서 이메일을 찾을 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
        try:  # todo username으로 바꿔보기
            # 기존 사용자라면 로그인 처리
            user = User.objects.get(email=email)
            
        # 기존사용자가 아니라면 회원가입 처리
        except User.DoesNotExist:
            user = User.objects.create(
                email=email,
                username=email,
                is_setting=False
            )
            user.set_unusable_password()  # 소셜 로그인은 비밀번호를 사용하지 않음
            user.save()
            
        # 서비스 자체의 JWT 토큰 발급(SimpleJWT)
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'is_setting': user.is_setting,
        }, status=status.HTTP_200_OK)
        
        
class KakaoLoginUrlAPIView(APIView):
    def get(self, request):
        """
        프론트에게 '이 주소로 이동해'라고 URL을 만들어주는 API
        API Key를 백엔드 환경변수에서만 관리하려는 목적
        """
        kakao_auth_url = (
            f"https://kauth.kakao.com/oauth/authorize"
            f"?response_type=code"
            f"&client_id={settings.KAKAO_REST_API_KEY}"
            f"&redirect_uri={settings.KAKAO_REDIRECT_URI}"
        )
        return Response({"url": kakao_auth_url})