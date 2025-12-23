from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from datetime import date

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
        fields = [
            "username",
            "password",
            "birth_date",
            "gender",
            "marriage_status",
            "job",
            "income",
            "travel_num",
            "residence",
        ]

    def validate_username(self, value):
        """
        username의 중복 체크를 위한 유효성 검사 메서드
        """
        # 만약 이미 사용중인 username 이 있다면 ValidationError를 발생시킴
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("이미 사용 중인 아이디입니다.")
        # 아니라면 사용자가 입력한 username 을 반환함
        return value
    
    def validate_birth_date(self, value):
        """
        생년월일의 유효성 검사 메서드
        """
        if value > date.today():
            raise serializers.ValidationError("생년월일은 미래일 수 없습니다.")
        return value
    
    def validate_travel_num(self, value):
        # 허용값은 우선 임의로 설정
        # TODO 여행 빈도값 확정 후 재작성 필요
        allowed = {1,2,3,4,5,6,7,8,9,10,11,12,15,20,25,30}
        if value not in allowed:
            raise serializers.ValidationError("연간 여행 빈도 값이 허용 범위가 아닙니다.")
        return value

    def create(self, validated_data):
        """
        serailizer.save() 호출 시 실행되는 메서드
        비밀번호 해싱을 위해 반드시 수행되어야 함
        """
        password = validated_data.pop("password")

        # validated_data에 들어있는 모든 프로필 필드까지 포함하여 User 생성
        user = User(**validated_data)

        # set_password -> 해싱된 비밀번호 자동 생성
        user.set_password(password)

        # 최종적으로 DB에 반영
        user.save()
        return user
    

class LoginSirializer(serializers.Serializer):
    """
    로그인 요청으로부터 들어오는 username / password를 검증하고,
    django의 authenticate() 를 호출하여 유효한 사용자 여부를 확인하는 serializer
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attributes):
        """
        전체 필드 검증 메서드.
        is_valid 호출 시:
            1. 각 필드 기본 검사
            2. 필드 레벨 유효성 검사
            3. 마지막으로 이 메서드가 실행됨
        """
        username = attributes.get("username")
        password = attributes.get("password")

        # 만약 둘 중 하나라도 비어있다면 에러
        if not username or not password:
            raise serializers.ValidationError("username과 password는 모두 필수 입력 사항입니다.")

        # username과 password가 일치하다면 로그인된 사용자 객체를 반환하는 함수
        user = authenticate(username=username, password=password)

        # 인증 실패
        if not user:
            raise serializers.ValidationError("아이디 또는 비밀번호가 일치하지 않습니다.")
        
        # 이후 view에서 꺼내서 사용할 수 있도록 user를 넣어두기
        attributes["user"] = user
        return attributes
    

class MeSerializer(serializers.ModelSerializer):
    """
    현재 로그인한 사용자 정보를 조회하는 Serializer
    """
    class Meta:
        model = User
        fields = ["id", "username", ]
        read_only_fields = fields
        
        
class UserInfoUpdateSerializer(serializers.ModelSerializer):
    """
    사용자의 유저 정보를 변경하는 serializer
    """
    class Meta:
        model = User
        fields = ["birth_date", "marriage_status", "job", "income", "travel_num", "residence",]
    
    def validate_birth_date(self, value):
        """
        # 사용자가 입력한 생년월일을 검증함
        """
        if value > date.today():
            raise serializers.ValidationError("생년월일은 미래일 수 없습니다.")
        return value
    
    def update(self, instance, validated_data):
        return super().update(instance, validated_data)