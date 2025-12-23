from django.shortcuts import get_list_or_404, get_object_or_404
from .models import Post, Comment
from .serialzers import PostListSerailizer, PostDetailSerializer, CommentSerializer, PostCreateUpdateSerializer
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
# Create your views here.


User = get_user_model()

class PostListAPIView(APIView):
    """
    Get /posts/ -> 게시글 목록 조회
    POST /posts/ -> 게시글 작성
    """
    # 로그인 하지 않은 사용자는 상호작용 할 수 없음
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        사용자의 GET 요청을 받아 작성된 모든 게시글을 조회하는 함수
        """
        # 최신순으로 정렬
        posts = Post.objects.annotate(
            comment_count=Count("writed_comments", distinct=True),
            like_count=Count("like_users", distinct=True),
        ).order_by("-created_at")

        serializer = PostListSerailizer(posts, many=True, context={"request":request})
        return Response(serializer.data)


class PostCreateAPIView(APIView):
    """
    사용자의 요청을 받아 게시글 생성
    """
    
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        POST -> 게시글 생성
        """
        serializer = PostCreateUpdateSerializer(data=request.data, context={"request":request})

        if serializer.is_valid(raise_exception=True):
            post = serializer.save(user=request.user)
            return Response(PostCreateUpdateSerializer(post).data, status=status.HTTP_201_CREATED)


class PostUpdateDeleteAPIView(APIView):
    """
    사용자의 요청을 받아 게시글을 수정 및 삭제
    """ 

    permission_classes = [IsAuthenticated]

    def patch(self, request, post_pk):
        post = get_object_or_404(Post, pk=post_pk)

        serializer = PostCreateUpdateSerializer(post, data=request.data, partial=True, context={"request":request})

        if request.user != post.user:
            return Response({"message": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        if serializer.is_valid(raise_exception=True):
            post = serializer.save(user=request.user)
            return Response(PostCreateUpdateSerializer(post).data)
        
    def delete(self, request, post_pk):
        post = get_object_or_404(Post, pk=post_pk)
        
        if request.user != post.user:
            return Response({"message": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

        

class PostDetailAPIView(APIView):
    """
    GET    /posts/<id>/   → 게시글 상세 조회
    PUT    /posts/<id>/   → 게시글 전체 수정
    PATCH  /posts/<id>/   → 게시글 부분 수정
    DELETE /posts/<id>/   → 게시글 삭제
    """
    # 로그인한 사용자만 상호작용 가능
    permission_classes = [IsAuthenticated]

    # 요청된 pk에 맞는 post 객체를 반환
    def get_object(self, post_pk):
        return get_object_or_404(Post, pk=post_pk)
    

    def get(self, request, post_pk):
        """
        사용자의 GET 요청을 받아 post_pk에 해당하는 post를 조회하는 함수
        """
        post = self.get_object(post_pk)
        serializer = PostDetailSerializer(post, context={"request":request})
        return Response(serializer.data)


class LikeAPIView(APIView):
    """
    Post   /api/v1/post/"<int:post_pk>/like/
    -> 게시글 좋아요/좋아요 취소
    """
    
    permission_classes = [IsAuthenticated]

    def post(self, request, post_pk):
        """
        사용자의 POST 요청을 받아 좋아요/좋아요 취소를 수행하는 함수
        """
        # 게시글 조회
        post = get_object_or_404(Post, pk=post_pk)
        # 현재 요청을 보낸 유저가 이미 좋아요 상태인지 아닌지 확인
        already_liked = post.like_users.filter(pk=request.user.pk).exists()

        if already_liked:
            post.like_users.remove(request.user)
            liked = False
        else:
            post.like_users.add(request.user)
            liked = True

        serializer = PostDetailSerializer(post, context={"request":request})
        return Response({
            "post_id": post_pk,
            "liked": liked,
            "post": serializer.data,
        })
    

class CommentAPIView(APIView):
    """
    POST    /api/v1/post/<int:post_pk>/comment/
    -> 댓글 생성
    DELETE    /api/v1/post/<int:comment_pk>/comment/
    -> 댓글 삭제
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, post_pk):
        post = get_object_or_404(Post, pk=post_pk)

        serializer = CommentSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            comment = serializer.save(user=request.user, post=post)
            return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)
        
    def delete(self, request, comment_pk):
        comment = get_object_or_404(Comment, pk=comment_pk)

        if request.user != comment.user:
            return Response({"message": "권한이 없습니다"}, status=status.HTTP_403_FORBIDDEN)
        
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
class MyPostsAPIView(APIView):
    """
    현재 로그인되어있는 사용자가 작성한 글만 조회
    GET /api/v1/post/my/
    -> 현재 로그인되어있는 사용자가 작성한 게시글 조회
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        posts = Post.objects.annotate(
            comment_count=Count("writed_comments", distinct=True),
            like_count=Count("like_users", distinct=True),
        ).filter(user=request.user).order_by("-created_at")
        serializer = PostListSerailizer(posts, many=True, context={"request": request})
        return Response(serializer.data)
    
    
class MyLikePostAPIView(APIView):
    """
    현재 로그인되어있는 사용자가 "좋아요"한 게시글만 조회
    GET /api/v1/post/my/like/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        posts = get_list_or_404(Post, like_users = request.user)
        serializer = PostListSerailizer(posts, many=True, context={"request": request})
        return Response(serializer.data)