from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

class SignupSerializer(serializers.ModelSerializer):
    """
    회원가입 요청으로 들어오는 JSON 데이터를 검증하고
    User 모델 인스턴스를 실제로 생성해주는 serializer 입니다.
    """

    # 응답 JSON에는 노출되지 않음
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "password",]

    def validate_username(self, value):
        """
        username의 중복 체크를 위한 유효성 검사 메서드
        """
        # 만약 이미 사용중인 username 이 있다면 ValidationError를 발생시킴
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("이미 사용 중인 아이디입니다.")
        # 아니라면 사용자가 입력한 username 을 반환함
        return value
    
    def create(self, validated_data):
        """
        serailizer.save() 호출 시 실행되는 메서드
        비밀번호 해싱을 위해 반드시 수행되어야 함
        """
        password = validated_data.pop("password")

        # username, nickname만 삽입
        user = User(**validated_data)

        # set_password -> 해싱된 비밀번호 자동 생성
        user.set_password(password)

        # 최종적으로 DB에 반영
        user.save()
        return user