from rest_framework import serializers
from .models import Post, Comment
from routes.models import Route
from routes.serializers import RouteSerializer
from accounts.serializers import MeSerializer

class CommentSerializer(serializers.ModelSerializer):
    """
    댓글 생성 및 삭제에 사용할 serilaizer
    """
    class PostCommentSerializer(serializers.ModelSerializer):
        class Meta:
            model = Post
            fields = ["id", "user"]

    post = PostCommentSerializer(read_only=True)
    user = MeSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = "__all__"
        read_only_fields = ["id", "user", "created_at",]

        
class PostListSerailizer(serializers.ModelSerializer):
    """
    게시글 목록 조회용 serializer
    """
    # view 에서 annotate로 붙은 값을 그대로 받는 필드
    comment_count = serializers.IntegerField(read_only=True)
    like_count = serializers.IntegerField(read_only=True)
    route = RouteSerializer(read_only=True)

    # 요청 유저 기준으로 좋아요 여부 산출
    is_liked = serializers.SerializerMethodField()

    # 작성자 정보 조회
    user = MeSerializer(read_only=True)
    class Meta:
        model = Post
        fields = [
            "id", "title", "content", "created_at", "updated_at",
            "like_count", "is_liked", "comment_count", "route", "user"
        ]

    def get_is_liked(self, obj):
        """
        view에서 context에 담겨져서 넘어오는 request를 꺼내서
        해당 게시글에 좋아요를 눌렀는지 여부 검사
        """
        request = self.context.get("request")

        if not request or request.user.is_anonymous:
            return False
        
        # todo: view 에서 prefetch_related를 사용하면 N + 1 쿼리를 줄이고 성능을 향상 시킬 수 있다는데 알아보고 적용해보자
        return obj.like_users.filter(pk=request.user.pk).exists()



class PostDetailSerializer(serializers.ModelSerializer):
    """
    게시글 상세 조회용 serializer, 댓글 목록, 댓글 개수, 좋아요 수 포함
    """
    # 댓글 목록 조회
    writed_comments = CommentSerializer(many=True, read_only=True)

    like_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    route = RouteSerializer(read_only=True)

    # 유저 정보 같이 넘겨줌
    user = MeSerializer(read_only=True)
    
    class Meta:
        model = Post
        fields = [
            "id", "title", "content", "created_at", "updated_at",
            "like_count", "is_liked", "writed_comments", "route", "user",
        ]

    def get_like_count(self, obj):
        return obj.like_users.count()
    
    def get_is_liked(self, obj):
        request = self.context.get("request")

        if not request or request.user.is_anonymous:
            return False
        return obj.like_users.filter(pk=request.user.pk).exists()
        

class PostCreateUpdateSerializer(serializers.ModelSerializer):
    """
    게시글 생성에서 입력 검증만 담당함
    요청을 보낸 사용자가 저장한 루트만 선택 가능하도록 제한"(route)
    """

    # 관계를 pk로 주고받게 해주는 필드
    # 모델에 관계가 정의되어있을 때 id(pk)로 입출력할 때 사용됨
    route = serializers.PrimaryKeyRelatedField(
        # 인스턴스가 생성되는 시점에 request.user 기준으로
        # 해당 사용자가 저장한 route만 채움
        queryset = Route.objects.none,
        required = False,
        allow_null = True,
    )

    class Meta:
        model = Post
        fields = ["title", "content", "route",]

    def __init__(self, *args, **kwargs):
        # 인스턴스를 만드는 시점에 부모 클래스인 ModelsSrailizer의 생성자를 호출
        # 인스턴스가 만들어지는 시점에 자식 클래스에 정의해놓은 필드들이 생성됨
        # 여기서는 route, title, content 등...
        # 클래스 내부에서 필드를 사용할 수 있음
        super().__init__(*args, **kwargs)

        request = self.context.get("request")
        if request and request.user.is_authenticated:
            self.fields["route"].queryset = Route.objects.filter(user=request.user)


